# Plugin Component Services Manager.
 #-
 # Copyright (c) 2013 Clint Banis (hereby known as "The Author")
 # All rights reserved.
 #
 # Redistribution and use in source and binary forms, with or without
 # modification, are permitted provided that the following conditions
 # are met:
 # 1. Redistributions of source code must retain the above copyright
 #    notice, this list of conditions and the following disclaimer.
 # 2. Redistributions in binary form must reproduce the above copyright
 #    notice, this list of conditions and the following disclaimer in the
 #    documentation and/or other materials provided with the distribution.
 # 3. All advertising materials mentioning features or use of this software
 #    must display the following acknowledgement:
 #        This product includes software developed by The Author, Clint Banis.
 # 4. The name of The Author may not be used to endorse or promote products
 #    derived from this software without specific prior written permission.
 #
 # THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS
 # ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
 # TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 # PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS
 # BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 # CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 # SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 # INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 # CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 # ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 # POSSIBILITY OF SUCH DAMAGE.
 #
# ---
# Purpose: configuring optional (external to core) components generically
#
from mud.runtime.facilities import Facility, LoadFacility
from mud.runtime.registry import getObject
from mud.runtime import LookupObject as LookupPluginAction
from mud.management.config import loadConfig

from game import syslog

from os.path import abspath, exists as fileExists
import traceback

import re
COMPONENT_PATTERN = re.compile('^component(?:\.\d+)?$')
GROUP_PATTERN = re.compile('component-group(?:\.\d+)?$')
FACILITY_PATTERN = re.compile('facility(?:\.\d+)?$')

PKGDEP_PATTERN = re.compile('package(?:\.\d+)?$')
SVCDEP_PATTERN = re.compile('service(?:\.\d+)?$')

import sys
if sys.platform == 'win32':
    PATH_PATTERN = re.compile('^windows-path(?:\.\d+)?$')
elif sys.platform == 'cygwin':
    PATH_PATTERN = re.compile('^path(?:\.\d+)?$')
else:
    PATH_PATTERN = re.compile('^path(?:\.\d+)?$')

class PluginManager(Facility):
    NAME = 'Plugin::Manager'
    CACHE_NAME = 'Plugin::Manager::Cache'

    def loadBootPlugins(self):
        pluginCache = getObject(self.CACHE_NAME, create = dict)
        thesePlugins = []

        from mud import getSection
        cfg = getSection('Services')
        for opt in cfg.options():
            if COMPONENT_PATTERN.match(opt) is not None:
                plugin = self.loadPluginFromConfig(cfg[opt])
                if plugin is not None:
                    if plugin.name not in pluginCache:
                        pluginCache[plugin.name] = plugin
                        thesePlugins.append(plugin)

            elif GROUP_PATTERN.match(opt) is not None:
                # todo: load a group of services/plugins from file/directory
                pass

            elif FACILITY_PATTERN.match(opt) is not None:
                LoadFacility(cfg[opt])

        for plugin in thesePlugins:
            try: plugin.boot()
            except: traceback.print_exc() # XXX warn

    __init__ = loadBootPlugins

    def loadPluginFromConfig(self, config_file):
        config_file = abspath(config_file)
        if fileExists(config_file):
            try: return Plugin.LoadFromConfig(config_file)
            except: traceback.print_exc()

class Plugin:
    class Type(str):
        def __repr__(self):
            return self

    UnknownType = Type('unknown')
    PythonPluginType = Type('python-service')

    @classmethod
    def LoadFromConfig(self, config_file):
        cfg = loadConfig(config_file)
        return self(config_file, cfg)

    MODE_BOOT = 'boot'
    MODE_LOAD = 'load'
    MODE_UNLOAD = 'unload'
    MODE_SHUTDOWN = 'shutdown'

    LIFECYCLE_SECTIONS = [MODE_BOOT, MODE_LOAD, MODE_UNLOAD, MODE_SHUTDOWN]

    def __init__(self, config_file, cfg):
        self.config_file = config_file
        self.mode = None

        # XXX These don't validation as non-None!
        module = cfg['Module']
        self.name = module['name']
        self.type = module.get('type', self.UnknownType)
        self.package = module['package']
        self.added_paths = []
        self.paths = self.loadPathsFromConfig(module)
        self.lifecycle = {}

        self.dependencies = self.loadDependenciesFromConfig(cfg['Dependencies'])

        for section in cfg.sections():
            mode = section.lower()
            if mode in self.LIFECYCLE_SECTIONS:
                self.lifecycle[mode] = self.loadLifecycle(cfg[section])

    def __repr__(self):
        return '<%s: %s (%s) [%s] %s>' % (self.__class__.__name__, self.name,
                                          self.type, self.package, self.mode)

    class Lifecycle:
        ACTION_NAMES = ['method', 'action', 'object']
        def __init__(self, cfg):
            for name in self.ACTION_NAMES:
                try:
                    value = cfg[name]
                    if value is None:
                        continue

                    self.action = value
                    self.name = name
                    break
                except KeyError:
                    pass
            else:
                raise ValueError('No action name specified in the lifecycle! %s' % self.ACTION_NAMES)

        def __repr__(self):
            return '<%s: action = %s>' % (self.__class__.__name__, self.action)

    loadLifecycle = Lifecycle

    def loadPathsFromConfig(self, module):
        path_collection = []
        for opt in module.options():
            if PATH_PATTERN.match(opt):
                path = module[opt]
                if path and path not in path_collection:
                    path_collection.append(path)

        return path_collection

    def loadPathsIntoSystem(self, these_paths):
        from sys import path as system_path
        added_paths = []
        for path in these_paths:
            path = abspath(path)
            if path not in system_path:
                added_paths.append(path)
                system_path.append(path)

        # For future unload..?
        self.added_paths = added_paths

    def loadDependenciesFromConfig(self, cfg):
        pkgdeps = []
        svcdeps = []

        for opt in cfg.options():
            if PKGDEP_PATTERN.match(opt):
                pkg = cfg.get(opt)
                if pkg not in pkgdeps:
                    pkgdeps.append(pkg)

            elif SVCDEP_PATTERN.match(opt):
               svc = cfg.get(opt)
               if svc not in svcdeps:
                   svcdeps.append(svcdeps)

        deps = []
        for pkg in pkgdeps:
            deps.append(self.PackageDependency(pkg))
        for svc in svcdeps:
            deps.append(self.ServiceDependency(svc))

        return deps

    class PackageDependency:
        def __init__(self, package_name):
            self.package_name = package_name
        def load(self):
            # is this sufficient for full import?
            try: return __import__(self.package_name)
            except ImportError, e:
                syslog('PACKAGE-DEPENDENCY: %s: %s' % (self.package_name, e))
                return False

            return True

    class ServiceDependency:
        def __init__(self, service_name):
            self.service_name = service_name
        def load(self):
            e = NotImplementedError('No way to load service dependencies, yet!')
            syslog('SERVICE-DEPENDENCY: %s: %s' % (self.service_name, e))
            return True

    def loadDependenciesIntoSystem(self, dependencies):
        for dep in dependencies:
            try:
                if not dep.load():
                    return False

            except:
                traceback.print_exc() # todo: log
                return False

        return True

    def lookupAction(self, name):
        if self.type == self.PythonPluginType:
            return LookupPluginAction('%s.%s' % (self.package, name))

        raise TypeError(self.type)

    # Lifecycles.
    def changeMode(self, mode):
        self.mode = mode

        try: action = self.lifecycle[mode].action
        except KeyError: pass
        else:
            action = self.lookupAction(action)
            if callable(action):
                try: action(self, mode)
                except: traceback.print_exc() # XXX change into error mode

    def boot(self):
        self.loadPathsIntoSystem(self.paths)
        if self.loadDependenciesIntoSystem(self.dependencies):
            self.changeMode(self.MODE_BOOT)
        else:
            # Rollback paths load-in??
            pass

def installPlugins():
    # This is called during mud.bootStart, but eventually I want to be
    # able to hot-plug plugin components, too.
    PluginManager.manage()
    PluginManager.get(create = True)
