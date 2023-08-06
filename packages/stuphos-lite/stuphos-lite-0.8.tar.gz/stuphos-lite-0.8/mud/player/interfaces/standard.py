# Standard implementation of Command Manager.
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
__all__ = ['StandardCommandManager']

import mud

from mud.player.interfaces import CommandCenter
from mud.tools import getLineFromCache, functionLines, functionName

SYSLOG_FILE = '../log/syslog'
def readSyslog():
    from os import getenv
    file = getenv('STUPH_LOGFILE', SYSLOG_FILE)
    return filterSyslog(open(file).read())

def filterSyslog(text):
    return text.replace('\x00', '').replace('\n', '\r\n')

##  try: from mud.tools import functionLines, functionName
##  except ImportError:
##      def notimpl(*args, **kwd):
##          raise NotImplementedError
##
##      functionLines = functionName = notimpl

def listCommands(commands):
    # Generates two-column lines.
    commandMap = dict()
    for v in commands.values():
        commandMap[v] = list()

    # Collect names for each function -- Inversion.
    for (k, v) in commands.iteritems():
        commandMap[v].append(k)

    # Go through each function, generating a listing for all the names and descr of func.
    for (func, names) in commandMap.iteritems():
        doc = func.__doc__ or ''
        if doc:
            doc = doc.replace('\n', '')

        # yield functionName(func), doc
        yield func.__name__, doc

        # Zip side-by-sides.
        names.sort() # Alphabetically
        desc = map(str, functionLines(func, max = len(names), trim_decorators = True))

        for (a, b) in sideBySide(names, desc):
            yield '    ' + a, b

    # Generate empty line.
    yield ('', '')

def sideBySide(a, b):
    '(unzip list-first-column list-second-column)'

    la = len(a)
    lb = len(b)

    for x in xrange(la):
        # Python 2.6 syntax capability:
        # i = a[x] if x < la else ''
        # j = b[x] if x < lb else ''
        if x < la:
            i = a[x]
        else:
            i = ''

        if x < lb:
            j = b[x]
        else:
            j = ''

        yield i, j

class StandardCommands(CommandCenter):
    'Some sample standard commands provided here.'
    # Only compatible with a CmdDict multiple-inheritance.

    # @MininumLevel(LVL_IMPL)
    # @Qualifier(lambda peer, *args:peer.avatar and peer.avatar.implementor)
    @staticmethod
    def doPageSyslog(peer, cmd, argstr):
        'Page the ENTIRE SYSLOG!!'

        if peer.avatar and peer.avatar.implementor:
            peer.page(readSyslog())
            return True

    @staticmethod
    def doShowBridgedEvents(peer, cmd, argstr):
        'Display aspects on bridged mud events.'

        if peer.avatar and peer.avatar.implementor:
            import mud.bridge, game

            mud.bridge.showBridgedEvents(game.bridgeModule(), page = peer.page, endline = '\r\n')
            return True

    @staticmethod
    def doShowHeartbeatTasks(peer, cmd, argstr):
        'Show heartbeat tasks.'

        if peer.avatar and peer.avatar.implementor:
            from mud import tasks
            tasks.show(peer.page)
            return True

    @staticmethod
    def doReloadInterpreter(peer, cmd, argstr):
        'Reload the player module, all the interpretation, and re-interpret player.'

        if peer.avatar and peer.avatar.implementor:
            import mud.player
            reload(mud.player).interpret(peer)
            return True

    def doShowCommands(self, peer, cmd, argstr):
        'Displays command listing of this object.'

        # Generate lines to be printed side-by-side with names.
        width = 30, 80
        fmt   = '%%-%(left)d.%(left)ds %%-%(right)d.%(right)ds' % {'left':width[0], 'right':width[1]}

        peer.page('\r\n'.join(fmt % line for line in listCommands(self.c)) + '\r\n')
        return True

    def doCassiusConnection(self, peer, cmd, argstr):
        if peer.avatar and peer.avatar.supreme:
            cas = self.openCassius()

            # Python 2.6 syntax capability:
            # argstr = argstr.strip() if argstr else ''
            argstr = argstr and argstr.strip() or ''

            if argstr == 'close':
                # Delete installation known to mud, and our cas builtin.
                del builtin.cassius_connection, builtin.cas

                print >> peer, '&D >&N', cas, 'Deleted!'
                return True

            if argstr == 'reopen':
                del builtin.cassius_connection, builtin.cas

                # Re-open and fall thru...
                # reload(telnet)
                cas = self.openCassius()

            elif argstr == 'bind':
                cas.adapters.add(telnet.bind(peer))

                print >> peer, 'Okay.'
                return True

            elif argstr == 'unbind':
                print >> peer, 'No idea how to do that!'
                return True

            elif argstr:
                # Send to connection.
                cas.sendline(argstr)

                print >> peer, '&D >&N', argstr
                return True

            print >> peer, cas
            return True

        # Not supreme, not allowed!

    def doMainMenu(self, peer, cmd, argstr):
            mainMenu = mud.player.namespace.getGlobals().get('Menu')
            if not mainMenu:
                    from fraun.menu import Main as mainMenu

            
            return True

    def setup(self):
        # CommandSetup.setup(self)
        a = self.insertOverridingAll

        a('page-*syslog',          self.doPageSyslog        )
        a('show-br*idged-events',  self.doShowBridgedEvents )
        a('show-t*asks',           self.doShowHeartbeatTasks)
        a('reload-*interpreter',   self.doReloadInterpreter )
        a('interpret*',            self.doReloadInterpreter )
        a('show-comm*ands',        self.doShowCommands      )
        a('main*-menu',            self.doMainMenu          )

# Export this:
##  class StandardCommandManager(CommandManager):
##      'Implements a command manager (abbreviation-managed command dictionary) with standard commands.'
##
##      def setup(self):
##          StandardCommandMixin.setup(self)
##
##          try:
##              # self.importCommands('commands')
##              self.importCommands('mud.player.interfaces.commands')
##
##          except ImportError:
##              pass
##
##      def __init__(self, *args, **kwd):
##          CommandManager.__init__(self, *args, **kwd)
