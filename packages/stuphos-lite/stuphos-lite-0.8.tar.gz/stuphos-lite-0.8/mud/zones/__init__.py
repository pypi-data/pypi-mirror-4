 #-
 # Copyright (c) 2003 - 2013 Clint Banis (hereby known as "The Author")
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
from mud import log, getConfig
from mud.tools import InterpolateStringVariables
from os.path import realpath, dirname, basename

core = None
def initForCore():
    # Dynamically install component.
    from mud.runtime import Component
    class Instrument(Component, World):
        pass

    global core
    core = Instrument

    ##    global core
    ##    from mud.runtime import newComponent
    ##    core = newComponent(World)

# Top-Level Construct.
class World:
    ZONE_CONFIG_FILE = 'etc/zones.cfg'
    def getZoneConfigFile(self):
        return getConfig('zone-config-file') or self.ZONE_CONFIG_FILE

    def onResetStart(self, ctlr):
        self.zoneModules = loadZoneFile(self.getZoneConfigFile())
        for module in self.zoneModules:
            try: module.importModule()
            except ImportError:
                name = module.name and ('[%s]' % module.name) or ''
                log('Unknown Zone Module%s: %r' % (name, module.package))

    def onResetComplete(self, ctlr):
        # Initialize zone module associations.
        for module in self.zoneModules:
            # Configure special procedures first (that they may be overridden by module).
            # XXX Catch errors -- or, do this from within the loadSpecials routine.
            loadSpecialsConfigFromFile(module.getSpecialsFilename(self.getZoneConfigFile()))

            # Load module.
            loader = module.getLoader()
            if callable(loader):
                for zone in module.zones:
                    handle = zone.findHandle()
                    if handle is not None:
                        loader(self, module, zone, handle)

    # Supplemental.
    def onCreateZone(self, zone):
        pass
    def onLoadZone(self, zone):
        pass
    def onSaveZone(self, zone):
        pass
    def onUnloadZone(self, zone):
        pass

# Specials
from mud.zones.specials import loadSpecialsConfigFromFile

from mud.zones.config import dumpZoneInfoXMLToString
from mud.zones.config import dumpZoneInfoConfigToString
from mud.zones.config import dumpZoneModuleXMLToString
from mud.zones.config import dumpZoneModuleConfigToString

DEFAULT_PATH_DIRECTORY = {'lib-etc': 'etc',
                          'lib-text': 'text',
                          'lib-misc': 'misc',
                          'lib-world': 'world'}

class ZoneModule:
    DEFAULT_ZONE_LOADER_NAME = '__load_zone__'

    class ZoneInfo:
        def __init__(self, nr, guid, name):
            self.nr = nr
            self.guid = guid
            self.name = name

        def findHandle(self):
            # TODO: Validate against guid and zname.
            import world # from game-module.

            try: return world.zone(self.nr)
            except ValueError: pass

        # Serialization.
        def getData(self):
            return (self.nr, self.guid, self.name)
        def toXMLString(self, indent = ''):
            return dumpZoneInfoXMLToString(self.getData(), indent = indent)
        def toConfigString(self):
            return dumpZoneInfoConfigToString(self.getData())

        __repr__ = __str__ = toXMLString

    def __init__(self, name, package, handler = None, specials = None):
        self.name = name
        self.package = package
        self.handler = handler
        self.specials = specials
        self.zones = []

    def importModule(self):
        if self.package:
            return __import__(self.package)

    def getPackage(self):
        # Rename to importPackage?
        # fromlist: must not be []
        # return __import__(self.package, globals(), locals(), [''])
        if self.package:
            try: return self._package
            except AttributeError: pass

            module = self.importModule()
            for m in self.package.split('.')[1:]:
                module = getattr(module, m)

            self._package = module
            return module

    def getHandlerName(self):
        return self.handler or self.DEFAULT_ZONE_LOADER_NAME
    def getLoader(self):
        try:
            package = self.getPackage()
            if package:
                return getattr(package, self.getHandlerName(), None)

        except ImportError:
            pass

    def getSpecialsFilename(self, zone_config_filename = None):
        values = DEFAULT_PATH_DIRECTORY.copy() # Also, from actual config variables..
        values['module-package-path'] = dirname(getattr(self.getPackage(), '__file__', ''))

        values['zone-config-path'] = realpath(dirname(zone_config_filename)) if zone_config_filename else ''
        values['zone-config-name'] = basename(zone_config_filename) if zone_config_filename else ''

        path = InterpolateStringVariables(self.specials, **values)
        # todo: convert to platform-specific path
        return path

    def addZone(self, nr, guid, zname):
        self.zones.append(self.ZoneInfo(nr, guid, zname))

    def __iadd__(self, info):
        self.addZone(*info)
        return self

    # Serialization.
    def getData(self):
        return (self.name, self.package, self.handler, self.getZoneData())
    def getZoneData(self):
        return dict((z.nr, z.getData()) for z in self.zones)
    def toXMLString(self, indent = ''):
        return dumpZoneModuleXMLToString(self.getData(), indent = indent)
    def toConfigString(self):
        return dumpZoneModuleConfigToString(self.getData())

    __repr__ = __str__ = toXMLString

def loadZoneModules(modules):
    zoneModules = []
    for (name, package, handler, specials, zones) in modules:
        zm = ZoneModule(name, package, handler = handler, specials = specials)
        for (nr, guid, zname) in zones.itervalues():
            zm.addZone(nr, guid, zname)

        zoneModules.append(zm)
    return zoneModules

# Input Formats.
from config import parseZoneConfigFromFile, parseZoneConfigFromString
from config import parseZoneXMLFromFile, parseZoneXMLFromString
from config import parseZoneJSONFromFile, parseZoneJSONFromString
from config import parseZonePyFromFile, parseZonePyFromString

def loadZoneConfig(config):
    return loadZoneModules(parseZoneConfig(config))

def loadZoneConfigFromFile(config_file):
    return loadZoneModules(parseZoneConfigFromFile(config_file))
def loadZoneConfigFromString(string):
    return loadZoneModules(parseZoneConfigFromString(string))

def loadZoneXMLFromFile(xml_file):
    return loadZoneModules(parseZoneXMLFromFile(xml_file))
def loadZoneXMLFromString(string):
    return loadZoneModules(parseZoneXMLFromString(string))

def loadZoneJSONFromFile(json_file):
    return loadZoneModules(parseZoneJSONFromFile(json_file))
def loadZoneJSONFromString(string):
    return loadZoneModules(parseZoneJSONFromString(string))

def loadZonePyFromFile(py_file):
    return loadZoneModules(parseZonePyFromFile(py_file))
def loadZonePyFromString(string):
    return loadZoneModules(parseZonePyFromString(string))

# YAML
# Pickle

# Generic.
from config import parseZoneFile
def loadZoneFile(filename, *args, **kwd):
    return loadZoneModules(parseZoneFile(filename, *args, **kwd))
