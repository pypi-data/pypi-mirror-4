"""
    # Workaround / say if using cached Charm present
    # Write out resolved deployment file with includes & overrides
    # Ensure bootstrap
"""

from base64 import b64encode
from bzrlib.workingtree import WorkingTree
from copy import deepcopy
from contextlib import contextmanager

import errno
import logging
from logging.config import dictConfig as logConfig
import optparse
import os

from os.path import abspath, dirname, isabs
from os.path import join as path_join
from os.path import exists as path_exists

import pprint
import sys
import subprocess
import tempfile
import time

try:
    from yaml import CSafeLoader, CSafeDumper
except ImportError:
    optimized = False
else:
    optimized = True

from yaml import dump as _dump
from yaml import load as _load

from jujuclient import Environment as EnvironmentClient, UnitErrors


class ErrorExit(Exception):

    def __init__(self, error=None):
        self.error = error

# Utility functions


def yaml_dump(value):
    if optimized:
        return _dump(value, Dumper=CSafeDumper)
    return _dump(value)


def yaml_load(value):
    if optimized:
        return _load(value, Loader=CSafeLoader)
    return _load(value)

DEFAULT_LOGGING = """
version: 1
formatters:
    standard:
        format: '%(asctime)s %(message)s'
    detailed:
        format: '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
handlers:
    console:
        class: logging.StreamHandler
        formatter: standard
        level: DEBUG
        stream: ext://sys.stderr
loggers:
    deployer:
        level: DEBUG
        propogate: true
    deploy.cli:
        level: DEBUG
        propogate: true
    deploy.charm:
        level: DEBUG
        propogate: true
    deploy.env:
        level: DEBUG
        propogate: true
    deploy.deploy:
        level: DEBUG
        propogate: true
    deploy.importer:
        level: DEBUG
        propogate: true
    "":
        level: INFO
        handlers:
            - console
"""


def setup_logging(verbose=False, debug=False):
    config = yaml_load(DEFAULT_LOGGING)
    log_options = {}
    if debug and not verbose:
        verbose = True
    if verbose:
        log_options.update({"loggers": {"": {"level": "DEBUG"}}})
    if debug:
        log_options.update({"handlers": {"console": {"formatter": "detailed"}}})
    config = dict_merge(config, log_options)
    logConfig(config)


@contextmanager
def temp_file():
    t = tempfile.NamedTemporaryFile()
    try:
        yield t
    finally:
        t.close()


def _check_call(params, cwd, log, *args, **kw):
    try:
        cwd = cwd or abspath(".")
        output = subprocess.check_output(
            params, cwd=cwd, stderr=subprocess.STDOUT, env=os.environ)
    except subprocess.CalledProcessError, e:
        #print "subprocess error"
        #print " ".join(params), "\ncwd: %s\n" % cwd, "\n ".join(
        #    ["%s=%s" % (k, os.environ[k]) for k in os.environ if k.startswith("JUJU")])
        #print e.output
        log.error(*args, **kw)
        log.error("Command (%s) Output:\n\n %s", " ".join(params), e.output)
        raise ErrorExit(e)
    return output


# Utils from deployer 1
def relations_combine(onto, source):
    target = deepcopy(onto)
    for (key, value) in source.items():
        if key in target:
            if isinstance(target[key], dict) and isinstance(value, dict):
                target[key] = relations_combine(target[key], value)
            elif isinstance(target[key], list) and isinstance(value, list):
                target[key] = list(set(target[key] + value))
        else:
            target[key] = value
    return target


def dict_merge(onto, source):
    target = deepcopy(onto)
    for (key, value) in source.items():
        if (key in target and isinstance(target[key], dict) and
                isinstance(value, dict)):
            if key == 'relations':
                target[key] = relations_combine(target[key], value)
            else:
                target[key] = dict_merge(target[key], value)
        else:
            target[key] = value
    return target


def resolve_include(fname, include_dirs):
    if isabs(fname):
        return fname
    for path in include_dirs:
        full_path = path_join(path, fname)
        if path_exists(full_path):
            return full_path

    return None


def setup_parser():
    parser = optparse.OptionParser()
    parser.add_option('-c', '--config',
                      help=('File containing deployment(s) json config. This '
                            'option can be repeated, with later files overriding '
                            'values in earlier ones.'),
                      dest='configs', action='append')
    parser.add_option('-d', '--debug', help='Enable debugging to stdout',
                      dest="debug",
                      action="store_true", default=False)
    parser.add_option('-L', '--local-mods',
                      help='Allow deployment of locally-modified charms',
                      dest="no_local_mods", default=True, action='store_false')
    parser.add_option('-u', '--update-charms',
                      help='Update existing charm branches',
                      dest="update_charms", default=False, action="store_true")
    parser.add_option('-l', '--ls', help='List available deployments',
                      dest="list_deploys", action="store_true", default=False)
    parser.add_option('-D', '--destroy-services',
                      help='Destroy all services (do not terminate machines)',
                      dest="destroy_services", action="store_true",
                      default=False)
    parser.add_option('-T', '--terminate-machines',
                      help=('Terminate all machines but the bootstrap node.  '
                            'Destroy any services that exist on each'),
                      dest="terminate_machines", action="store_true",
                      default=False)
    parser.add_option('-t', '--timeout',
                      help='Timeout (sec) for entire deployment (45min default)',
                      dest='timeout', action='store', type='int', default=2700)
    parser.add_option("-f", '--find-service', action="store", type="string",
                      help='Find hostname from first unit of a specific service.',
                      dest="find_service")
#    parser.add_option("-m", '--max-concurrent', action="store", type="int",
#                      help=("Maximum number of concurrent deployments to send "
#                            " to provider. Default: no limit"),
#                      dest="max_concur_deploy", default=0)
    parser.add_option('-s', '--deploy-delay', action='store', type='float',
                      help=("Time in seconds to sleep between 'deploy' commands, "
                            "to allow machine provider to process requests. This "
                            "delay is also enforced between calls to"
                            "terminate_machine"),
                      dest="deploy_delay", default=0)
    parser.add_option('-e', '--environment', action='store', dest='juju_env',
                      help='Deploy to a specific Juju environment.',
                      default=os.getenv('JUJU_ENV'))
    parser.add_option('-o', '--override', action='append', type='string',
                      help=('Override *all* config options of the same name '
                            'across all services.  Input as key=value.'),
                      dest='overrides', default=None)
    parser.add_option('-W', '--watch', help='Watch environment changes on console',
                      dest="watch",
                      action="store_true", default=False)

# bzr up -r doesn't seem to support revisionspec date forms??
#    parser.add_option('-r', '--revdate', help='Deploy charm revisions as of date',
#                      dest="revspec",
#                      action="store", default=False)
    parser.add_option('-w', '--relation-wait', action='store', dest='rel_wait',
                      default=60, type=int,
                      help=('Number of seconds to wait before checking for '
                            'relation errors after all relations have been added '
                            'and subordinates started. (default: 60)'))

    return parser


class ConfigStack(object):

    log = logging.getLogger("deployer.config")

    def __init__(self, config_files):
        self.config_files = config_files
        self.data = {}
        self.include_dirs = []
        self.load()

    def keys(self):
        return sorted(self.data)

    def get(self, key):
        if not key in self.data:
            self.log.warning("Deployment %r not found. Available %s",
                             key, ", ".join(self.keys()))
            raise ErrorExit()
        deploy_data = self.data[key]
        deploy_data = self._resolve_inherited(deploy_data)
        return Deployment(key, deploy_data, self.include_dirs)

    def load(self):
        data = {}
        include_dirs = []
        for fp in self.config_files:
            if not path_exists(fp):
                self.log.warning("Config file not found %s", fp)
                raise ErrorExit()
            include_dirs.append(dirname(abspath(fp)))
            with open(fp) as fh:
                try:
                    d = yaml_load(fh.read())
                    data = dict_merge(data, d)
                except Exception, e:
                    self.log.warning(
                        "Couldn't load config file @ %r, error: %s:%s",
                        fp, type(e), e)
                    raise
        self.data = data
        self.include_dirs = include_dirs

    def _inherits(self, d):
        parents = d.get('inherits', ())
        if isinstance(parents, basestring):
            parents = [parents]
        return parents

    def _resolve_inherited(self, deploy_data):
        if not 'inherits' in deploy_data:
            return deploy_data
        inherits = parents = self._inherits(deploy_data)
        for parent_name in parents:
            parent = self.get(parent_name)
            inherits.extend(self._inherits(parent.data))
            deploy_data = dict_merge(deploy_data, parent.data)
        deploy_data['inherits'] = inherits
        return deploy_data


class Service(object):

    def __init__(self, name, svc_data):
        self.svc_data = svc_data
        self.name = name

    @property
    def config(self):
        return self.svc_data.get('options', None)

    @property
    def constraints(self):
        return self.svc_data.get('constraints', None)

    @property
    def num_units(self):
        return int(self.svc_data.get('num_units', 1))


class Vcs(object):

    err_update = "Could not update branch %(path)s from %(branch_url)s\n\n %(output)s"
    err_branch = "Could not branch %(branch_url)s to %(path)s\n\n %(output)s"
    err_is_mod = "Couldn't determine if %(path)s was modified\n\n %(output)s"
    err_pull = "Could not pull branch @ %(branch_url)s to %(path)s\n\n %(output)s"
    err_cur_rev = "Could not determine current revision %(path)s\n\n %(output)s"

    def __init__(self, path, origin, log):
        self.path = path
        self.log = log
        self.origin = origin

    def _call(self, args, error_msg, cwd=None, stderr=()):
        #print " ".join(args), "in", cwd or self.path
        try:
            stderr = stderr is None and stderr or subprocess.STDOUT
            output = subprocess.check_output(
                args, cwd=cwd or self.path, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            print "vcs err", " ".join(args), "[dir: %s]" % cwd
            self.log.error(error_msg % self.get_err_msg_ctx(e))
            raise ErrorExit()
        return output.strip()

    def get_err_msg_ctx(self, e):
        return {
            'path': self.path,
            'branch_url': self.origin,
            'exit_code': e.returncode,
            'output': e.output,
            'vcs': self.__class__.__name__.lower()}

    def get_cur_rev(self):
        raise NotImplementedError()

    def update(self, rev=None):
        raise NotImplementedError()

    def branch(self):
        raise NotImplementedError()

    def pull(self):
        raise NotImplementedError()

    def is_modified(self):
        raise NotImplementedError()

    #m upstream missing?


class Bzr(Vcs):

    def get_cur_rev(self):
        params = ["bzr", "revno", "--tree"]
        return self._call(params, self.err_cur_rev)

    def update(self, rev=None):
        params = ["bzr", "up"]
        if rev:
            params.extend(["-r", str(rev)])
        self._call(params, self.err_update)

    def pull(self):
        params = ["bzr", "pull", "--remember", self.origin]
        self._call(params, self.err_pull)

    def branch(self):
        params = ["bzr", "branch", self.origin]
        self._call(params, self.err_branch, os.path.dirname(self.path))

    def is_modified(self):
        # To replace with bzr cli, we need to be able to detect changes
        # to a wc @ a rev or @ trunk.
        tree = WorkingTree.open(self.path)
        return tree.has_changes()


class Charm(object):

    log = logging.getLogger('deployer.charm')

    def __init__(self, name, path, branch, rev, build, charm_url=""):
        self.name = name
        self.path = path
        self.branch = branch
        self.rev = rev
        self._charm_url = charm_url
        self._build = build
        self.vcs = self.get_vcs()

    def get_vcs(self):
        return Bzr(self.path, self.branch, self.log)

    @classmethod
    def from_service(cls, name, series_path, d):
        branch, rev = None, None
        charm_branch = d.get('branch')
        if charm_branch is not None:
            branch, sep, rev = charm_branch.partition('@')
        name = d.get('charm', name)
        charm_path = path_join(series_path, name)
        build = d.get('build', '')
        store_url = d.get('charm_url', None)

        if store_url and branch:
            cls.log.error(
                "Service: %s has both charm url: %s and branch: %s specified",
                name, store_url, branch)
        return cls(name, charm_path, branch, rev, build, store_url)

    def exists(self):
        return path_exists(self.path)

    def is_subordinate(self):
        return self.metadata.get('subordinate', False)

    @property
    def charm_url(self):
        if self._charm_url:
            return self._charm_url
        return "local:%s" % self.name

    def build(self):
        if not self._build:
            return
        self.log.debug("Building charm %s with %s", self.path, self._build)
        _check_call([self._build], self.path, self.log,
                    "Charm build failed %s @ %s", self._build, self.path)

    def fetch(self):
        if not self.branch:
            return
        self.log.debug(" Branching charm %s @ %s", self.branch, self.path)
        self.vcs.branch()
        self.build()

    def update(self, build=False):
        if not self.branch:
            return
        assert self.exists()
        self.log.debug(" Updating charm %s from %s", self.path, self.branch)
        self.vcs.update(self.rev)
        if build:
            self.build()

    def is_modified(self):
        if not self.branch:
            return False
        return self.vcs.is_modified()

    @property
    def config(self):
        config_path = path_join(self.path, "config.yaml")
        if not path_exists(config_path):
            return {}

        with open(config_path) as fh:
            return yaml_load(fh.read()).get('options', {})

    @property
    def metadata(self):
        md_path = path_join(self.path, "metadata.yaml")
        if not path_exists(md_path):
            if not path_exists(self.path):
                raise RuntimeError("No charm metadata @ %s", md_path)
        with open(md_path) as fh:
            return yaml_load(fh.read())


class Deployment(object):

    log = logging.getLogger("deployer.deploy")

    def __init__(self, name, data, include_dirs, repo_path=""):
        self.name = name
        self.data = data
        self.include_dirs = include_dirs
        self.repo_path = repo_path

    @property
    def series(self):
        # Series could use a little help, charm series should be inferred
        # directly from a store url, or
        return self.data.get('series', 'precise')

    @property
    def series_path(self):
        return path_join(self.repo_path, self.series)

    def pretty_print(self):
        pprint.pprint(self.data)

    def get_service(self, name):
        if not name in self.data['services']:
            return
        return Service(name, self.data['services'][name])

    def get_services(self):
        for name, svc_data in self.data['services'].items():
            yield Service(name, svc_data)

    def get_relations(self):
        if 'relations' not in self.data:
            return

        # Support an ordered list of [endpoints]
        if isinstance(self.data['relations'], list):
            for end_a, end_b in self.data['relations']:
                yield (end_a, end_b)
            return

        # Legacy format (dictionary of dictionaries with weights)
        rels = {}
        for k, v in self.data['relations'].items():
            expanded = []
            for c in v['consumes']:
                expanded.append((k, c))
            rels[v.get('weight', 0)] = expanded
        for k in sorted(rels):
            for r in rels[k]:
                yield r

    def get_charms(self):
        for k, v in self.data['services'].items():
            yield Charm.from_service(k, self.series_path, v)

    def get_charm_for(self, svc_name):
        svc_data = self.data['services'][svc_name]
        return Charm.from_service(svc_name, self.series_path, svc_data)

    def fetch_charms(self, update=False, no_local_mods=False):
        if not os.path.exists(self.series_path):
            os.mkdir(self.series_path)
        for charm in self.get_charms():
            if charm.exists():
                if no_local_mods:
                    if charm.is_modified():
                        self.log.warning(
                            "Charm %r has local modifications",
                            charm.path)
                        raise ErrorExit()
                if update:
                    charm.update(build=True)
            else:
                charm.fetch()

    def load_overrides(self, cli_overrides=()):
        """Load overrides."""
        overrides = {}
        overrides.update(self.data.get('overrides', {}))

        for o in cli_overrides:
            key, value = o.split('=', 1)
            overrides[key] = value

        for k, v in overrides.iteritems():
            found = False
            for svc_name, svc_data in self.data['services'].items():
                charm = self.get_charm_for(svc_name)
                if k in charm.config:
                    svc_data['options'][k] = v
                    found = True
            if not found:
                self.log.warning(
                    "Override %s does not match any charms %s", k)

    def resolve_config(self):
        """Load any lazy config values (includes), and verify config options.
        """
        # XXX TODO, rename resolve, validate relations against defined services.
        for svc_name, svc_data in self.data.get('services', {}).items():
            if not 'options' in svc_data:
                continue
            charm = self.get_charm_for(svc_name)
            config = charm.config
            options = {}

            for k, v in svc_data['options'].items():
                if not k in config:
                    self.log.warning(
                        "Invalid charm %s config %s=%s", charm.name, k, v)
                    continue
                for include_type in ["file", "base64"]:
                    if not v.startswith("include-%s://" % include_type):
                        continue
                    include, fname = v.split("://", 1)
                    ip = resolve_include(fname, self.include_dirs)
                    if ip is None:
                        self.log.warning(
                            "Invalid config %s.%s include not found %s",
                            svc_name, k, v)
                        continue
                    with open(ip) as fh:
                        v = fh.read()
                        if include_type == "base64":
                            v = b64encode(v)
                        svc_data['options'][k] = v
                options[k] = v
            svc_data['options'] = options


class Environment(object):

    log = logging.getLogger("deployer.env")

    def __init__(self, name, endpoint=None):
        self.name = name
        self.api_endpoint = endpoint
        self.client = None

    def close(self):
        if self.client:
            self.client.close()

    def connect(self):
        if not self.api_endpoint:
            # should really have a cheaper/faster way of getting the endpoint
            # ala juju status 0 for a get_endpoint method.
            self.get_cli_status()
        while True:
            try:
                self.client = EnvironmentClient(self.api_endpoint)
            except Exception, e:
                if e.errno != errno.ETIMEDOUT:
                    raise
                continue
            else:
                break
        self.client.login(self._get_token())
        self.log.debug("Connected to environment")

    def _get_token(self):
        with open(self.env_config_path) as fh:
            config = yaml_load(fh.read())
            if self.name:
                token = config['environments'][self.name]['admin-secret']
            else:
                env_name = config.get('default')
                if env_name is None:
                    if len(config['environments'].keys()) == 1:
                        env_name = config['environments'].keys().pop()
                    else:
                        self.log.error("Ambigious operation environment")
                        raise ErrorExit()
                token = config['environments'][env_name]['admin-secret']
            return token

    @property
    def env_config_path(self):
        jhome = os.environ.get("JUJU_HOME")
        if jhome is None:
            jhome = path_join(os.environ.get('HOME'), '.juju')
        env_config_path = path_join(jhome, 'environments.yaml')
        return env_config_path

    def _named_env(self, params):
        if self.name:
            params.extend(["-e", self.name])
        return params

    def deploy(self, name, charm_url, repo=None, config=None, constraints=None, num_units=1):
        params = self._named_env(["juju", "deploy"])

        with temp_file() as fh:
            if config:
                fh.write(yaml_dump(config))
                params.extend(["--config", fh.name])
            if constraints:
                params.extend(['--constraints', constraints])
                #print 'constraints', constraints
            if num_units != 1:
                params.extend(["--num-units", str(num_units)])
            if charm_url.startswith('local'):
                if repo == "":
                    repo = "."
                params.extend(["--repository=%s" % repo])
            params.extend([charm_url, name])
            _check_call(params, '', self.log, "Error deploying service %r", name)

    def add_units(self, service_name, num_units):
        return self.client.add_units(service_name, num_units)

    def add_relation(self, endpoint_a, endpoint_b):
        return self.client.add_relation(endpoint_a, endpoint_b)

    def terminate_machine(self, mid, wait=False):
        """Terminate a machine.

        The machine can't have any running units, after removing the units or
        destroying the service, use wait_for_units to know when its safe to
        delete the machine (ie units have finished executing stop hooks and are
        removed)
        """
        if int(mid) == 0:
            raise RuntimeError("Can't terminate machine 0")
        params = self._named_env(["juju", "terminate-machine"])
        params.append(mid)
        _check_call(params, "", self.log, "Error terminating machine %r" % mid)

    def get_service_address(self, svc_name):
        status = self.get_cli_status()
        if svc_name not in status['services']:
            self.log.warning("Service %s does not exist", svc_name)
            return None
        units = status['services'][svc_name].get('units', {})
        unit_keys = list(sorted(units.keys()))
        if unit_keys:
            return units[unit_keys[0]].get('public-address', '')
        self.log.warning("Service %s has no units")

    def get_cli_status(self):
        params = self._named_env(["juju", "status"])
        output = _check_call(params, "", self.log, "Error getting status, is it bootstrapped?")
        status = yaml_load(output)
        # Opportunistic, see connect method comment.
        if not self.api_endpoint:
            self.api_endpoint = "wss://%s:17070/" % (
                status["machines"]["0"]["dns-name"])
        return status

    def reset(self, terminate_machines=False, terminate_delay=0, timeout=360, watch=False):
        status = self.status()
        destroyed = False
        for s in status.get('services', {}).keys():
            self.log.debug(" Destroying service %s", s)
            self.client.destroy_service(s)
            destroyed = True
            # Check for any units in error and resolve them.
            for uid, u in status['services'][s].get('units', {}).items():
                if u['agent-state'] == 'error':
                    self.log.debug("  Resolving unit error %s for destroy", uid)
                    self.client.resolved(uid)

        # Wait for units
        if destroyed:
            self.wait_for_units(timeout, "removed", watch=watch)

        # The only value to not terminating is keeping the data on the machines around.
        if not terminate_machines:
            self.log.info(" *juju-core machines are not reusable for units")
            return

        # Terminate machines
        self.log.info("Terminating machines")
        for mid in status['machines'].keys():
            if mid == "0":
                continue
            self.log.debug(" Terminating machine %s", mid)
            self.terminate_machine(mid)
            if terminate_delay:
                time.sleep(terminate_delay)

    def status(self):
        return self.client.get_stat()

    def wait_for_units(self, timeout, goal_state="started", watch=False):
        """Wait for units to reach a given condition.
        """
        callback = watch and self._delta_event_log or None
        self.log.debug("Waiting for units to be %s", goal_state)
        try:
            self.client.wait_for_units(timeout, goal_state, callback=callback)
        except UnitErrors, e:
            error_units = [
                "unit: %s: machine: %s agent-state: %s details: %s" % (
                    u['Name'], u['MachineId'], u['Status'], u['StatusInfo']
                )
                for u in e.errors]
            self.log.error("The following units had errors:\n   %s" % (
                "   \n".join(error_units)))
            raise ErrorExit()

    def _delta_event_log(self, et, ct, d):
        # event type, change type, data
        name = d.get('Name', d.get('Id', 'unknown'))
        state = d.get('Status', d.get('Life', 'unknown'))
        if et == "relation":
            name = self._format_endpoints(d['Endpoints'])
            state = "created"
            if ct == "remove":
                state = "removed"
        self.log.debug(
            " Delta %s: %s %s:%s", et, name, ct, state)

    def _format_endpoints(self, eps):
        if len(eps) == 1:
            ep = eps.pop()
            return "[%s:%s:%s]" % (
                ep['ServiceName'],
                ep['Relation']['Name'],
                ep['Relation']['Role'])

        return "[%s:%s <-> %s:%s]" % (
            eps[0]['ServiceName'],
            eps[0]['Relation']['Name'],
            eps[1]['ServiceName'],
            eps[1]['Relation']['Name'])


class Importer(object):

    log = logging.getLogger("deployer.import")

    def __init__(self, env, deployment, options):
        self.options = options
        self.env = env
        self.deployment = deployment

    def add_units(self):
        # TODO Check if subordinate
        self.log.debug("Adding units...")
        # Add units to existing services that don't match count.
        env_status = self.env.status()
        added = set()
        for svc in self.deployment.get_services():
            delta = svc.num_units - len(env_status['services'][svc.name]['units'])
            if delta > 0:
                self.log.info(
                    "Adding %d more units to %s" % (abs(delta), svc.name))
                for u in self.env.add_units(svc.name, abs(delta)):
                    added.add(u)
            else:
                self.log.debug(
                    " Service %r does not need any more units added." % svc.name)

    def get_charms(self):
        # Get Charms
        self.log.debug("Getting charms...")
        self.deployment.fetch_charms(
            update=self.options.update_charms,
            no_local_mods=self.options.no_local_mods)
        # Load config overrides after we can validate them.
        self.deployment.load_overrides(self.options.overrides or ())
        # Load includes
        self.deployment.resolve_config()

    def deploy_services(self):
        self.log.info("Deploying services...")
        env_status = self.env.status()
        for svc in self.deployment.get_services():
            if svc.name in env_status['services']:
                self.log.debug(
                    " Service %r already deployed. Skipping" % svc.name)
                continue

            charm = self.deployment.get_charm_for(svc.name)
            self.log.info(" Deploying service %s using %s", svc.name, charm.charm_url)
            self.env.deploy(
                svc.name,
                charm.charm_url,
                self.deployment.repo_path,
                svc.config,
                svc.constraints,
                svc.num_units)

            if self.options.deploy_delay:
                time.sleep(self.options.deploy_delay)

    def add_relations(self):
        self.log.info("Adding relations...")

        # Relations
        status = self.env.status()
        created = False

        for end_a, end_b in self.deployment.get_relations():
            if self._rel_exists(status, end_a, end_b):
                continue
            self.log.info(" Adding relation %s <-> %s", end_a, end_b)
            self.env.add_relation(end_a, end_b)
            created = True
            time.sleep(5)  # per the original
        return created

    def _rel_exists(self, status, end_a, end_b):
        # Checks for a named relation on one side that matches the local
        # endpoint and remote service.
        (name_a, name_b, rem_a, rem_b) = (end_a, end_b, None, None)

        if ":" in end_a:
            name_a, rem_a = end_a.split(":", 1)
        if ":" in end_b:
            name_b, rem_b = end_b.split(":", 1)

        rels_svc_a = status['services'][name_a].get('relations', {})

        found = False
        for r, related in rels_svc_a.items():
            if name_b in related:
                if rem_a and not r in rem_a:
                    continue
                found = True
                break
        if found:
            return True
        return False

    def wait_for_units(self):
        timeout = self.options.timeout - (time.time() - self.start_time)
        if timeout < 0:
            self.log.error("Reached deployment timeout.. exiting")
            raise ErrorExit()
        self.env.wait_for_units(int(timeout), watch=self.options.watch)

    def run(self):
        self.start_time = time.time()
        self.env.connect()
        self.get_charms()
        self.deploy_services()
        self.wait_for_units()
        self.add_units()
        rels_created = self.add_relations()
        # Wait for the units to be up before waiting for rel stability.
        self.wait_for_units()
        if rels_created:
            self.log.debug("Waiting for relations %d", self.options.rel_wait)
            time.sleep(self.options.rel_wait)


def main():
    parser = setup_parser()
    (options, args) = parser.parse_args()
    setup_logging(options)
    log = logging.getLogger("deployer.cli")

    start_time = time.time()

    env = Environment(options.juju_env)
    config = ConfigStack(options.configs or [])

    # Debug implies watching
    if options.debug and not options.watch:
        options.watch = True

    # Destroy services and exit
    if options.destroy_services or options.terminate_machines:
        log.debug("Resetting environment...")
        env.connect()
        env.reset(terminate_machines=options.terminate_machines,
                  terminate_delay=1,
                  watch=options.watch)
        log.info("Environment reset")
        sys.exit(0)

    # Display service info and exit
    if options.find_service:
        address = env.get_service_address(options.find_service)
        if address is None:
            log.error("Service not found %r", options.find_service)
            sys.exit(1)
        elif not address:
            log.warning("Service: %s has no address for first unit",
                        options.find_service)
        else:
            log.info("Service: %s address: %s", options.find_service, address)
        sys.exit(0)

    # Arg check on config files and deployment name.
    if not options.configs:
        log.error("Config files must be specified")
        sys.exit(1)

    config.load()

    # Just list the available deployments
    if options.list_deploys:
        log.info("%s", " ".join(config.keys()))
        sys.exit(0)

    # Do something to a deployment
    if not args:
        log.error(
            "Deployment name must be specified. available: %s", tuple(config.keys()))
        sys.exit(1)

    deploy_name = args[0]
    deployment = config.get(deploy_name)

    log.debug("Starting deployment")
    try:
        Importer(env, deployment, options).run()
    except ErrorExit:
        sys.exit(1)
    finally:
        env.close()

    # Deploy complete
    log.info("Deployment complete in %0.2f seconds" % (time.time() - start_time))


if __name__ == '__main__':
    main()
