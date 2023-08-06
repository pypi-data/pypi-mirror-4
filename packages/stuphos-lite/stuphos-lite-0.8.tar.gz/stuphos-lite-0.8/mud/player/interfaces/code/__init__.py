# Player Interpreter -- Code Evaluators Stack.
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
#
from mud.tools import columnize, checkLineCache
from mud.runtime import Object, LookupObject as LookupFactoryClass
from mud.runtime import LookupObject as LookupProgrammeManagerObject
from mud.player import isFromSecureHost
from mud.tools import parseOptionsOverSystem

# Record compiled statements to file so that tracebacks can look up the source code.
USE_RECORD_COMPILER = True
from os import unlink as delete_file
from optparse import OptionParser

class CodeManager:
    # This kind of functionality could every well just go into CommandManager
    def __init__(self, *evaluators):
        self.evaluators = list(evaluators)

    def pushEvaluator(self, e):
        self.evaluators.append(e)
    def popEvaluator(self):
        return self.evaluators.pop()

    def getCurrentEvaluator(self):
        try: return self.evaluators[-1]
        except IndexError: pass

    def evaluateStatement(self, peer, argstr):
        evaluate = self.getCurrentEvaluator()
        if evaluate is not None:
            return evaluate(self, peer, argstr)

    def getEvaluatorByManagerName(self, name):
        # First in reverse.
        v = self.evaluators
        i = len(v) - 1
        while i >= 0:
            e = v[i]
            if e.manager.getManagerName() == name:
                return e

            i -= 1

class Programme(Object):
    class Meta(Object.Meta):
        Attributes = Object.Meta.Attributes + ['manager', 'name', 'codeSource', 'owner']

    # Shelvable.
    def __init__(self, manager, name, sourceCode,
                 owner = None, codeSource = None,
                 documentation = ''):

        self.manager = manager
        self.name = name
        self.sourceCode = sourceCode
        self.owner = owner
        self.codeSource = codeSource
        self.documentation = documentation

    def __getstate__(self):
        # Basically, the manager instance 'goes away' when shelved.
        return dict(name = self.name, owner = self.owner,
                    codeSource = self.codeSource,
                    sourceCode = self.sourceCode,
                    documentation = self.documentation,
                    managerId = self.getManagerId())

    def getManagerId(self):
        # Called during serialization.
        try: return self.managerId
        except AttributeError:
            managerId = self.managerId = self.getManager().getManagerId()
            return managerId

    def getManager(self):
        try: return self.manager
        except AttributeError:
            # Called during invocation/deserialization.
            manager = self.manager = LookupProgrammeManagerObject(self.managerId)
            return manager

    def getShortName(self):
        return self.name
    def getDisplayForm(self):
        manager = self.getManager().getManagerName()

        doc = self.documentation
        if doc:
            doc = '\n  '.join(doc.split('\n'))
            return '[ %s: %s ]\n  %s\n\n%s' % (manager, self.name, doc, self.sourceCode)

        return '[ %s: %s ]\n\n%s' % (manager, self.name, self.sourceCode)

    def __str__(self):
        return self.sourceCode

    # ProgrammeManager Implementation.
    def invokeProgramme(self, shell, peer, **environ):
        # By default, ProgrammeManagers need to define compileSourceCodeBlock and executeCode.
        manager = self.getManager()
        code = manager.compileSourceCodeBlock(peer, self.sourceCode)
        manager.executeCode(shell, peer, code, **environ)

# How to make programs notebook-based?  Well, it's keyed on avatar.programs object (which should
# look like a shelf, so technically compatability already exists.  Of course, most other notebooks
# are only open long enough to do one operation.)
class ProgrammeManager: # (mud.player.notebook.Notebook.Model)
    # Shelving.
    def getPlayerProgrammes(self, peer):
        try: return peer.avatar.programs
        except AttributeError:
            pass

    def getManagerName(self):
        return '--'
    def getManagerId(self):
        raise NotImplementedError

    def formatSourceCode(self, source):
        return source.replace('\r', '')

    ProgrammeClass = Programme

    def buildProgramme(self, peer, name, source):
        # Override this.
        return self.ProgrammeClass(self, name, self.formatSourceCode(source))
                                   # owner = peer

    def loadProgramme(self, peer, name):
        'Load a program off avatar using dictionary mapping.'

        try: return self.getPlayerProgrammes(peer)[name]
        except (TypeError, KeyError):
            pass

        return ''

    def saveProgramme(self, peer, name, source):
        'Save a program onto avatar using dictionary mapping.'

        programs = self.getPlayerProgrammes(peer)
        if programs is not None:
            try:
                programs[name] = source
                programs.sync()

            except (TypeError, AttributeError):
                pass

    def showProgrammes(self, peer, args):
        'Show programmes available through avatar.'

        programs = self.getPlayerProgrammes(peer)
        if programs is not None:
            if args:
                name = ' '.join(args)

                try: p = programs[name]
                except (TypeError, KeyError): pass
                else:
                    if isinstance(p, Programme):
                        p = p.getDisplayForm()
                    else:
                        p = str(p)

                    peer.page_string(p)
            else:
                programs = programs.items()
                if programs:
                    def getProgramDescriptions():
                        for (name, p) in programs:
                            if isinstance(p, Programme):
                                yield p.getShortName()
                            else:
                                yield str(name)

                    peer.page_string('&yPrograms&N\r\n&r========&N\r\n%s\r\n' % \
                                     columnize(getProgramDescriptions(), 2, 20))
                else:
                    print >> peer, 'You have no programs.'

    def deleteProgramme(self, peer, name):
        'Delete programme, as named, available through avatar.'

        if name:
            programs = self.getPlayerProgrammes(peer)
            if programs is not None:
                try:
                    del programs[name]
                    programs.sync()

                except (TypeError, KeyError): pass
                else:
                    return True

class EvaluationShell:
    # Utilities for managing and executing code.
    def __init__(self, manager):
        self.manager = manager

    def executeSourceCode(self, shell, peer, argstr):
        # argstr = delete_doubledollar(argstr)

        if self.isCodeBlock(argstr):
            self.executeCodeBlock(shell, peer, argstr[0], argstr[1:])
        else:
            self.executeSingleStatement(shell, peer, argstr)

        return True

    def isCodeBlock(self, argstr):
        # todo: something cooler like:
        # ;trigger=enter-game
        # ;trigger+=enter-game
        # ;!trigger:enter-game

        return argstr[0] in '=+;!'

    def executeDirective(self, peer, args):
        # Directive mode.
        larg = args[0].lower() if args else ''

        if larg in ('list', 'show'):
            self.manager.showProgrammes(peer, args[1:])
            return True

        elif larg == 'delete':
            name = ' '.join(args[1:])
            if self.manager.deleteProgramme(peer, name):
                print >> peer, '%r deleted.' % name

            return True

        elif args:
            print >> peer, 'Unknown code block directive: %r' % ' '.join(args)
            return True

    PROGRAMMING_HEADER = '[ %s ] &B*&N ---------------               --------------- &B*&N [ Edit ]'

    def startEditingCodeBlock(self, shell, peer, block, name = '', initialSource = ''):
        # Dispatch the programmed code block by deferring evaluation and entering string-edit.
        def dispatchProgramWithPeerHead(peer, source):
            # Cleanup.
            try: del peer.messenger
            except AttributeError:
                pass # peer.messenger = None

            return shell.withPeerHead(peer, block, source)

        # Start editing.
        peer.messenger = dispatchProgramWithPeerHead
        peer.editString(initialSource)

        # Complete the line in case the peer is in compact mode.
        name = (name and name.upper() or 'Program')
        print >> peer, self.PROGRAMMING_HEADER % name # ,

    def parseProgramName(self, argstr):
        parts = argstr.split(' ', 1)
        if len(parts) == 2:
            return parts
        elif len(parts) == 1:
            return (parts[0], '')
        return ('', '')

    def executeCodeBlock(self, shell, peer, mode, argstr):
        # Handle code block mode.
        if mode == ';':
            if not self.executeDirective(peer, argstr.split()):
                # Basic batch compile and execute (with existing source).
                def CompileAndExecute(peer, source):
                    # Direct compile and execute.
                    source = self.manager.formatSourceCode(source)
                    self.executeCode(shell, peer, self.compileSourceCodeBlock(peer, source))

                self.startEditingCodeBlock(shell, peer, CompileAndExecute)

        elif mode == '=':
            # Edit and save programme, replacing old.
            (name, rest) = self.parseProgramName(argstr)
            if not name:
                print >> peer, 'A programme name is required.'
            else:
                def StoreProgramme(peer, source):
                    # (should be passing this shell)
                    programme = self.manager.buildProgramme(peer, name, source)
                    self.manager.saveProgramme(peer, name, programme)

                self.startEditingCodeBlock(shell, peer, StoreProgramme, name = name)

        elif mode == '+':
            # Load, edit and save existing programme.
            (name, rest) = self.parseProgramName(argstr)
            if not name:
                print >> peer, 'A programme name is required.'
            else:
                programme = self.manager.loadProgramme(peer, name)
                if isinstance(programme, Programme):
                    initialSource = programme.sourceCode
                elif isinstance(programme, basestring):
                    initialSource = programme
                else:
                    initialSource = ''

                def StoreProgramme(peer, source):
                    # (should be passing this shell)
                    programme = self.manager.buildProgramme(peer, name, source)
                    self.manager.saveProgramme(peer, name, programme)

                self.startEditingCodeBlock(shell, peer, StoreProgramme, name = name,
                                           initialSource = initialSource)

        elif mode == '!':
            # Load programme.
            (name, rest) = self.parseProgramName(argstr)
            if not name:
                print >> peer, 'A programme name is required.'
            else:
                # Execute right now.
                programme = self.manager.loadProgramme(peer, name)
                if isinstance(programme, Programme):
                    programme.invokeProgramme(shell, peer, argstr = rest)
                elif isinstance(programme, basestring):
                    code = self.compileSourceCodeBlock(peer, programme)
                    self.executeCode(shell, peer, code, argstr = rest)

    def executeSingleStatement(self, shell, peer, source):
        self.executeCode(shell, peer, self.compileSingleStatement(peer, source))

    # Abstractions.
    ##    def executeCode(self, shell, peer, code): pass
    ##    def executeSingleStatement(self, shell, peer, source): pass
    ##    def compileSourceCodeBlock(self, peer, source): pass
    ##    def compileSingleStatement(self, peer, sourceCode, type = 'single', ext = ''): pass

# Todo: move this kind of thing into mud.tools?
class TemporaryCodeFile:
    'As context -- Compile to temporary file and return the code.  Delete on exit.'

    def __init__(self, peer, sourceCode, ext = '', shellName = '-'):
        self.peer = peer
        self.sourceCode = sourceCode
        self.ext = ext
        self.shellName = shellName

    def shouldUse(self):
        return getattr(self.peer, 'recordCompiler', USE_RECORD_COMPILER)

    def __enter__(self):
        if self.shouldUse():
            try:
                # Build file name -- this should go in plrfiles.
                peer = self.peer
                filename = 'etc/code/%s@%s%s' %      \
                        (peer.avatar.name            \
                           if (peer.avatar and       \
                               peer.avatar.isPlayer) \
                           else '-', self.shellName, self.ext)

                # Do this first.
                checkLineCache(filename)

                # Write to file.
                fl = open(filename, 'wt')
                fl.write(self.sourceCode)
                fl.close()

            except:
                pass
            else:
                self.filename = filename

        return self

    def __exit__(self, etype = None, value = None, tb = None):
        try: delete_file(self.filename)
        except AttributeError:
            pass

# Factory routines.
class ShellFactoryBase(object):
    @classmethod
    def parseArgs(self, args):
        try: parser = self.__parser
        except AttributeError:
            try: options = self.OPTIONS
            except AttributeError: parser = None
            else:
                parser = self.__parser = OptionParser()
                for (opt_args, opt_kwd) in options:
                    parser.add_option(*opt_args, **opt_kwd)

        if parser is not None:
            try: (options, args) = parseOptionsOverSystem(parser, list(args))
            except SystemExit: return
            else: return options.__dict__

        return dict()

from python import getPythonCodeEvaluator
try: from girl import getGirlCodeEvaluator
except ImportError, e:
    print e

def makeCodeEvaluators(*args, **kwd):
    return [getPythonCodeEvaluator(*args, **kwd)]

# Todo: Initialize this from MUDConf.
SHELL_FACTORIES = dict(girl = 'mud.player.interfaces.code.girl.GirlCodeEvaluatorFactory',
                       python = 'mud.player.interfaces.code.python.PythonCodeEvaluatorFactory')

def findShellFactory(name):
    try: cls = SHELL_FACTORIES[name]
    except KeyError: pass
    else: return LookupFactoryClass(cls)

def doManageShellEvaluators(peer, action, name = None, *args):
    if action == 'open':
        factory = findShellFactory(name)
        if factory is None:
            print >> peer, 'Unknown shell: %r' % name
        else:
            options = factory.parseArgs(args)
            if isinstance(options, dict):
                # Open a shell context.
                try: pushEv = peer.interpreter.pushEvaluator
                except AttributeError:
                    print >> peer, 'Your shell interpreter does not support new evaluators.'
                else:
                    pushEv(factory(peer, **options))

    elif action == 'close':
        # Close this shell context.
        try: popEv = peer.interpreter.popEvaluator
        except AttributeError:
            print >> peer, 'Your shell interpreter does not support evaluators.'
        else:
            manager = peer.interpreter.getCurrentEvaluator().manager
            print >> peer, 'Closing Program: %s.' % manager.getManagerName()
            popEv()

    elif action == 'show':
        try: evaluators = peer.interpreter.evaluators
        except AttributeError:
            print >> peer, 'Your shell interpreter does not support evaluators.'
        else:
            peer.page('\n'.join(map(repr, evaluators)) + '\n')
