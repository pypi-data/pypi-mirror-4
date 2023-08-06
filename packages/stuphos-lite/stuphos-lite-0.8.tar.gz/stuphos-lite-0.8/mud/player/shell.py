# Player Interpreter.
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
from mud.player import HandleCommandError
from interfaces import *

# Todo: implement a prompt-response-handler queue.
class ShellI(CommandManager, HistoryManager, CodeManager, ThreadingManager):
    "Hot Command Interpreter [exit! to exit, ;%`<python statement>, ;%`'[<edit program name>]]"

    def __init__(self, commands, scope):
        CommandManager.__init__(self, commands)
        CodeManager.__init__(self, *makeCodeEvaluators(scope))

    def shellCommand(self, peer, line):
        # Fraun Dec 21st 2005 - New form
        cmd, argstr = self.parseCommand(line)
        if not cmd:
            return False

        # Fraun Sept 21st 2006 - History override.
        cmd, argstr = self.historyOverride(peer, cmd, argstr)
        if cmd is None:
            return True

        # Fraun Dec 21st 2005 - Incorporation of CmdDict
        if self.playerCommand(peer, cmd, argstr):
            return True

        # Parse regular command-names
        # XXX Why would this be allowed at this point...?
        ##    if cmd.lower() == 'exit!':
        ##        del peer.interpreter
        ##        return True

        # Fraun Nov 4th 2005 - Only do python if preceeded by ';'.  Do not trigger chat.
        if cmd == ';' or cmd == '`' or cmd == '%':
            # Fraun Sep 20th 2005 - Delegate
            return self.evaluateStatement(peer, argstr)

        return False

    def withPeerHeadAndException(self, peer, exception, procedure, *args, **kwd):
        '''
        Evaluate procedure while output is going to peer.  Send exceptions to peer.
        Not all exceptions, let those of kind <exception> through.
        '''
        import sys

        # Todo: better management of system state.
        STDOUT = sys.stdout
        STDERR = sys.stderr

        # stdout queues to peer output buffer
        sys.stdout = peer
        sys.stderr = peer

        # What about stdin?

        try:
            result = procedure(peer, *args, **kwd)
            sys.stdout = STDOUT
            sys.stderr = STDERR
            return result

        except:
            sys.stdout = STDOUT
            sys.stderr = STDERR

            (etype, value, tb) = sys.exc_info()
            if exception is not None and isinstance(value, exception):
                raise (etype, value, tb)

            return HandleCommandError(peer, (etype, value, tb))

    def withPeerHead(self, peer, procedure, *args, **kwd):
        return self.withPeerHeadAndException(peer, None, procedure, *args, **kwd)

    def __call__(self, peer, line):
        'Interpret player input line by executing it in this shell.'

        # If someone points their web browser at this port, redirect them.
        from mud.player import http
        if http.detectHttpRequest(peer, line):
            return

        # Synthesize Event
        if playerInput(peer, line):
            return

        # Invoke "CGI"
        return self.withPeerHead(peer, self.shellCommand, line)

        # try:
        #   with Head(peer):
        #       self.shellCommand(peer, line)
        # except:
        #   mud.player.HandleCommandError(peer, sys.exc_info())

    def __repr__(self):
        return "<Python Player Shell Interpreter>"

from time import time as now
def getDataRate(p):
    duration = float(now() - p.login_time)
    return (p.bandwidth_in / duration,
            p.bandwidth_out / duration)

from mud.runtime import eventResult
def makePrompt(peer):
    # This should go in mud.player again.
    if peer.state == 'Playing':
        makePrompt = getattr(peer, 'makePrompt', None)
        if callable(makePrompt):
            return eventResult(makePrompt())

        p = peer.prompt # Why would this return None?
        a = peer.avatar
        if a is not None:
            if a.hasMail:
                p = '(&wMail&N) %s' % p

            if False: # a.properties.display.prompt.flags.Bandwidth:
                p = '(&M%.1f&N:&m%.1f&N/s) %s' % (getDataRate(peer) + (p,))

        return eventResult(p)

class PromptFor:
    def __init__(self, peer, callback, message = None, write_mode = False,
                 compact_mode = True, timeout = None):

        # Todo: allow for interacting with ShellI and installing a sub-interpreter.
        # This allows the main player-shell to operate some of the lower-level features
        # like interpreted code while calling this prompting mechanism when needed.
        # (good for debugging the prompt)

        self.previous_interpreter = peer.interpreter
        self.callback = callback

        a = peer.avatar
        if a is not None:
            if write_mode:
                pf = a.playerflags
                self.previous_write_mode = pf.Writing
                pf.Writing = True
            else:
                self.previous_write_mode = None

            if compact_mode:
                pf = a.preferences
                self.previous_compact_mode = pf.Compact
                pf.Compact = True
            else:
                self.previous_compact_mode = None

        peer.interpreter = self

        self.message = message
        if message is not None:
            self.previous_make_prompt = getattr(peer, 'makePrompt', None)
            peer.makePrompt = (lambda:message)

    def regenerate(self, peer):
        self.__class__(peer, self.callback, message = self.message,
                       write_mode = self.previous_write_mode is not None)

    def __call__(self, peer, line):
        if self.previous_interpreter is None:
            del peer.interpreter
        else:
            peer.interpreter = self.previous_interpreter

        if self.previous_make_prompt is None:
            del peer.makePrompt
        else:
            peer.makePrompt = self.previous_make_prompt

        a = peer.avatar
        if a is not None:
            pwm = self.previous_write_mode
            if pwm is not None:
                a.playerflags.Writing = pwm

            pcm = self.previous_compact_mode
            if pcm is not None:
                a.preferences.Compact = pcm

        # Q: Catch exceptions?  Failure should still consume the action.
        # XXX Breaking backwards compatability: pass in this instance to the
        # callback (natural solution, keeps things current), otherwise, the
        # new PromptFor instance is completely separated from the controller.
        if self.callback(self, peer, line):
            self.regenerate(peer)

        return True

    def __repr__(self):
        return '<%s callback: %r, previous: %r>' % (self.__class__.__name__,
                                                    self.callback,
                                                    self.previous_interpreter)

def Prompting(peer, message, *args, **kwd):
    def makePromptResponse(function):
        PromptFor(peer, message = message, callback = function)
        return function

    return makePromptResponse


from mud.runtime import DeclareEvent
from mud import getBridgeModule

class playerInput(DeclareEvent):
    Module = getBridgeModule()
