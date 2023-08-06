# Player Commands Package.
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
from mud.player import ACMD, ACMDLN, Option, getSharedScope
from .mime import loadMessageFile
import string

def installCommands():
    from mud.management.services import getEnablingSection
    isEnabled = getEnablingSection('Interpreter')

    if isEnabled('rich-editor'):
        import mud.player.editor
    if isEnabled('player-notebook'):
        import mud.player.notebook

    if isEnabled('wizard-gc'):
        from mud.player.commands.gc import wizard
    if isEnabled('checkpointing'):
        from mud.player.commands.gc import system
        system.EnableCheckpointing()

    loadFilesystemCommands()

def loadFilesystemCommands():
    from mud import getSection
    commands = getSection('VerbCommands')

    # Define commands from files in folder.
    for option in commands.options():
        if option.startswith('commands-folder'):
            folder = commands.get(option)
            for filename in listdir(folder):
                if filename.endswith('.mime'):
                    with open(filename) as message:
                        loadMessageFile(message)

# Todo: Runtime API.
class BuiltCommandError(SyntaxError):
    def __init__(self, syntax, declaration, tb):
        self.syntax = syntax
        self.declaration = declaration
        self.tb = tb

def programVerbCommand(verbCode, language, source, options = [],
                       minlevel = None, group = None,
                       shlex = None, decorators = []):

    assert language == 'python'

    # Format parameters and verb name.
    parameters = 'player, command'

    if '*' not in verbCode:
        verbCode += '*'

    # Make command registrator.
    register = ACMDLN(verbCode,
                      *(options or []),
                      **dict(shlex = shlex))

    # Decide function name holding command code.
    valid = string.lowercase + string.uppercase + string.digits

    def formatWord(w):
        # Strip invalid characters.
        w = ''.join(c for c in w if c in valid)
        return w[:1].upper() + w[1:].lower()

    functionName = verbCode.replace('_', '-').split('-')
    functionName = 'do%s' % ''.join(formatWord(w) for w in functionName)

    def buildCommand(functionName, parameters, statements):
        # Compile the command statements and return the function.
        statements = statements.replace('\r', '')
        declaration = 'def %s(%s):\n    %s\n' % \
                       (functionName, parameters,
                        '\n    '.join(statements.split('\n')))

        # Declare function symbol in locals, but bind it to a
        # shared global scope so it has access later.
        ns = dict()

        # scope = player.interpreter.scope.__dict__

        ##    from mud.player import getPlayerScope
        ##    scope = getPlayerScope(player).__dict__

        scope = getSharedScope().__dict__

        try: exec declaration in scope, ns
        except SyntaxError, syntax:
            from sys import exc_info
            (_, _, tb) = exc_info()
            raise BuiltCommandError(syntax, declaration, tb)

        return ns[functionName]

    # Perform build.
    function = buildCommand(functionName, parameters, source)

    # Wrap.
    for d in decorators:
        function = d(function)

    register(function)
    return function
