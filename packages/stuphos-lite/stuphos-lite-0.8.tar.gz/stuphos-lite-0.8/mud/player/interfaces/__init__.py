# MUD . Player . Interfaces
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
import mud
import dictcmd

class ACMD:
    Name = '?'
    def __init__(self, **kwd):
        self.__dict__.update(kwd)

class CommandCenter(dictcmd.CmdDict):
    # This can probably go away and just use CmdDict..?

    def __init__(self):
        dictcmd.CmdDict.__init__(self)
        self.setup()

    def setup(self):
        pass

    def importCommands(self, module):
        for proc in  __import__(module).__all__:
            if callable(proc) and hasattr(proc, 'ACMD'):
                self.insertAssignment(proc.ACMD.Name, proc)

def getCommandCenter(module):
    if not hasattr(module, 'SharedCommands'):
        from standard import StandardCommands
        module.SharedCommands = StandardCommands()
        module.ACMD = module.assignCommand = module.SharedCommands.assign

    return module.SharedCommands

# Python implementation of a command manager that can execute verbs out of a dictionary.
class CommandManager:
    def __init__(self, commands = None):
        self.commands = commands

    # Fraun Dec 21st 2005 Incorporation of CmdDict
    def playerCommand(self, peer, cmd, argstr):
        # Fraun Oct 1st 2006 - Only playing connections for commands!
        if peer.avatar:
            action = self.commands.lookup(cmd)
            if callable(action):
                try: return action(peer, cmd, argstr)
                except (mud.player.PlayerResponse, mud.player.DoNotHere), e:
                    print >> peer, e # e.message
                    return True

                except mud.player.PlayerAlert, e:
                    e.deliver(peer)
                    return True

    try: from world.commands import parseCommand
    except ImportError:
        def parseCommand(self, cmdln):
            return self.commands.parse(cmdln)

    def assignCommand(self, *args):
        return self.commands.insertOverridingAll(*args)

    def getCommands(self):
        return self.commands

from history import HistoryManager
from threading import ThreadingManager
from code import CodeManager, makeCodeEvaluators
