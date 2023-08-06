# Paths.
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
from os.path import join as joinpath, normpath, dirname
import sys

try: from path import path as pathObject
except ImportError:
    pathObject = str

def getPlatformDrivePath(drive_letter):
    if sys.platform.startswith('cygwin'):
        return '/cygdrive/%s' % str(drive_letter).lower()
    if sys.platform.startswith('win32'):
        return '%s:\\' % str(drive_letter).upper()

    return '/%s' % str(drive_letter)

def getStandardDrivePath(drive_letter, *parts):
    return getStandardPath(getPlatformDrivePath(drive_letter), *parts)

def getStandardPath(*parts):
    return pathObject(normpath(joinpath(*parts)))

def getParentPath(path):
    # Standardize?
    return dirname(path)

# Configuration Files.
from ConfigParser import ConfigParser, DEFAULTSECT, NoOptionError, NoSectionError

def loadConfig(filename, defaults = None):
    config = ConfigParser(defaults = defaults)
    config.read([filename])
    return Configuration(config, filename)

class Configuration:
    class Section:
        def __init__(self, config, section = None, **vars):
            if section is not None and type(section) is not str:
                raise TypeError(type(section).__name__)

            self.config = config
            self.section = section or DEFAULTSECT
            self.vars = vars

        def get(self, name, default = None):
            try: return self.config.config.get(self.section, name, vars = self.vars)
            except (NoOptionError, NoSectionError): return default

        def options(self):
            return self.config.options(self.section)

        def __iter__(self):
            return iter(self.options())
        def __getitem__(self, name):
            return self.get(name) # ??? Should this throw error?
        def __repr__(self):
            return "<Section '%s:%s'>" % (self.config.filename, self.section)

    def __init__(self, config, filename = None):
        self.config = config
        self.filename = filename

    def get(self, name, section = None, vars = None):
        try: return self.config.get(section, name, vars = vars)
        except (NoOptionError, NoSectionError): pass

    def sections(self):
        return self.config.sections()
    def options(self, section = None):
        try: return self.config.options(section or DEFAULTSECT)
        except NoSectionError: return []

    def getSection(self, section = None, **vars):
        return self.Section(self, section, **vars)
    def getDefaultSection(self, **vars):
        return self.getSection(self, **vars)

    def __iter__(self):
        return iter(self.sections())
    def __getitem__(self, section):
        return self.getSection(section)
    def __repr__(self):
        return "<Configuration '%s'>" % self.filename

# Package Support.
class PackageManager:
    def __init__(self, site_path = None, *components):
        if site_path is None:
            raise ValueError('Unsupported Site Path')

        self.site_path = site_path
        self.component_files = list(components)

    def install(self):
        from site import addpackage
        from sys import path as known_paths

        known_paths = set(known_paths)
        for comp_fl in self.component_files:
            addpackage(self.site_path, comp_fl, known_paths)

# Standard MUD Properties.
LIB_ETC = getStandardPath('etc')
