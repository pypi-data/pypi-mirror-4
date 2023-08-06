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
# from mud.zones.specials import Special, Register, Any
from mud.zones.specials import parseSpecialCommand
from mud.player import PlayerAlert
from . import isCommandReserved

from shlex import split as splitShellTokens

class NoOptions(dict):
    def __init__(self):
        self.__dict__ = self
    def __missing__(self, name):
        return False

# Formalization.
##    class SpecialProcedure:
##        # Interface (Abstract).
##        def doSpecial(self, actor, cmd, argstr):
##            SubsystemError('SpecialProcedure', NotImplementedError)
##        def __call__(self, *args, **kwd):
##            return self.doSpecial(*args, **kwd)

##    #@Special('Generic', Any)
##    def genericSpecial(this, actor, command, argstr):
##        pass
##
##    #@Register('Spacecraft::Telepad', Any)
##    class Telepad(Special):
##        room = 3001
##
##        def doLook(self, this, actor, *args):
##            pass

##    class Special(object):
##        def __new__(self, object, name = None, type = Any,
##                    room = None, mobile = None, item = None):
##
##            # Act as decorator, OR instance class.
##            pass
##
##        def __init__(self, name, type = Any):
##            self.name = name
##            self.type = type
##
##        def __lshift__(self, entity):
##            # Todo: validate entity type.
##            entity.special = self
##
##        # XXX lifecycle
##        ##    Assign = Assign
##        ##    Register = Register
##
##        def __call__(self, this, actor, command, argstr):
##            # generic processing:
##            # if isCommandReserved(command):
##            #     return self.periodic(this)
##            # method = getattr(self, 'do%s' % command.name.capitalize() None)
##            # if callable(method):
##            #     return method(This, actor, *argstr.split())
##
##            pass
##
##    class EnvironmentalCommandGrammar:
##        class ParsedCommand:
##            object = subject = directObject = indirectObject = \
##                     verb = preposition = None
##
##        def __init__(self, object):
##            pass
##        def parseCommand(self, args):
##            pass

class Special:
    # Generic base.
    SHLEX = False
    TARGET_SELF = False
    OPTIONS = []

    @classmethod
    def BindSpecial(self, entity, **values):
        # Default binder: if using the Special base class, we should be using an instance anyway.
        return self(**values)

    ##    @classmethod
    ##    def getEntityConfig(self, entity):
    ##        # Try to find a configuration for this entity and the special implementation.
    ##        # If loading from zones.core, then it's related to a zone module, which could
    ##        #   have information about where to find this config.
    ##        pass

    class Commands(dict):
        def Extend(self, **others):
            o = self.copy()
            o.update(others)
            return o

    COMMANDS = Commands()

    class ParsedCommand:
        @classmethod
        def Parse(self, cmd, argstr, shlex = False, options = None):
            if argstr is None:
                argstr = ''

            stripped = argstr.strip()
            if shlex:
                argv = splitShellTokens(argstr)
            else:
                argv = argstr.split()

            if options:
                # Todo: fold some of this into special base.
                # Hickenlooper
                from optparse import OptionParser
                parser = OptionParser()

                for (opt, kwd) in options:
                    parser.add_option(*opt, **kwd)

                (options, argv) = parser.parse_args(argv)
            else:
                options = NoOptions()

            return self(cmd, argstr, argv, stripped, options)

        def __init__(self, cmd, argstr, argv, stripped, options):
            self.command = cmd
            self.argstr = argstr
            self.args = argv
            self.stripped = stripped
            self.options = options
            self.next = iter(self).next

            # Presumably, these things don't change.
            self.first = self.first
            self.rest = self.rest

        def isPeriodic(self):
            return isCommandReserved(self.command)
        periodic = property(isPeriodic)

        @property
        def name(self):
            return self.command.name

        @property
        def first(self):
            return self.args[0] if self.args else None

        @property
        def trailing(self):
            (_, trailing) = parseSpecialCommand(self.argstr)
            return trailing

        @property
        def rest(self):
            return self.args[1:]

        @property
        def hasArguments(self):
            return bool(self.args)

        def __iter__(self):
            return iter(self.args)

    def parseCommand(self, cmd, argstr):
        return self.ParsedCommand.Parse(cmd, argstr, shlex = self.SHLEX)

    def findCommandAction(self, cmd, argstr):
        try: return getattr(self, self.COMMANDS[cmd.name])
        except KeyError: pass

    def __call__(self, actor, this, cmd, argstr):
        try:
            action = self.findCommandAction(cmd, argstr)
            if callable(action):
                parsed = self.parseCommand(cmd, argstr)
                if self.TARGET_SELF:
                    first = parsed.first
                    if not (first and actor.find(first) is this):
                        return False

                try:
                    if action(actor, this, parsed) is False:
                        return False

                except PlayerAlert, e:
                    if actor.peer:
                        e.deliver(actor.peer)

                return True
        except:
            from mud import logException
            logException(traceback = True)
