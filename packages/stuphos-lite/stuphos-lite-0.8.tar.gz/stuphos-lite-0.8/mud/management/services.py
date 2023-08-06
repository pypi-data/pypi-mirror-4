# Automatic service configuration for zone modules.
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
from mud.runtime.registry import getObject as getRegistryObject, RegistryNotInstalled
from mud.tools import isYesValue, capitalize, getSystemException, logException

from mud.management.config import getStandardPath, getParentPath, loadConfig
from mud.management.config import getStandardPath, getParentPath, loadConfig

def getEnablingSection(name):
    # A shorter, sweeter version.
    from mud import getSection
    from mud.tools import isYesValue

    cfg = getSection(name)
    def isEnabled(option):
        return isYesValue(cfg.get(option))

    return isEnabled

class AutoServices:
    CONFIG_SECTION_NAME = 'Services'

    @classmethod
    def ParentPath(self, base, *parts):
        return self.JoinPath(getParentPath(base), *parts)

    @classmethod
    def JoinPath(self, *parts):
        return getStandardPath(*parts)

    def __init__(self, setup_deferred = False):
        self.reset()

        # Do the actual object setup during load because maybe the
        # (configuration) objects aren't around yet.
        self.setup_deferred = setup_deferred
        if not setup_deferred:
            self.setup()

    def setup(self):
        try:
            configObj = getRegistryObject(self.CONFIG_OBJECT_NAME,
                                          create = lambda:loadConfig(self.CONFIG_FILE))

            self.section = configObj.getSection(self.CONFIG_SECTION_NAME)
            self.configObj = configObj
        except RegistryNotInstalled:
            self.section = None

    def getConfigObject(self):
        return self.configObj
    def getConfigSection(self):
        return self.section
    def getConfig(self, name, section = None):
        return self.getConfigObject().get(name, section = self.CONFIG_OBJECT_NAME
                                          if section is None else section)

    def reloadConfig(self):
        # todo: use method-based api..
        del runtime[self.CONFIG_OBJECT_NAME]
        self.setup()

    def reset(self):
        self.loaded = set()

    class ServiceConf:
        def __init__(self, name, value):
            self.name = name
            self.value = value

    def getServiceLoaderName(self, name):
        return 'load' + ''.join(capitalize(part) for part in name.split('-'))

    def findServiceLoader(self, conf):
        methodName = self.getServiceLoaderName(conf.name)
        return getattr(self, methodName, None)

    def iterateConfServices(self):
        if self.section:
            for opt in self.section.options():
                conf = self.ServiceConf(opt, self.section.get(opt))
                function = self.findServiceLoader(conf)

                if callable(function):
                    yield (conf, function)

    def shouldLoad(self, conf):
        try:
            if conf.name not in self.loaded:
                return isYesValue(conf.value)
        finally:
            self.loaded.add(conf.name)

    def __call__(self):
        if self.setup_deferred:
            self.setup()

        for (conf, load) in self.iterateConfServices():
            if self.shouldLoad(conf):
                try: load(conf)
                except: self.error(*getSystemException())

    def error(self, etype, evalue, tb):
        # Non-fatal.
        logException(etype, evalue, tb, traceback = True)
