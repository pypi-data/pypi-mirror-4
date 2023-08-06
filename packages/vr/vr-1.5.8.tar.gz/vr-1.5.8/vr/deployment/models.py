import sys
import xmlrpclib
import hashlib
import json
import datetime
from copy import copy

from django.db import models
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.utils import timezone
import yaml
import redis

from vr.deployment.fields import YAMLDictField
from vr.deployment import events
from raptor import repo, build, models as raptor_models
from raptor.utils import parse_redis_url


# If we're actually running (not just collecting static files), and there's not
# already an 'events_redis' in this module, then make a such a connection and
# save it here.  redis-py implements an internal connection pool, so this
# should be thread safe and gevent safe.
if 'collectstatic' not in sys.argv and 'events_redis' not in globals():
    events_redis = redis.StrictRedis(**parse_redis_url(settings.EVENTS_PUBSUB_URL))

LOG_ENTRY_TYPES = (
    ('build', 'Build'),
    ('release', 'Release'),
    ('deployment', 'Deployment'),
)


def no_spaces(value):
    if ' ' in value:
        raise ValidationError(u'spaces not allowed')


def no_dashes(value):
    if '-' in value:
        raise ValidationError(u'dashes not allowed')


class DeploymentLogEntry(models.Model):
    type = models.CharField(max_length=50, choices=LOG_ENTRY_TYPES)
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    message = models.TextField()

    def __unicode__(self):
        return self.message

    class Meta:
        ordering = ['-time']


class ConfigIngredient(models.Model):
    label = models.CharField(max_length=50, unique=True)
    value = YAMLDictField(help_text=("Must be valid YAML dict."))

    def __unicode__(self):
        return self.label

    class Meta:
        ordering = ['label', ]


repo_choices = (
    ('git', 'git'),
    ('hg', 'hg'),
)


class BuildPack(models.Model):
    repo_url = models.CharField(max_length=200, unique=True)
    repo_type = models.CharField(max_length=10, choices=repo_choices,
                                 default='git')
    desc = models.TextField(blank=True, null=True)
    order = models.IntegerField()

    def __unicode__(self):
        return self.repo_url

    class Meta:
        ordering = ['order']

    @classmethod
    def get_order(cls):
        """
        Return the order in which the build packs should be checked as a list
        of folder name strings.
        """
        return [repo.basename(bp.repo_url) for bp in cls.objects.all()]

    def get_repo(self):
        return build.add_buildpack(self.repo_url, vcs_type=self.repo_type)


class App(models.Model):
    namehelp = ("Used in release name.  Good app names are short and use "
                "no spaces or dashes (underscores are OK).")
    name = models.CharField(max_length=50, help_text=namehelp,
        validators=[no_spaces, no_dashes], unique=True)
    repo_url = models.CharField(max_length=200)
    repo_type = models.CharField(max_length=10, choices=repo_choices)

    buildpack = models.ForeignKey(BuildPack, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Tag(models.Model):
    """ Storage for latest tags for a given app. This model is filled up by a
    task that clones/pulls all the apps and runs an hg tags to update this
    model.
    """
    app = models.ForeignKey(App)
    name = models.CharField(max_length=20)


class ConfigRecipe(models.Model):
    app = models.ForeignKey(App)
    namehelp = ("Used in release name.  Good recipe names are short and use "
                "no spaces or dashes (underscores are OK)")
    name = models.CharField(verbose_name="ConfigRecipe Name", max_length=20,
                            help_text=namehelp,
                            validators=[no_spaces, no_dashes])
    ingredients = models.ManyToManyField(ConfigIngredient,
                                         through='RecipeIngredient')

    env_vars = YAMLDictField(help_text=("YAML dict of env vars to be set at "
                                        "runtime"), null=True, blank=True)

    def __unicode__(self):
        return '%s-%s' % (self.app.name, self.name)

    def assemble(self, custom_ingredients=None):
        """ Use current RecipeIngredients objects to assemble a dict of
        options, or use a custom list of ConfigIngredient ids that might
        be generated from a preview view. """
        out = {}
        if custom_ingredients is None:
            ingredients = [i.ingredient for i in
                           RecipeIngredient.objects.filter(recipe=self)]
        else:
            ingredients = ConfigIngredient.objects.filter(
                id__in=custom_ingredients)

        for i in ingredients:
            out.update(i.value)
        return out

    def to_yaml(self, custom_dict=None):
        """ Use assemble method to build a yaml file, or use a custom_dict
        that might be constructed from a preview view """
        if custom_dict is None:
            return yaml.safe_dump(self.assemble(), default_flow_style=False)
        else:
            return yaml.safe_dump(custom_dict, default_flow_style=False)

    def get_current_release(self, tag):
        """
        Retrieve or create a Release that has current config and a build with
        the specified tag.
        """

        build = Build.get_current(self.app, tag)
        if build is None:
            build = Build(app=self.app, tag=tag)
            build.save()
        # If there's a release linked to the given recipe, that uses the given
        # build, and has current config, then return that.  Else make a new
        # release that satisfies those constraints, and return that.
        releases = Release.objects.filter(recipe=self,
                                          build__tag=tag).order_by('-id')

        # only re-use a release if it has current env vars too
        env_vars = dict(build.env_vars or {})
        env_vars.update(self.env_vars or {})

        if (releases and releases[0].parsed_config() == self.assemble()
            and dict(releases[0].env_vars or {}) == env_vars):
            return releases[0]
        release = Release(recipe=self, build=build, config=self.to_yaml())
        release.save()
        return release

    class Meta:
        unique_together = ('app', 'name')
        ordering = ('app__name', 'name')


class RecipeIngredient(models.Model):
    """
    Through-table for the many:many relationship between configingredients and
    configrecipes.  Managed manually so we can have some extra fields.
    """
    ingredient = models.ForeignKey(ConfigIngredient)
    recipe = models.ForeignKey(ConfigRecipe)

    ohelp = "Order for merging when creating release. Higher number takes "\
            "precedence."
    order = models.IntegerField(blank=True, null=True,  help_text=ohelp)

    class Meta:
        unique_together = ('ingredient', 'recipe')
        ordering = ['order']


class Build(models.Model):
    app = models.ForeignKey(App)
    tag = models.CharField(max_length=50)
    file = models.FileField(upload_to='builds', null=True, blank=True)

    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)

    build_status_choices = (
        ('pending', 'Pending'),
        ('started', 'Started'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
    )

    status = models.CharField(max_length=20, choices=build_status_choices,
                              default='pending')

    env_vars = YAMLDictField(help_text=("YAML dict of env vars from "
                                        "buildpack"), null=True, blank=True)

    buildpack_url = models.CharField(max_length=200, null=True, blank=True)
    buildpack_version = models.CharField(max_length=50, null=True, blank=True)

    def is_usable(self):
        return self.file.name and self.status == 'success'

    def in_progress(self):
        if self.status not in ('pending', 'started'):
            return False

        if self.end_time or not self.start_time:
            # If build ended, or never started, then it's not in progress
            return False

        # settings.BUILD_WAIT_AGE is the max number of seconds between starting
        # a build and considering that it must have failed because it's been so
        # long since hearing from it.  Defaults to one hour.
        max_age = getattr(settings, 'BUILD_WAIT_AGE', 3600)
        min_start = timezone.now() - datetime.timedelta(0, max_age, 0)
        if self.start_time < min_start:
            return False

        return True

    @classmethod
    def get_current(cls, app, tag):
        """
        Given an app and a tag, look for a build that matches both, and was
        successfully built (or is currently building).  If not found, return
        None.
        """
        # First check if there's a build for our app and the given tag
        builds = cls.objects.filter(
                app=app, tag=tag
            ).exclude(status='expired'
            ).exclude(status='failed'
            ).order_by('-id')

        if not builds:
            return None

        # we found a qualifying build (either successful or in progress of
        # being built right this moment).
        return builds[0]

        # TODO: Also check that the build was made with the current version of
        # the buildpack.  We used to have a check like this that used the
        # buildpack revision hash, but it was removed when trying to figure out
        # why we were seeing unnecessary builds.


    def __unicode__(self):
        # Return the app name and version
        return u'-'.join([self.app.name, self.tag])

    class Meta:
        ordering = ['-id']


class Release(models.Model):
    recipe = models.ForeignKey(ConfigRecipe)
    build = models.ForeignKey(Build)
    config = models.TextField(blank=True, null=True, help_text="YAML text to "
                             "be written to settings.yaml at deploy time.")

    # Hash will be computed on saving the model.
    hash = models.CharField(max_length=32, blank=True, null=True)

    env_vars = YAMLDictField(help_text=("YAML dict of env vars to be set "
                                           "at runtime"), null=True, blank=True)

    def __unicode__(self):
        return u'-'.join([self.build.app.name, self.build.tag,
                          self.recipe.name, self.hash or 'PENDING'])

    def compute_hash(self):
        # Compute self.hash from the config contents and build file.
        buildcontents = default_storage.open(self.build.file.name, 'rb').read()

        md5chars = hashlib.md5(buildcontents + bytes(self.config) +
                               bytes(self.env_vars)).hexdigest()
        return md5chars[:8]

    def save(self, *args, **kwargs):
        # If there's a build, then copy the env vars and compute the hash
        if self.build.file.name:
            # copy env vars from build
            self.env_vars = dict(self.build.env_vars or {})

            # update with env vars from recipe
            if self.env_vars is None:
                self.env_vars = self.recipe.env_vars or {}
            else:
                self.env_vars.update(self.recipe.env_vars or {})

            self.hash = self.compute_hash()
        super(Release, self).save(*args, **kwargs)

    def parsed_config(self):
        return yaml.safe_load(self.config or '')

    class Meta:
        ordering = ['-id']


class Host(models.Model):
    name = models.CharField(max_length=200, unique=True)

    # It might be hard to delete host records if there
    active = models.BooleanField(default=True)
    squad = models.ForeignKey('Squad', null=True, blank=True,
                              related_name='hosts')

    def __unicode__(self):
        return self.name

    def get_used_ports(self):
        return set(p.port for p in self.get_procs())

    def get_next_port(self):

        all_ports = xrange(settings.PORT_RANGE_START, settings.PORT_RANGE_END)
        used_ports = self.get_used_ports()

        # Return the first port in our configured range that's not already in
        # use.
        def free(port):
            if PortLock.objects.filter(host=self, port=port):
                return False

            return port not in used_ports

        return next(x for x in all_ports if free(x))

    def get_proc(self, name, check_cache=False):
        """
        Given a name of a proc, get its information from supervisord and return
        a Proc instance.
        """
        return self.raw_host.get_proc(name, check_cache)

    def get_procs(self, check_cache=False):
        return self.raw_host.get_procs(check_cache)

    def shortname(self):
        return self.raw_host.shortname()

    class Meta:
        ordering = ('name',)

    def __init__(self, *args, **kwargs):
        super(Host, self).__init__(*args, **kwargs)
        user = getattr(settings, 'SUPERVISOR_USERNAME', None)
        pwd = getattr(settings, 'SUPERVISOR_PASSWORD', None)
        self.raw_host = raptor_models.Host(self.name, settings.SUPERVISOR_PORT,
                                          redis_or_url=events_redis,
                                           supervisor_username=user,
                                           supervisor_password=pwd)


class Squad(models.Model):
    """
    A Squad is a group of identical hosts.  When deploying a swarm, its procs
    will be load balanced across the specified squad.  A host may only be in
    one squad.
    """
    name = models.CharField(max_length=50, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Swarm(models.Model):
    """
    This is the payoff.  Save a swarm record and then you can tell Velociraptor
    to 'make it so'.
    """
    recipe = models.ForeignKey(ConfigRecipe)
    squad = models.ForeignKey(Squad)
    release = models.ForeignKey(Release)
    proc_name = models.CharField(max_length=50)
    size = models.IntegerField(help_text='The number of procs in the swarm',
                               default=1)

    pool_help = "The name of the pool in the load balancer (omit prefix)"
    pool = models.CharField(max_length=50, help_text=pool_help, blank=True,
                            null=True)

    # Select which balancer should be used for this squad, from
    # settings.BALANCERS
    _balancer_choices = [(k, k) for k in settings.BALANCERS]
    balancer = models.CharField(max_length=50, choices=_balancer_choices,
                                blank=True, null=True)

    # If set to true, then the workers will periodically check this swarm's
    # status and make sure it has enough workers, running the right version,
    # with the right config.  Someday.
    active = models.BooleanField(default=True)

    def save(self):
        if self.pool and not self.balancer:
            raise ValidationError('Swarms that specify a pool must specify a '
                                  'balancer')
        super(Swarm, self).save()

    class Meta:
        unique_together = ('recipe', 'squad', 'proc_name')
        ordering = ['recipe__app__name', 'recipe__name', 'proc_name']

    def __unicode__(self):
        return u'%(rname)s-%(proc)s' % {
            'rname': self.release.__unicode__(),
            'proc': self.proc_name,
        }

    def shortname(self):
        return u'%(app)s-%(version)s-%(proc)s' % {
            'app': self.recipe.app.name,
            'version': self.release.build.tag,
            'proc': self.proc_name
        }

    def get_procs(self, check_cache=False):
        """
        Return all running procs on the squad that share this swarm's proc name
        and recipe.
        """
        if not self.release:
            return []

        procs = []
        for host in self.squad.hosts.all():
            procs += host.get_procs(check_cache=check_cache)

        def is_mine(proc):
            return p.recipe_name == self.recipe.name and \
                   p.proc_name == self.proc_name and \
                   p.app_name == self.recipe.app.name

        return [p for p in procs if is_mine(p)]

    def get_prioritized_hosts(self):
        """
        Return list of hosts in the squad sorted first by number of procs from
        this swarm, then by total number of procs.
        """
        # Make list of all hosts in the squad.  Then we'll sort it.
        squad_hosts = list(self.squad.hosts.all())

        for h in squad_hosts:
            # Set a couple temp attributes on each host in the squad, for
            # sorting by.
            h.all_procs = h.get_procs()
            h.swarm_procs = [p for p in h.all_procs if p.hash ==
                             self.release.hash and p.proc_name == self.proc_name]

            # On each host, set a tuple in form (x, y), where:
                # x = number of procs running on this host that belong to the
                # swarm
                # y = total number of procs running on this host

            h.sortkey = (len(h.swarm_procs), len(h.all_procs))

        squad_hosts.sort(key=lambda h: h.sortkey)
        return squad_hosts

    def get_next_host(self):
        return self.get_prioritized_hosts()[0]


class PortLock(models.Model):
    """
    The presence of one of these records indicates that a port is reserved for
    a particular proc that's probably still in the process of being deployed.
    Port locks should be deleted when their deploys are finished.
    """
    host = models.ForeignKey(Host)
    port = models.IntegerField()
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('host', 'port')

    def __unicode__(self):
        return '%s:%s' % (self.host, self.port)


class TestRun(models.Model):
    """
    Once every 15 minutes or so (configurable), run uptests on every proc on
    every host.  One of these records should be created for each such run.
    """
    start = models.DateTimeField()
    end = models.DateTimeField(null=True)

    def __unicode__(self):
        return self.start.isoformat()

    # TODO: convert this to a normal method (after first finding all callers)
    @property
    def results(self):
        """
        Return a serializable compilation/summary of the test run results.
        """
        end = self.end.isoformat() if self.end else None
        seconds = (self.end - self.start).total_seconds() if end else None
        return {
            'start': self.start.isoformat(),
            'end': end,
            'seconds': seconds,
            'pass_count': self.tests.filter(passed=True).count(),
            'fail_count': self.tests.filter(passed=False).count(),
            'notests_count': self.tests.filter(testcount=0).count(),
            'results': {'%s-%s' % (t.hostname, t.procname): t.as_dict() for t in
                        self.tests.all()}
        }

    def get_failures(self):
        """
        Return a serializable compilation/summary of the test run failures.
        """
        end = self.end.isoformat() if self.end else None
        seconds = (self.end - self.start).total_seconds() if end else None
        return {
            'start': self.start.isoformat(),
            'end': end,
            'seconds': seconds,
            'pass_count': self.tests.filter(passed=True).count(),
            'fail_count': self.tests.filter(passed=False).count(),
            'notests_count': self.tests.filter(testcount=0).count(),
            'results': {'%s-%s' % (t.hostname, t.procname): t.as_dict() for t in
                        self.tests.filter(passed=False)}
        }

    def has_failures(self):
        return self.tests.filter(passed=False).count() > 0

    class Meta:
        ordering = ['-start']


class TestResult(models.Model):
    """
    Results from testing a single proc on a single host.
    """
    run = models.ForeignKey(TestRun, related_name='tests')
    time = models.DateTimeField()
    hostname = models.CharField(max_length=200)
    procname = models.CharField(max_length=200)
    passed = models.BooleanField(default=False)
    testcount = models.IntegerField(default=0)
    # YAML dump of test results
    results = models.TextField()

    def __unicode__(self):
        if self.testcount:
            desc = 'pass' if self.passed else 'fail'
        else:
            desc = 'no tests'
        return '%s: %s' % (self.procname, desc)

    def as_dict(self):
        return yaml.safe_load(self.results)

    def get_fails(self):
        """
        Return a list of dictionaries like the one returned from as_dict, but
        containing just the failed tests.
        """
        parsed = yaml.safe_load(self.results)
        return [t for t in parsed if t['Passed'] == False]

    def format_fail(self, result):
        """
        Given a result dict like that emitted from the uptester, return a
        human-friendly string showing the failure.
        """
        name = self.procname + '@' + self.hostname
        return (name + ": {Name} failed:\n{Output}".format(**result))

    def get_formatted_fails(self):
        return '\n'.join(self.format_fail(f) for f in self.get_fails())
