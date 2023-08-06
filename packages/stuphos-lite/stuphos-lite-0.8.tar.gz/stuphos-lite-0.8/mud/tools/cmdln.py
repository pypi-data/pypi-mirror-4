# Command-Line Interface Routines
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
# (Used for subsystems.)
# Todo: merge in special command stuff.  Also, this should probably be migrated to mud.player.commands
#
import sys
import shlex

NoArgv = object()

def parseOptionsOverSystem(parser, args):
    # Must temporarily shift the given argv into system module so that optparse functions right.
    previous_argv = getattr(sys, 'argv', NoArgv)

    if isinstance(args, basestring):
        args = args.split()
    elif args is None:
        args = []
    else:
        args = list(args)

    sys.argv = [''] + args
    try: return parser.parse_args(args)
    finally:
        if previous_argv is NoArgv:
            del sys.argv
        else:
            sys.argv = previous_argv

def printOptionsWithPrognameOverSystem(parser, progname, fileObj = None):
    previous_argv = getattr(sys, 'argv', NoArgv)

    progname = str(progname)
    assert progname
    sys.argv = [progname]

    try: return parser.print_help(file = fileObj)
    finally:
        if previous_argv is NoArgv:
            del sys.argv
        else:
            sys.argv = previous_argv

# Why isn't this in tools?
def maxWidth(sequence, width):
    for n in sequence:
        n = len(n)
        if n > width:
            width = n

    return width

def getKeyword(kwd, name, default = None):
    try: value = kwd[name]
    except KeyError: return default
    else: del kwd[name]

    return value

def Option(*args, **kwd):
    # Returns a pair of argument aggregates suitable for passing as the
    # positional and keyword arguments to a function (add_option).
    return (args, kwd)

def createCmdlnParser(*options):
    from optparse import OptionParser
    parser = OptionParser()
    for (args, kwd) in options:
        parser.add_option(*args, **kwd)

    return parser

class Cmdln:
    def __init__(self, progName, *options, **kwd):
        self.progName = progName
        self.options = options
        self.parser = createCmdlnParser(*options)
        self.shlex = bool(kwd.get('shlex', False))

    class HelpExit(Exception):
        pass

    class Parsed:
        def __init__(self, cmdln, command, argstr, options, args):
            self.cmdln = cmdln
            self.command = command
            self.options = options
            self.args = args
            self.argstr = argstr

            self.nextArg = iter(self).next

        def __repr__(self):
            return 'Parsed-Command: %s [%s] %r' % \
                   (self.command, self.argstr, self.options)

        def help(self):
            return self.cmdln.help()

        @property
        def argstr_stripped(self):
            return self.argstr.strip() if self.argstr else ''

        def __iter__(self):
            for arg in self.args:
                yield arg

            while True:
                yield ''

        def __len__(self):
            return len(self.args)

        def halfChop(self, string = None):
            if string is None:
                string = self.argstr

            a = string.strip()
            i = a.find(' ')
            if i < 0:
                return (a, '')

            return (a[:i], a[i:].lstrip())

        def oneArg(self, string = None):
            return self.halfChop(self.argstr if string is None else string)[0]

    def parseCommand(self, cmd, argstr):
        if argstr:
            if self.shlex:
                argv = shlex.split(argstr)
            else:
                argv = argstr.split()
        else:
            argv = []

        return self.Parsed(self, cmd, argstr, *self.parseArgv(argv))

    def parseArgv(self, argv):
        try: return parseOptionsOverSystem(self.parser, argv)
        except SystemExit:
            raise self.HelpExit

    __call__ = parseArgv

    def help(self):
        from StringIO import StringIO
        buf = StringIO()

        printOptionsWithPrognameOverSystem(self.parser, self.progName, buf)
        return buf.getvalue()
