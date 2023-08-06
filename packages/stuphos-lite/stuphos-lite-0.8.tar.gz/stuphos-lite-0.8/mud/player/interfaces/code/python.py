# Python Code Shell Evaluator.
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
from mud.tools import getSystemException, Attributes
from mud.player import HandleCommandError, policy, getPlayerScope
from mud.player.interfaces.code import ShellFactoryBase
from . import ProgrammeManager, EvaluationShell, TemporaryCodeFile, isFromSecureHost

@Attributes.Dynamic
def Environment(player, name, **search):
    return player.find(name, **search)

class PythonCodeManager(ProgrammeManager):
    # ProgrammeManager:
    def getManagerName(self):
        return 'Python'
    def getManagerId(self):
        return '%s.%s.Instance' % (self.__class__.__module__, self.__class__.__name__)

    # Implementation.
    isFromSecureHost = staticmethod(isFromSecureHost)
    def isPythonAllowed(self, peer):
        # Connection must originate from this machine.
        if not self.isFromSecureHost(peer):
            return False

        avatar = peer.avatar
        if avatar:
            if avatar in policy:
                # Powerful.
                return True

            # This line allows all implementors to use python:
            return avatar.supreme

        return False

    PROLOG = 'from __future__ import with_statement\n'
    EPILOG = ''

    def getDefaultShellName(self):
        # (code source)
        return '?'

    def compileSourceCodeBlock(self, peer, sourceCode, shellName = None):
        # Remove-preceding whitespace.
        sourceCode = self.formatSourceCode(sourceCode.lstrip())
        sourceCode = ''.join((self.PROLOG, sourceCode, self.EPILOG))

        if shellName is None:
            shellName = self.getDefaultShellName()

        # Compile code from source.
        with TemporaryCodeFile(peer, sourceCode, shellName):
            return compile(sourceCode, shellName, 'exec')

    def compileSingleStatement(self, peer, sourceCode, shellName = None):
        if shellName is None:
            shellName = self.getDefaultShellName()

        sourceCode = self.formatSourceCode(sourceCode)
        with TemporaryCodeFile(peer, sourceCode):
            return compile(sourceCode, shellName, 'single')

    def executeCode(self, shell, peer, code, **environ):
        # Hack: inspect evaluator stack on CodeManager Shell.
        managerName = self.getManagerName()

        try: execute = shell.getEvaluatorByManagerName(managerName).executeCode
        except AttributeError: pass
        else: return execute(shell, peer, code, **environ)

class PythonCodeShell(EvaluationShell):
    # EvaluationShell:
    def executePython(self, shell, peer, argstr):
        if argstr and self.manager.isPythonAllowed(peer):
            return self.executeSourceCode(shell, peer, argstr)

    __call__ = executePython

    def executeCode(self, shell, peer, code, **environ):
        local = self.setupLocalNamespace(shell, peer, (None, None), **environ)

        ##    if getattr(self, 'debug', False):
        ##        debug_code(code, local)

        try: exec code in self.global_namespace, local
        except:
            # For now, show all how we got here.
            HandleCommandError(peer, getSystemException(), frame_skip = 0)

    # Implementation.
    thisName   = 'this' # avatar's peer
    myName     = 'me'   # peer's avatar
    myLocation = 'here' # avatar's room location

    shellName  = '<player>'

    def __init__(self, manager, scope):
        EvaluationShell.__init__(self, manager)
        self.scope = scope

        # I guess these are separately-configurable.
        self.local_namespace = scope.__dict__
        self.global_namespace = getMainNamespace(scope)

    def getShellName(self, peer):
        'Code Source (not source code).'

        self.compiler_name = shellName = getattr(peer, 'host', False) or self.shellName
        return shellName

    def compileSourceCodeBlock(self, peer, sourceCode):
        return self.manager.compileSourceCodeBlock(peer, sourceCode, self.getShellName(peer))
    def compileSingleStatement(self, peer, sourceCode):
        return self.manager.compileSingleStatement(peer, sourceCode, self.getShellName(peer))

    def setupLocalNamespace(self, shell, peer, (cmd, argstr), **environ):
        local = self.local_namespace
        avatar = peer.avatar

        local.update({
            self.thisName   : peer,
            self.myName     : avatar or peer.avatar,
            self.myLocation : avatar and avatar.room,

            # '__command__'   : cmd,
            # '__argstr__'    : argstr,

            'commands'      : shell.commands,
            'acmd'          : getattr(shell.commands, 'insert', None), # or just self.insert
            'history'       : shell.historyObject(peer),
            'last'          : lambda *args, **kwd:shell.historyLast(peer, *args, **kwd),

            'sh'            : shell,
            'run'           : shell.enqueueHeartbeatTask,
            'spawn'         : shell.spawnTask,
            'inline'        : mud.enqueueHeartbeatTask,

            'e'             : Environment(avatar),
            'g'             : Environment(avatar, mobile_in_world = True, item_in_world = True),

            # 'com'           : self.getCode,
        })

        local.update(environ)
        return local

# Infrastructure.
def getMainNamespace(scope):
    main = getModule()
    main.shell = scope
    main.main = main

    import mud, pdb
    main.mud = mud
    main.pdb = pdb

    import game, world
    main.game = game
    main.world = world

    import __builtin__ as builtin
    main.builtin = builtin

    import sys, os
    main.sys = sys
    main.os = os

    return main.__dict__

def getModule(name = '__main__'):
    # This should go in tools.

    try: main = __import__(name)
    except ImportError:
        main = new.module(name)
        from sys import modules
        modules[name] = main

    return main

# Singleton.
PythonCodeManager.Instance = PythonCodeManager()

def getPythonCodeEvaluator(scope):
    return PythonCodeShell(PythonCodeManager.Instance, scope)

class PythonCodeEvaluatorFactory(ShellFactoryBase):
    def __new__(self, peer):
        print >> peer, EvaluationShell.PROGRAMMING_HEADER % 'Python'
        return getPythonCodeEvaluator(getPlayerScope(peer))
