# MUD Runtime Core.
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
# This should probably be called 'bootstrap' (the runtime is the core)
from . import BINDINGS, EVENT_NAMES, loadOnto, Binding
from ..tools.logs import *

from ..management.config import PackageManager, getParentPath, joinpath
from ..management.config import getStandardPath, loadConfig

from .registry import getObject as getRegistryObject
from .registry import delObject as deleteRegistryObject
from .registry import RegistryNotInstalled

from .plugins import installPlugins

__version__ = 0.8

def getBridgeModule():
    ##    # First code to load the game module.
    ##    from pdb import run
    ##    run('from game import bridgeModule')

    from game import bridgeModule
    return bridgeModule()

def callEventBridge(name, *args, **kwd):
    try: event = getattr(getBridgeModule(), name)
    except AttributeError: pass
    else:
        if callable(event):
            return event(*args, **kwd)

def getMudModule():
    import mud
    return mud

def getHeartbeat():
    return getBridgeModule().heartbeat

def enqueueHeartbeatTask(*args, **kwd):
    return getHeartbeat().enqueueTask(*args, **kwd)
def deferredTask(*args, **kwd):
    return getHeartbeat().deferredTask(*args, **kwd)

enqueue = enqueueHeartbeatTask
executeInline = deferredTask

def inline(function):
    # Decorator
    def inlineWrapper(*args, **kwd):
        return executeInline(function, *args, **kwd)

    try: inlineWrapper.__name__ = function.__name__
    except AttributeError: pass

    try: inlineWrapper.__doc__ = function.__doc__
    except AttributeError: pass

    return inlineWrapper

def invokeTimeoutForHeartbeat(timeout, function, *args, **kwd):
    return getHeartbeat().invokeTimeoutForHeartbeat(timeout, function, *args, **kwd)
def invokeTimeout(timeout, function, *args, **kwd):
    return getHeartbeat().invokeTimeout(timeout, function, *args, **kwd)

CONFIG_OBJECT_NAME = 'MUD::Configuration'
CONFIG_FILE = getStandardPath('etc', 'config.cfg')

# mudConfig = runtime.MUD.Configuration
def _createMUDConfig():
    return loadConfig(CONFIG_FILE)
def getConfigObject():
    # return mudConfig(loadConfig, CONFIG_FILE)
    return getRegistryObject(CONFIG_OBJECT_NAME,
                             create = _createMUDConfig)

def deleteConfig():
    # del runtime[mudConfig]
    return deleteRegistryObject(CONFIG_OBJECT_NAME)

def reloadConfigFile(filename):
    global CONFIG_FILE
    CONFIG_FILE = filename
    deleteConfig()

def getConfig(name, section = 'MUD'):
    try: return getConfigObject().get(name, section = section)
    except RegistryNotInstalled: pass
def getSection(section = 'MUD'):
    try: return getConfigObject().getSection(section)
    except RegistryNotInstalled: pass

SITE_PATH = getParentPath(getParentPath(getParentPath(__file__)))
COMPONENTS_FILE = 'components.pth'

EASY_SITE_PATH = joinpath(SITE_PATH, 'packages/third-party')
EASY_INSTALL_FILE = 'easy-install.pth'

def installSite():
    # Manually search non-standard paths for .pth files.
    PackageManager(SITE_PATH, COMPONENTS_FILE).install()
    PackageManager(EASY_SITE_PATH, EASY_INSTALL_FILE).install()

def installBridge():
    bridgeModule = getBridgeModule()
    thisModule = getMudModule()

    # from mud.runtime import declare, DeclareEvent
    # declare(bridgeModule, EVENTS)
    loadOnto(BINDINGS, bridgeModule)

    thisModule.on = Binding(bridgeModule)
    thisModule.core = Binding(thisModule)

    ##    class bootStart(DeclareEvent):
    ##        Module = thisModule
    ##    class bootComplete(DeclareEvent):
    ##        Module = thisModule

    return bridgeModule

def installHost():
    from socket import error
    from errno import EADDRINUSE
    try:
        from mud.tasks.xmlrpc import getHost
        getHost(create = True).start()
    except error, e:
        if e.args[0] is not EADDRINUSE:
            from mud.tools import reraiseSystemException
            reraiseSystemException()

        logWarning('Host port is in used -- XMLRPC disabled.  Please reconfigure!')

def installEnviron():
    # Configure the system/shell environment.
    from os import environ
    envCfg = getSection('Environment')
    for name in envCfg.options():
        environ[name] = envCfg.get(name)

def installServices():
    # Create binding to bridge module.
    from mud.runtime.registry import getRegistry
    getRegistry(create = getMudModule().on)

    # Todo: actually make this a registered COM object!
    from mud.tasks import Machine
    getBridgeModule().heartbeat = Machine()

    # Pre-Management Set:
    installEnviron()
    installHost()

    try: from mud.management import initForCore
    except ImportError: pass
    else: initForCore()

    # Todo: integrate this into management initForCore?
    installPlugins()

def installWorld():
    try: from mud.zones import initForCore
    except ImportError: pass
    else: initForCore()

    from mud.player.commands import installCommands
    installCommands()

# Event Bridge.
def bootStart():
    # Note: this function must return the bridge, or
    # the rest of the extension is not installed.

    # todo: import more of management
    # import mud.tools.debug

    installSite()
    bridge = installBridge()

    try:
        installServices()
        installWorld()

        from mud.management.reboot import StartRecovery
        StartRecovery()

    except:
        logException(traceback = True)
    finally:
        return bridge

def bootComplete((secs, usecs)):
    try: from mud.management.reboot import CompleteRecovery
    except ImportError: pass
    else: CompleteRecovery()
