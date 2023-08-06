"""
Implement an interpreter-based OLC, which loads a syslog (by virtual FS) as an input source,
subjecting each line to a match against a pattern database, which matches and processes messages
based on their format.  The menu-based editor is used to process lines against existing templates,
and to allow provision of new templates for processed lines.

Process lines come from streamed sources: they can be from a file, possibly a re-scan of the entire
syslog, or, as a branched processing intercept from the mudlog programmable bridge event.  The editor
can then be used to edit a certain new batch of incoming lines that have not been matched yet.

The matched lines database associates with handlers that are called in the final target processing
of ongoing mudlog events.  It is the responsibility of the scheduler executing these handlers towards
unifying them within the mud whole.

---
Implementation:
        
"""
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

import re, errno, pickle, traceback,pprint
from os import popen

try: import readline as rl
except ImportError: rl = None

# Generic serializable pattern construct.
class pattern:
    def __init__(self, pattern):
        self.pattern = pattern

    def __getstate__(self):
        return self.pattern

    def __setstate__(self, pattern):
        self.pattern = pattern

    def __str__(self):
        return str(self.pattern)

    __reduce__ = __str__

class compile_pattern(pattern):
    'Implements regular-expression match.'
    TYPE = 'compiled'

    def __init__(self, pattern):
        self.pattern = pattern
        # self._compiled = re.compile(pattern)
        self.match = re.compile(pattern).match

    __setstate__ = __init__

class static_pattern(pattern):
    'Implements a simple equality match.'
    TYPE = 'static'

    def match(self, line):
        return line == self.pattern


logfile_timefmt_header = 'mon day 24h:m:s year     :: '

class PatternMatch:
    'Serializable database pattern-matching algorithm.'

    patternCollection = list # set

    def __init__(self, patterns = None):
        self.patterns = self.patternCollection(patterns) \
                            if patterns else self.patternCollection()
        self.lineno = 0
        self.processMatch = None

    def __getstate__(self):
        return (self.patterns, self.lineno)

    def __setstate__(self, state):
        (patterns, lineno) = state

        self.patterns = self.patternCollection(patterns)
        self.lineno = lineno

    # The algorithm, with callbacks:
    def matchlines(self, source):
        'Scan iteratable line source and generate full-stage pattern recognition processing.'

        for line in self.iterateLines(source):
            self.startMatch(line)

            result = False
            for pat in self.patterns:
                match = pat.match(line)
                if match:
                    result = True
                    yield (match, pat, line, self.lineno)

            if not result:
                yield (None, None, line, self.lineno)

            self.endMatch(line)

    def iterateLines(self, source):
        for line in source:
            self.lineno += 1

            # yield line
            # self.timestamp = strptime(logfile_timefmt_header, line[:28])
            self.timestamp = line[:28]
            yield line[28:]

    def startMatch(self, source):
        pass

    def endMatch(self, source):
        pass

    def addPattern(self, pattern):
        s = self.patterns
        if type(s) is list and pattern not in s:
            s.append(pattern)
        elif type(s) is set:
            s.add(pattern)

    def getPattern(self, index):
        return self.patterns[index] if type(self.patterns) is list else None

    def setPattern(self, index, pattern):
        if type(self.patterns) is list:
            self.patterns[index] = pattern

    __getitem__ = getPattern
    __setitem__ = setPattern

class InteractiveMatch(PatternMatch):
    'Interactive pattern match shell used for editing the syslog templates.'
    # High-level interface for pattern-matching database.

    def noMatch(self, line, lineno):
        'Interactive prompt when no match is found for a line.'

        while 1:
            resp = self.doPrompt(line).strip()
            if resp == '':
                break

            lresp = resp.lower()

            if resp == '=':
                # Add a static pattern for this line.
                self.addPattern(static_pattern(line))
                print 'Static Pattern added for:\n  %r' % line
                break

            elif lresp in ('-h', '-he', '-hel', '-help', '--h', '--he', '--hel', '--help'):
                self.doHelp(lresp)

            elif lresp in ('-s', '-sh', '-sho', '-show', '--s', '--sh', '--sho', '--show'):
                self.doShow(lresp)

            elif lresp in ('-sa', '-sav', '-save', '--sa', '--sav', '--save'):
                self.save()
                n = len(self.patterns)
                print '%d pattern%s saved.' % (n, 's' if n <> 1 else '')

            elif '-populate'.startswith(lresp):
                self.populatePatternHistory()

            elif '-replace'.startswith(lresp):
                pass
            elif '-up'.startswith(lresp):
                pass
            elif '-down'.startswith(lresp):
                pass
            elif '-back'.startswith(lresp):
                pass
            elif '-forward'.startswith(lresp):
                pass
            elif '-select'.startswith(lresp):
                pass

            else:
                try:
                    pat = compile_pattern(resp)
                except:
                    traceback.print_exc()
                    continue

                if not pat.match(line):
                    print 'line does not match:', resp
                    print '  ', line
                else:
                    self.addPattern(pat)
                    break

    def doPrompt(self, line):
        return raw_input('Provide a template match for:\n   %r\n? ' % line)

    def doHelp(self, command):
        self.page(re.__doc__)

    def doShow(self, command):
        s = self.patterns

        if type(s) is list:
            from cStringIO import StringIO
            b = StringIO()

            for x in xrange(len(s)):
                print >> b, '#%3d :' % x, str(s[x]).rstrip()

            self.page(b.getvalue())
        else:
            self.page('\r\n'.join(str(pat).rstrip() for pat in s))

    def page(self, msg, columnize = False):
        popen('less' if not columnize else 'column|less', 'w').write(msg)

    def populatePatternHistory(self):
        s = self.patterns
        if type(s) is list:
            x = len(s)
            def get(i):
                return str(s[i]).rstrip()

            n = rl.get_current_history_length()
            if n > x:
                n = x

            for i in xrange(n):
                rl.replace_history_item(i, get(i))

            if x > n:
                for i in xrange(n, x):
                    rl.add_history(get(i))

    def interactive(self, source = None, notifyMatch = None):
        if source is None:
            source = getattr(self, 'source', None)

        assert source
        self.source = source
        if not notifyMatch:
            notifyMatch = getattr(self, 'notifyMatch', None)

        try:
            for (match, pat, line, lineno) in self.matchlines(source):
                if match:
                    notifyMatch(match, pat, line, lineno)
                else:
                    self.noMatch(line, lineno)

        except EOFError:
            pass

    resume = interactive

    def notifyMatch(self, match, pattern, line, lineno):
        if hasattr(pattern, 'handleMatch'):
            return pattern.handleMatch(match, line, lineno)

        print 'Found (line #%d): %r' % (lineno, line)
        if type(match) is not type(True):
            print '  ', str(pattern).rstrip()
            print '  ', ', '.join(filter(None, match.groups()))

            gd = match.groupdict()
            if gd:
                pprint.pprint(gd)

    def save(self, file = None):
        pickle.dump(self, open(str(file or self.templates_file), 'w'))

    def export(self, filename):
        out = open(filename, 'wt')
        type = None
        nr = 0

        for pattern in self.patterns:
            if type != pattern.TYPE:
                type = pattern.TYPE
                if type is not None:
                    print >> out

                print >> out, '[%s]' % type.capitalize()

            # XXX careful:
            pattern = str(pattern).rstrip()

            print >> out, '%d: %s'  % (nr, pattern)
            nr += 1

        out.flush()
        out.close()

def loadPatternMatcher(templates_file):
    patternMatcher = InteractiveMatch
    try:
        if templates_file.endswith('.pkl'):
            # Deserialize.
            patmatch = pickle.load(open(templates_file))
        else:
            # Load templates from regular file -- constructing regexprs.
            patmatch = patternMatcher(compile_pattern(pattern) for pattern in open(templates_file))

        patmatch.templates_file = templates_file

    # Else default.
    except:
        from sys import exc_info
        (etype, value, tb) = exc_info()
        print '%s: %s' % (etype.__name__, value)

        patmatch = patternMatcher()
        patmatch.templates_file = templates_file

    return patmatch

def loadProcessor(name):
    if name:
        name = name.split('.')
        if len(name) == 1:
            return globals().get(name[0])

        try: module = __import__('.'.join(name[:-1]), globals(), locals(), [''])
        except ImportError: pass
        else: return getattr(module, name[-1], None)

def ignoreMatch(*args):
    pass

## Scripted Main.
DEFAULT_PATTERNS = 'stuph-log-patterns.pkl'

def main(argv = None):
    # Parse command line.
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--database', '--db')
    parser.add_option('-g', '--debug', action = 'store_true')
    parser.add_option('-i', '--input-file', '--source')
    parser.add_option('-s', '--show-patterns', action = 'store_true')
    parser.add_option('-p', '--processor')
    parser.add_option('-x', '--export')
    parser.add_option('--import')
    (options, args) = parser.parse_args()

    if options.input_file:
        source = open(options.input_file)
    elif args:
        assert len(args) == 1
        source = open(args[0])

    templates_file = options.database or DEFAULT_PATTERNS

    if options.debug:
        from pdb import set_trace
        set_trace()

    # Load the pattern matcher.
    patmatch = loadPatternMatcher(templates_file)
    if options.export:
        patmatch.export(options.export)
    else:
        processMatch = loadProcessor(options.processor)

        # Interact.
        if options.show_patterns:
            for pattern in patmatch.patterns:
                print pattern.pattern
        else:
            patmatch.interactive(source, processMatch)

if __name__ == '__main__':
    main()

USAGE = \
'''
This subcommand will compare a collection of syslogs against a category
of patterns (use --show=all or --show=static|compiled to get a list of
categories).

Use --show-paths to see a list of paths that the scanner searches, and
--category=<category seen with --show> to do the actual search.
'''

from optparse import OptionParser
syslogCommandParser = OptionParser(USAGE)
syslogCommandParser.add_option('-c', '--category')
syslogCommandParser.add_option('-s', '--show-categories', '--show')
syslogCommandParser.add_option('--show-paths', action = 'store_true')

def parseScanSyslogCmdln(args):
    from mud.tools import parseOptionsOverSystem
    return parseOptionsOverSystem(syslogCommandParser, args)

def getScanSyslogPaths(section):
    from glob import glob

    import re
    pathpat = re.compile('path(?:\.(\d+))?').match

    for opt in section.options():
        if pathpat(opt):
            for p in glob(section.get(opt)):
                yield p

# These should be: complex and basic
KNOWN_PATTERN_TYPES = ['Compiled', 'Static']
MINIMUM_LEVEL = 115
def doScanSyslog(peer, cmd, argstr):
    # todo: caching of patterns object, syslogs (pre-match index)
    # to disk.. reloaded via md5 checksum change detection.
    args = argstr.split() if argstr else []
    if not args or args[0].lower() != 'scan':
        return False

    del args[0]
    if peer.avatar and peer.avatar.level >= MINIMUM_LEVEL:
        try:
            (options, args) = parseScanSyslogCmdln(args)

            from mud import getSection
            section = getSection('Syslog')

            syslog_paths = getScanSyslogPaths(section)
            patterns = section.get('patterns')

            if options.show_paths:
                def showPaths():
                    yield '&ySyslog Paths:&N'
                    yield '============='
                    yield ''

                    for path in syslog_paths:
                        yield path

                peer.page_string('\n'.join(showPaths()) + '\n')
                raise SystemExit

            if not patterns:
                print >> peer, 'Not syslog patterns defined!'
                raise SystemExit

            # Load appropriate pattern category:
            # todo: actually provide categorical combinations.
            from ConfigParser import ConfigParser, NoOptionError, NoSectionError
            cfg = ConfigParser()
            cfg.readfp(open(patterns), patterns)

            show = options.show_categories
            if show:
                # todo: wildcard--search patterns themselves!
                show = show.lower()

                def showSections():
                    yield '&ySyslog Categories:&N'
                    yield '=================='
                    yield ''

                    for section in cfg.sections():
                        if section not in KNOWN_PATTERN_TYPES:
                            continue

                        lsection = section.lower()
                        if show in ['any', 'all'] or show == lsection:
                            yield str(section)
                            for opt in cfg.options(section):
                                yield '  [%-5s] %s' % (opt, cfg.get(section, opt))

                            yield ''

                peer.page_string('\n'.join(showSections()) + '\n')
                raise SystemExit

            if not options.category:
                print >> peer, 'Category is required.'
                print >> peer

                parseScanSyslogCmdln(['-h'])
                raise SystemExit

            # Check aliases, first:
            category_id = options.category
            try: category_id = cfg.get('Aliases', category_id)
            except (NoOptionError, NoSectionError): pass

            for type in KNOWN_PATTERN_TYPES:
                try: pattern = cfg.get(type, category_id)
                except (NoOptionError, NoSectionError): pass
                else:
                    if type == 'Compiled':
                        category = compile_pattern(pattern)
                    elif type == 'Static':
                        category = static_pattern(pattern)

                    # Get presentation format.
                    try: category_header = cfg.get('Presentation', '%s.header' % category_id, raw = True)
                    except (NoOptionError, NoSectionError): category_header = None

                    try: category_format = cfg.get('Presentation', '%s.format' % category_id, raw = True)
                    except (NoOptionError, NoSectionError): category_format = None

                    break
            else:
                print >> peer, 'Unknown category: %r' % category_id
                raise SystemExit

            # Do processing.
            def scanSyslog():
                yield '&ySyslog Contents:&N'
                yield '================'
                yield str(category)
                yield ''

                for path in syslog_paths:
                    try: stream = open(path)
                    except IOError:
                        # todo: test for non (is-directory or enoent)
                        continue

                    first_in_file = True
                    linenr = 0
                    for line in stream:
                        linenr += 1

                        # XXX Careful:
                        line = line.rstrip()
                        line = line[28:]
                        match = category.match(line)

                        if match is True:
                            if first_in_file:
                                yield '%s:' % path
                                first_in_file = False

                            yield '  %-5d: %s' % (linenr, line)

                        elif match not in (False, None):
                            if first_in_file:
                                yield '%s:' % path
                                if category_header:
                                    yield '         %s' % category_header
                                    yield '         %s' % ('-' * len(category_header))

                                first_in_file = False

                            groups = match.groupdict()
                            if not groups:
                                groups = match.groups()

                            if category_format:
                                yield '  %-5d: %s' % (linenr, category_format % groups)
                            else:
                                yield '  %-5d: %s' % (linenr, groups)

                    if not first_in_file:
                        yield ''

            # In another thread (how might this affection the active syslog??)
            def process(page_string):
                from mud import enqueueHeartbeatTask
                enqueueHeartbeatTask(page_string, '\r\n'.join(scanSyslog()))

            from thread import start_new_thread as nth
            nth(process, (peer.page_string,))

        except SystemExit:
            pass

        return True

try: from mud.player import ACMD
except ImportError: pass
else: ACMD('syslog*')(doScanSyslog)

try: from mud.runtime.registry import registerObject
except ImportError: pass
else:
    class API:
        getScanSyslogPaths = staticmethod(getScanSyslogPaths)

        KNOWN_PATTERN_TYPES = property(lambda self:KNOWN_PATTERN_TYPES)
        compile_pattern = property(lambda self:compile_pattern)
        static_pattern = property(lambda self:static_pattern)

    # Singleton.
    API = API()

    SYSLOG_SCANNER_OBJECT_NAME = 'Syslog::Scanner::API'
    registerObject(SYSLOG_SCANNER_OBJECT_NAME, API)
