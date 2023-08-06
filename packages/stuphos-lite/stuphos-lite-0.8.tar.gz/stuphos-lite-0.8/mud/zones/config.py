# INI Format.
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
from mud.tools import fromJsonFile, fromJsonString, toJsonFile, toJsonString

from ConfigParser import ConfigParser, NoOptionError
def getZoneConfigParser():
    return ConfigParser(defaults = dict(handler = '', specials = ''))

def parseZoneInfo(zone):
    info = zone.split(':', 3)
    if len(info) > 0:
        if info[0].isdigit():
            nr = int(info[0])
            if len(info) > 1:
                if len(info) > 2:
                    return (nr, info[1], info[2])
                return (nr, info[1], None)
            return (nr, None, None)

def getSoftConfigOption(cfg, section, name, *args, **kwd):
    try: return cfg.get(section, name, *args, **kwd)
    except NoOptionError:
        pass

def parseZoneConfig(config):
    modules = []
    for section in config.sections():
        if section.lower().startswith('module'):
            # Parse module name.  Skip all other sections.
            if len(section) > 6:
                if section[6] != ':':
                    continue
                name = section[7:]
            else:
                name = ''

            package = getSoftConfigOption(config, section, 'package')
            handler = getSoftConfigOption(config, section, 'handler')
            specials = getSoftConfigOption(config, section, 'specials', raw = True)

            zones = {}
            for opt in config.options(section):
                if opt.lower().startswith('zone'):
                    # Parse zone order number.
                    if len(opt) > 4:
                        if opt[4] != '.':
                            continue
                        znr = opt[5:]
                        if not znr.isdigit():
                            continue
                        znr = int(znr)
                    else:
                        znr = 0

                    info = config.get(section, opt)
                    info = parseZoneInfo(info)
                    if info is not None:
                        zones[znr] = info

            # Some modules just define specprocs:
            ##    if not package:
            ##        # Warning!
            ##        continue

            modules.append((name, package, handler, specials, zones))

    return modules

def parseZoneConfigFromFile(config_file):
    config = getZoneConfigParser()
    config.read([config_file])
    return parseZoneConfig(config)

def parseZoneConfigFromString(string):
    from cStringIO import StringIO
    config = getZoneConfigParser()
    config.readfp(StringIO(string)) # , '<init-buf>')
    return parseZoneConfig(config)

# XML Format.
from xml.sax.handler import ContentHandler
from xml.sax import parse as parseXML, parseString as parseXMLString

class ZoneModuleXML(ContentHandler):
    # Mostly validating.
    def __init__(self):
        self.modules = None
        self.current_m = None
        self.current_z = None
        self.setting = None

    def startElementNS(self, name, qname, attrs):
        if qname is not None:
            print 'ns:', qname

        # Todo: rewrite to look more state-based.
        lname = str(name).lower()
        if self.modules is None:
            if name.lower() != 'world':
                raise NameError(name)

            self.modules = []
        elif lname == 'module':
            if self.current_m is not None:
                raise NameError(name)
            else:
                # Todo: validate attrs
                self.current_m = dict((str(k).lower(), str(v)) for \
                                      (k, v) in attrs.items())
        elif lname == 'zone':
            if self.current_m is None:
                raise NameError(name)
            elif self.current_z is not None:
                raise NameError(name)
            else:
                # Todo: validate attrs
                self.current_z = dict((str(k).lower(), str(v)) \
                                      for (k, v) in attrs.items())
        else:
            if lname in ('package', 'handler'):
                if self.current_m is None:
                    raise NameError(name)
                if self.current_z is not None:
                    raise NameError(name)
            elif lname in ('number', 'guid'):
                if self.current_z is None:
                    raise NameError(name)
            elif lname != 'name':
                raise NameError(name)

    def endElementNS(self, name, qname):
        if qname is not None:
            print 'ns:', qname

        lname = str(name).lower()
        if lname == 'world':
            if self.modules is None:
                raise NameError(name)
            if self.current_m is not None:
                raise NameError(name)
        elif lname == 'module':
            if self.current_m is None:
                raise NameError(name)
            if self.current_z is not None:
                raise NameError

            # Plug it in.
            m = self.current_m
            self.current_m = None

            self.modules.append((m.get('name'),
                                 m.get('package'),
                                 m.get('handler'),
                                 m.get('zones')))

        elif lname == 'zone':
            if self.current_z is None:
                raise NameError(name)

            nr = self.current_z.get('number')
            if nr is None:
                raise ValueError('Zone without number!')
            elif not nr.isdigit():
                raise TypeError('Zone number is not a digit: %r' % nr)
            nr = int(nr)

            # Todo: validate settings.
            try: zones = self.current_m['zones']
            except KeyError:
                zones = self.current_m['zones'] = {}

            z = self.current_z
            self.current_z = None

            zones[nr] = (nr,
                         z.get('guid'),
                         z.get('name'))

        elif lname in ('package', 'handler'):
            if self.current_m is None:
                raise NameError(name)
            if self.current_z is not None:
                raise NameError(name)

            self.current_m[lname] = self.setting
            self.setting = None
        elif lname in ('guid', 'number'):
            if self.current_z is None:
                raise NameError(name)

            self.current_z[lname] = self.setting
            self.setting = None
        elif lname == 'name':
            if self.current_z:
                self.current_z[lname] = self.setting
            elif self.current_m:
                self.current_m[lname] = self.setting

            self.setting = None
        else:
            raise NameError(name)

    def characters(self, content):
        self.setting = str(content).strip()

    def startElement(self, name, attrs):
        return self.startElementNS(name, None, attrs)
    def endElement(self, name):
        return self.endElementNS(name, None)

    # Irrelevent (just interesting to see what comes through):
    def startPrefixMapping(self, prefix, uri):
        print 'start-prefix-mapping:', prefix, url
    def endPrefixMapping(self, prefix):
        print 'end-prefix-mapping:', prefix
    def processingInstruction(self, target, data):
        print 'processing-instruction:', target, data
    def skippedEntity(self, name):
        print 'skipped-entity:', name

def parseZoneXMLFromFile(xml_file):
    handler = ZoneModuleXML()
    parseXML(open(xml_file), handler)
    return handler.modules

def parseZoneXMLFromString(string):
    handler = ZoneModuleXML()
    parseXMLString(string, handler)
    return handler.modules

# JSON Format.
def parseZoneJSONFromFile(json_file):
    return _validateFormat(fromJsonFile(json_file))

def parseZoneJSONFromString(string):
    return _validateFormat(fromJsonString(json_file))

# Python Format -- UNSAFE!
def parseZonePyFromFile(py_file):
    return _validateFormat(eval(open(py_file).read()))
def parseZonePyFromString(string):
    return _validateFormat(eval(string))

# YAML
def parseZoneYAMLFromFile(yaml_file):
    from yaml import load
    return _validateFormat(load(open(yaml_file)))
def parseZoneYAMLFromString(string):
    from yaml import loads
    return _validateFormat(yaml.loads(string))

# Pickle
def parseZonePickleFromFile(pickle_file):
    from cPickle import load
    return _validateFormat(load(open(pickle_file)))
def parseZonePickleFromString(string):
    from cPickle import loads
    return _validateFormat(loads(string))

def _validateFormat(modules):
    # Todo: validate formats with associative keynames.
    for m in modules:
        if len(m) != 4:
            raise IndexError('Expected 4 items in module (not %d)' % len(m))
        if not m[1]:
            raise ValueError('No package specified')

        for z in m[3]:
            if len(z) != 3:
                raise IndexError('Expected 3 items in zone info (not %d)' % len(z))
            if type(z[0]) is not int:
                raise TypeError('Expected integer zone number (item 0), not %r' % type(z[0]).__name__)

    return modules

# Output Formats.
def dumpToBuffer(dumper, modules, *args, **kwd):
    from cStringIO import StringIO
    buf = StringIO()
    dumper(modules, buf, *args, **kwd)
    return buf.getvalue()

# Config
def dumpZoneInfoConfigToString(info):
    return ':'.join(v is not None and str(v) or '' for v in info)
def dumpZoneModuleConfigToStream(module, stream):
    if module[0]:
        print >> stream, '[Module:%s]' % module[0]
    else:
        print >> stream, '[Module]'

    if module[1]:
        print >> stream, 'package = %s' % module[1]
    if module[2]:
        print >> stream, 'handler = %s' % module[2]

    z = module[3].values()
    for x in xrange(len(z)):
        print >> stream, 'zone.%d = %s' % (x, dumpZoneInfoConfigToString(z[x]))
def dumpZoneModuleConfigToString(module):
    return dumpToBuffer(dumpZoneModuleConfigToStream, module)
def dumpZoneConfigToFile(modules, stream):
    for m in modules:
        dumpZoneModuleConfigToStream(m, stream)
def dumpZoneConfigToString(modules):
    return dumpToBuffer(dumpZoneConfigToFile, modules)

# XML
def dumpZoneInfoXMLToString(info, indent = ''):
    fields = ['Number="%d"' % info[0]]
    if info[2]:
        fields.append('Name="%s"' % info[2])
    if info[1]:
        fields.append('GUID="%s"' % info[1])

    return '%s<Zone %s />' % (indent, ' '.join(fields))
def dumpZoneModuleXMLToFile(module, stream, indent = ''):
    stream.write('%s<Module>\n' % indent)
    if module[0]:
        stream.write('%s    <Name>%s</Name>\n' % (indent, module[0]))
    if module[1]:
        stream.write('%s    <Package>%s</Package>\n' % (indent, module[1]))
    if module[2]:
        stream.write('%s    <Handler>%s</Handler>\n' % (indent, module[2]))

    indent1 = indent + '    '
    for zone in module[3].itervalues():
        stream.write(dumpZoneInfoXMLToString(zone, indent = indent1))
        stream.write('\n')

    stream.write('%s</Module>\n' % indent)
def dumpZoneModuleXMLToString(module, indent = ''):
    return dumpToBuffer(dumpZoneModuleXMLToFile, module, indent = indent)
def dumpZoneXMLToFile(modules, stream, indent = ''):
    # XXX Designed for use with loader...
    print >> stream, '<World xmlns="org/stuph/mud/zones/config">'
    indent1 = indent + '    '
    for zone in modules:
        dumpZoneModuleXMLToFile(zone, stream, indent = indent1)
    print >> stream, '</World>'
def dumpZoneXMLToString(modules):
    return dumpToBuffer(dumpZoneXMLToFile, modules)

# JSON
def dumpZoneJSONToFile(modules, stream):
    toJsonFile(modules, stream, indent = 1)
def dumpZoneJSONToString(modules):
    return dumpToBuffer(dumpZoneJSONToFile, modules)

# Py
def dumpZonePyToFile(modules, stream):
    for m in modules:
        print >> stream, 'name:', m[0]
        print >> stream, 'package:', m[1]
        print >> stream, 'handler:', m[2]
        for z in m[3].itervalues():
            print >> stream, '  nr:', z[0]
            print >> stream, '  guid:', z[1]
            print >> stream, '  name:', z[2]
def dumpZonePyToString(modules):
    return dumpToBuffer(dumpZonePyToFile, modules)

# YAML
def dumpZoneYAMLToFile(modules, stream):
    from yaml import dump
    dump(modules, stream)
def dumpZoneYAMLToString(modules):
    return dumpToBuffer(dumpZoneYAMLToFile, modules)

# Pickle
def dumpZonePickleToFile(modules, stream):
    from cPickle import dump
    dump(modules, stream)
def dumpZonePickleToString(modules):
    from cPickle import dumps
    return dumps(modules)

FORMATS = dict(cfg =  dict(parseFile   = parseZoneConfigFromFile,
                           parseString = parseZoneConfigFromString,
                           dumpFile    = dumpZoneConfigToFile,
                           dumpString  = dumpZoneConfigToString),

               xml =  dict(parseFile   = parseZoneXMLFromFile,
                           parseString = parseZoneXMLFromString,
                           dumpFile    = dumpZoneXMLToFile,
                           dumpString  = dumpZoneXMLToString),

               json = dict(parseFile   = parseZoneJSONFromFile,
                           parseString = parseZoneJSONFromString,
                           dumpFile    = dumpZoneJSONToFile,
                           dumpString  = dumpZoneJSONToString),

               py   = dict(parseFile   = parseZonePyFromFile,
                           parseString = parseZonePyFromString,
                           dumpFile    = dumpZonePyToFile,
                           dumpString  = dumpZonePyToString),

               yaml = dict(parseFile   = parseZoneYAMLFromFile,
                           parseString = parseZoneYAMLFromString,
                           dumpFile    = dumpZoneYAMLToFile,
                           dumpString  = dumpZoneYAMLToString),

               pkl  = dict(parseFile   = parseZonePickleFromFile,
                           parseString = parseZonePickleFromString,
                           dumpFile    = dumpZonePickleToFile,
                           dumpString  = dumpZonePickleToString))

def _getZoneFormat(filename, format = None):
    if format is None:
        assert filename
        from os.path import splitext
        format = splitext(filename)[1][1:].lower()

    info = FORMATS.get(format)
    if info is None:
        raise NameError('Unknown format: %r' % format)

    return info

def parseZoneFile(filename, format = None):
    parser = _getZoneFormat(filename, format)['parseFile']
    return parser(filename)
def dumpZoneFile(modules, stream, format):
    dumper = _getZoneFormat(None, format)['dumpFile']
    return dumper(modules, stream)

# Test Bed.
def testMain(argv = None):
    from optparse import OptionParser
    from sys import stdout

    parser = OptionParser()
    parser.add_option('-o', '--output-format', default = 'py')
    parser.add_option('-i', '--input-format')

    (options, args) = parser.parse_args(argv)

    for filename in args:
        modules = parseZoneFile(filename, options.input_format)
        dumpZoneFile(modules, stdout, options.output_format)

# todo: implement OLC submodules that manage zone-based modules.
# Associates zone-based modules built-in to a databased user component with olc-permissions/naming scheme.

if __name__ == '__main__':
    testMain()
