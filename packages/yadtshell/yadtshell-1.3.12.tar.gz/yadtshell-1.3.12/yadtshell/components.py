#! /usr/bin/env python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
from __future__ import absolute_import

import logging
import os
import subprocess
import sys
import yaml

import yadtshell



logger = logging.getLogger('components')

class Component(object):
    def __init__(self, t, host, name=None, version=None):
        self.type = t
        if isinstance(host, str):
            self.host = host
        else:
            self.host = host.host
            self.fqdn = host.fqdn
        self.host_uri = yadtshell.uri.create(yadtshell.settings.HOST, self.host)
        self.name = getattr(self, 'name', name)
        if self.name is not None:
            self.name = self.name.rstrip('/').split('/', 1)[0]
        self.version = version
        if self.version is not None:
            self.version = str(self.version)
        self.uri = yadtshell.uri.create(self.type, self.host, self.name, self.version)
        self.version = yadtshell.uri.parse(self.uri)['version']
        self.name_and_version = yadtshell.uri.as_source_file(self.uri)
        self.state = yadtshell.settings.UNKNOWN
        self.revision = yadtshell.settings.EMPTY
        self.needs = getattr(self, 'needs', set())
        self.needed_by = set()
        self.config_prefix = yadtshell.settings.TARGET_SETTINGS['name']

    def is_touched_also(self, other):
        return True

    def __str__(self):
        return self.uri

    def dump(self):
        res = self.uri + "\n"
        res += yaml.dump(self)
        return res

    def is_up(self):
        return not yadtshell.util.not_up(self.state)

    def is_unknown(self):
        return self.state == yadtshell.settings.UNKNOWN

    def create_remote_log_filename(self, tag=None):
        return yadtshell.helper.create_log_filename(
            yadtshell.settings.TODAY, 
            yadtshell.settings.TARGET_SETTINGS['name'], 
            yadtshell.settings.STARTED_ON, 
            yadtshell.settings.USER_INFO['user'], 
            self.host, 
            tag
        )

    def remote_call(self, cmd, tag=None, force=False):
        if not cmd:
            return
        if type(cmd) is not str:
            cmd = '\n'.join(cmd)

        ssh_cmd = yadtshell.settings.SSH
        if hasattr(self, 'fqdn'):
            host = self.fqdn
        else:
            # TODO valid for uninitialized hosts
            host = self.host
        # TODO only suiteable for service objects!
        service = self.name 
        remotecall_script = '/usr/bin/yadt-remotecall'
        log_file = self.create_remote_log_filename(tag=tag)
        owner = yadtshell.util.get_locking_user_info()['owner']
        is_force = {False: '', True: '-f'}[force]
        complete_cmd = '''%(ssh_cmd)s %(host)s %(remotecall_script)s -l %(log_file)s -m %(owner)s -s %(service)s %(is_force)s \"%(cmd)s\" ''' % locals()
        return complete_cmd

    def local_call(self, cmd, tag=None, guard=True, force=False, no_subprocess=True):
        if not cmd:
            return
        if type(cmd) is str:
            cmds = cmd
        else:
            cmds = '\n'.join(cmd)
        print cmds
        if no_subprocess:
            return cmds
        if guard:
            sp = self.remote_call(": #check service callable", tag='check_service_callable', force=force)
            returncode = yadtshell.util.log_subprocess(sp)
            if returncode != 0:
                return returncode
        pipe = subprocess.Popen(
            cmds,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        pipe.stdin.flush()
        pipe.stdin.close()
        return pipe

    def _create_owner_file(self, lockinfo, filename, force=False, tag=None):
        """@return: integer The error code of the remote call"""
        dirname = os.path.dirname(filename)
        cmd = '''umask 0002 && mkdir -pv %s && echo -e '%s' > %s''' % (dirname, yadtshell.util.get_yaml(lockinfo), filename)
        return self.remote_call(cmd, tag, force=force)

    def _remove_owner_file(self, lockinfo, filename, force=False, tag=None):
        """@return: integer The error code of the remote call"""
        cmd = "rm -fv %(filename)s" % locals()
        return self.remote_call(cmd, tag, force=force)

class MissingComponent(Component):
    def __init__(self, s):
        parts = yadtshell.uri.parse(s)
        Component.__init__(self, parts['type'], parts['host'], parts['name'], parts['version'])
        self.state = yadtshell.settings.MISSING

class ComponentDict(dict):
    def __init__(self):
        dict.__init__(self)
        self._add_when_missing_ = False

    def _key_(self, key):
        try:
            return self._key_(key.uri)
        except AttributeError:
            return key

    def __getitem__(self, key):
        if self._key_(key) not in self and self._add_when_missing_:
            logger.debug('missing ' + key)
            self[self._key_(key)] = MissingComponent(self._key_(key))
        return dict.__getitem__(self, self._key_(key))
    def get(self, key, default=None):
        if self._key_(key) not in self and self._add_when_missing_:
            logger.debug('missing' + key)
            self[self._key_(key)] = MissingComponent(key)
        return dict.get(self, self._key_(key), default)
    def __setitem__(self, key, value):
        #logger.debug('adding ' + self._key_(key) + ' ' + getattr(value, 'state', ''))
        return dict.__setitem__(self, self._key_(key), value)

class ComponentSet(set):
    def __init__(self, components=None):
        self.components = components
        self._set = set([])

    def _key_(self, item):
        try:
            return str(item.uri)
        except AttributeError:
            return str(item)

    def add(self, item, check=False):
        key = self._key_(item)
        logger.debug('adding ' + key)
        if key not in self.components and check:
            logger.warning('key %(key)s not found, ignoring' % locals())
            #logger.warning('known keys: ' + ', '.join(self.components.keys()))
            return None
        return self._set.add(key)

    def __iter__(self):
        if self.components is None:
            for item in self._set:
                yield item
        else:
            for item in self._set:
                result = self.components.get(item)
                yield result

    def update(self, other):
        for c in other:
            self.add(c)

    def __contains__(self, item):
        return self._key_(item) in self._set

class Host(Component):
    def __init__(self, name):
        self.lockstate = None
        self.is_locked = None
        self.is_locked_by_other = None
        self.is_locked_by_me = None
        Component.__init__(self, yadtshell.settings.HOST, name)

    def update(self):
        return self.remote_call('sudo /usr/bin/yadt-yum upgrade', '%s_%s' %
                (self.hostname, yadtshell.settings.UPDATE))

    def bootstrap(self):
        pass    # TODO to be implemented

    def is_uptodate(self):
        return self.state == yadtshell.settings.UPTODATE

    def is_update_needed(self):
        return self.state == yadtshell.settings.UPDATE_NEEDED

    def probe(self):
        return self.remote_call('/usr/bin/yadt-status-host')

    def probe_uptodate(self):
        return yadtshell.util.log_subprocess(self.remote_call('/usr/bin/yadt-status-host', '%s_probe' % self.hostname))

    def get_lock_dir(self):
        return self.defaults['YADT_LOCK_DIR']

    def get_ignored_dir(self):
        return self.defaults['YADT_LOCK_DIR']

    def get_lock_owner(self):
        if self.lockstate:
            return self.lockstate["owner"]
        else:
            return None

    def lock(self, message=None, force=False, **kwargs):
        if not message:
            raise ValueError('the "message" parameter is mandatory')
        lockinfo = yadtshell.util.get_locking_user_info()
        lockinfo["message"] = message
        lockinfo["force"] = force
        return self._create_owner_file(
                lockinfo, 
                os.path.join(self.get_lock_dir(), 'host.lock'),  # TODO extract method for filename
                force=force, tag="lock_host")

    def unlock(self, force=False, **kwargs):
        lockinfo = yadtshell.util.get_locking_user_info()
        return self._remove_owner_file(
                lockinfo, 
                os.path.join(self.get_lock_dir(), 'host.lock'),  # TODO extract method for filename
                force=force, 
                tag="unlock_host")

    def update_attributes_after_status(self):
        self.is_locked = not self.lockstate is None

        lockinfo = yadtshell.util.get_locking_user_info()
        lock_owner = None
        if self.lockstate:
            lock_owner = self.lockstate.get("owner")
        self.is_locked_by_me = self.is_locked and lock_owner and lock_owner == lockinfo["owner"]

        self.is_locked_by_other = self.is_locked and not self.is_locked_by_me

        logger.debug("is_locked=" + repr(self.is_locked) + ", is_locked_by_me=" + repr(self.is_locked_by_me) + ", is_locked_by_other=" + repr(self.is_locked_by_other))


class Artefact(Component):
    def __init__(self, host, name, version=None):
        Component.__init__(self, yadtshell.settings.ARTEFACT, host, name, version)
        #self.needs.add(uri.create(settings.HOST, host.host))

    def updateartefact(self):
        return self.remote_call('sudo /usr/bin/yadt-yum upgrade -y %s' % self.name, 
                                'artefact_%s_%s_%s' % (self.host, self.name, yadtshell.constants.UPDATEARTEFACT))



class Service(Component):
    def __init__(self, host, name, settings = None):
        Component.__init__(self, yadtshell.settings.SERVICE, host, name)
        
        self.needs_services = []
        self.needs_artefacts = []
        self.needs = set()

        for k in settings:
            setattr(self, k, settings[k])
        extras = settings.get('extra', [])
        for k in extras:
            if hasattr(self, k):
                getattr(self, k).extend(extras[k])
            else:
                setattr(self, k, extras[k])

        for n in self.needs_services:
            if n.startswith(yadtshell.settings.SERVICE):
                self.needs.add(n % locals())
            else:
                self.needs.add(yadtshell.uri.create(yadtshell.settings.SERVICE, host.host, n % locals()))
        for n in self.needs_artefacts:
            self.needs.add(yadtshell.uri.create(yadtshell.settings.ARTEFACT, host.host, n % locals() +
                "/" + yadtshell.settings.CURRENT))
        #self.needs.add(uri.create(yadtshell.settings.HOST, host.host))
        
        self.state = yadtshell.settings.STATE_DESCRIPTIONS.get(settings.get('state'),
                yadtshell.settings.UNKNOWN)
        self.script = None


    #@timelimit(10)
    def stop(self, force=False, **kwargs):
        return self.remote_call(self._retrieve_service_call(yadtshell.settings.STOP),
                '%s_%s' % (self.name, yadtshell.settings.STOP), force)

    #@timelimit(10)
    def start(self, force=False, **kwargs):
        return self.remote_call(self._retrieve_service_call(yadtshell.settings.START),
                '%s_%s' % (self.name, yadtshell.settings.START), force)

    #@timelimit(2)
    def status(self):
        return self.remote_call(self._retrieve_service_call(yadtshell.settings.STATUS),
                tag='%s_%s' % (self.name, yadtshell.settings.STATUS), force=True)

    def _retrieve_service_call(self, action):
        name = self.name
        return 'sudo /sbin/service %(name)s %(action)s' % locals()

    def ignore(self, message=None, **kwargs):
        if not message:
            raise ValueError('the "message" parameter is mandatory')
        components = yadtshell.util.restore_current_state()
        host = components[self.host_uri]
        result = self._create_owner_file(
            yadtshell.util.get_locking_user_info(),
            os.path.join(host.get_ignored_dir(), 'ignore.%s' % self.name),  # TODO extract method for filename
            force=kwargs.get('force', False),
            tag="ignore_%s" % self.name)
        if not result:
            logger.warn("Could not ignore %s. Try --force" % self.uri)
        return result

    def unignore(self, **kwargs):
        components = yadtshell.util.restore_current_state()
        host = components[self.host_uri]
        result = self._remove_owner_file(
            yadtshell.util.get_locking_user_info(),
            os.path.join(host.get_ignored_dir(), 'ignore.%s' % self.name),  # TODO extract method for filename
            force=True, #kwargs.get('force'),
            tag="unignore_%s" % self.name)
        if not result:
            logger.warn("Could not unignore %s. Try --force" % self.uri)
        return result


def do_cb(protocol, args, opts):
    return do(args, opts)

def do(args, opts):
    cmd = args[0]
    component_names = args[1:]
    if not component_names:
        logger.error('no components given to "%(cmd)s", aborting' % locals())
        sys.exit(1)

    components = yadtshell.util.restore_current_state()
    component_names = yadtshell.helper.expand_hosts(component_names)
    component_names = yadtshell.helper.glob_hosts(components, component_names)

    for component_name in component_names:
        component = components.get(component_name, None)
        if not component:
            component = components[yadtshell.uri.change_version(component_name, 'current')]
        fun = getattr(component, cmd, None)
        import inspect
        if inspect.ismethod(fun):
            try:
                sp = fun(**opts)
            except TypeError:
                sp = fun()
        else:
            logger.error('"%(cmd)s" is not defined for %(component_name)s, aborting' % locals())
            sys.exit(2)
        logger.debug('%(cmd)sing %(component_name)s' % locals())
        try:
            logger.debug('executing fun ' + str(fun))
            if isinstance(sp, subprocess.Popen):
                exit_code = yadtshell.util.log_subprocess(sp, stdout_level=logging.INFO)
            else:
                exit_code = sp
            logger.debug('exit code %(exit_code)s' % locals())
        except AttributeError, ae:
            logger.warning('problem while executing %(cmd)s on %(component_name)s' % locals())
            logger.exception(ae)

#if __name__ == "__main__":
#    from optparse import OptionParser
#    parser = OptionParser()
#    parser.add_option('-m', '--message', dest='message', help='reason for action')
#    parser.add_option('', '--force', dest='force', action='store_true',
#            default=False, help='force action')
#    opts, args = parser.parse_args()
#
#    from twisted.internet import reactor
#    import yadttwisted
#    
#    deferred = do(args, **vars(opts))
#    print deferred
#    deferred.addErrback(yadttwisted.report_error)
#    deferred.addBoth(yadttwisted.stop_and_return)
#
#    if not reactor.running:
#        reactor.return_code = 127
#        reactor.run()
#
#    sys.exit(reactor.return_code)
#
