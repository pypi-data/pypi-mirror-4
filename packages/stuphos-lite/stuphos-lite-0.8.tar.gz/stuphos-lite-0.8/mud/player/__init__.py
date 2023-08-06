# MUD Player Package.
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
from errno import ENOENT
from cPickle import load as load_pickle
from cPickle import dump as save_pickle
from types import GeneratorType as generator
import platform

from mud.tools import ShowFrame, HandleException, logException
from mud.tools import getSystemException, isYesValue
from mud.tools import capitalize as getCapitalizedName, stylizedHeader
from mud.tools.internet import IPAddressGroup

from mud import getConfig, invokeTimeoutForHeartbeat, getBridgeModule
from mud.runtime import eventResult, DeclareEvent
from mud.runtime.registry import getObject

from .events import TriggerPlayerEvent

#@on.newConnection
def interpret(peer):
    from mud.player.shell import ShellI
    peer.interpreter = ShellI(commands = getPlayerCommands(peer),
                              scope = getPlayerScope(peer))

    # Install peer.process_telnet_message
    # Install rich editString and messenger

# Greetings.
def getTitleScreen(peer):
    # Full title.
    title = getConfig('title-screen')
    if title:
        try: return open(title).read()
        except IOError, e:
            if e.args[0] != ENOENT:
                HandleException()

def getGreetings(peer):
    # Return the one-liner.
    greetings = getConfig('greetings')
    if greetings:
        greetings = greetings.strip()
        greetings = greetings.replace('%w', ' ')
        greetings = greetings.replace('%n', '\r\n')
        return greetings

def getTitleAndGreetings(peer):
    t = getTitleScreen(peer)
    g = getGreetings(peer)
    return (t + g) if (t and g) else t if t else g if g else ''

def getGreetingDelay(peer):
    try: return float(getConfig('greeting-delay'))
    except (ValueError, TypeError):
        return None

# mud.api.constants
CON_GET_NAME = 'Get name'

def greetPlayer(peer):
    greetings = getTitleAndGreetings(peer)
    if greetings:
        delay = getGreetingDelay(peer)
        if delay:
            def sendGreeting():
                try:
                    if peer.state == CON_GET_NAME:
                        peer.write(greetings)

                except ValueError:
                    # Peer handle no longer valid.
                    pass

            invokeTimeoutForHeartbeat(delay, sendGreeting)

        else:
            peer.write(greetings)

        return eventResult(True)

def welcomePlayer(peer):
    # New player -- Rename to welcomeNewPlayer?
    pass

class playerActivation(DeclareEvent):
    # An event that can be detached from enterGame.
    Module = getBridgeModule()

def enterGame(peer, player):
    # Prioritize activation handlers before triggered event.
    playerActivation(peer, player)

    ##    api = getObject('Web::Extension::API')
    ##    if api is not None:
    ##        player.properties = api.getProperties(player)

    TriggerPlayerEvent(player, 'enter-game')

# Rudimentary Access Policy.
TRUSTED_FILENAME = 'etc/trust.python'
class Trust(dict):
    def __init__(self, filename = TRUSTED_FILENAME):
        self.filename = filename
        self.loaded = False

    def load(self):
        try:
            self.update(load_pickle(open(self.filename)))
            self.loaded = True
        except IOError, e:
            from errno import ENOENT
            if e.errno != ENOENT:
                raise

    def save(self):
        save_pickle(self, open(self.filename, 'w'))

    def __contains__(self, avatar):
        not self.loaded and self.load()
        return avatar.idnum == self.get(avatar.name)

    def __iadd__(self, avatar):
        self[avatar.name] = avatar.idnum
        self.save()
        return self

policy = Trust()

# Host Security.
SECURE_DOMAINS = None

def getSecureDomains(reload = False):
    global SECURE_DOMAINS
    if SECURE_DOMAINS is None or reload:
        from mud import getSection
        securityCfg = getSection('Security')

        # Some builtin domains.
        domains = []
        if isYesValue(securityCfg.get('trust-localhost')):
            # IPv6? Hah!
            try: domains.append(platform.node().lower())
            except: logException(traceback = True)

            domains.append('localhost')
            domains.append('127.0.0.1')

        # Build from config.
        for option in securityCfg.options():
            if option == 'trusted-domain' or \
               option.startswith('trusted-domain.'):
                domains.append(securityCfg.get(option).lower())

        domains = filter(None, set(domains))
        SECURE_DOMAINS = IPAddressGroup(*domains)

    return SECURE_DOMAINS

def isSecureDomain(domainName):
    return domainName.lower() in getSecureDomains()
def isFromSecureHost(peer):
    return isSecureDomain(peer.host)

# Communication Constructs.
class PlayerResponse(Exception):
    pass
class DoNotHere(Exception):
    pass

class PlayerAlert(PlayerResponse):
    def __init__(self, alert):
        self.alert = alert
    def deliver(self, peer):
        # Todo: call customized handler.
        print >> peer, self.alert

def playerAlert(fmt, *args):
    raise PlayerAlert(fmt % args)

def HandleCommandError(peer, exc = None, full_traceback = True, error_color = 'r', frame_skip = 1):
    if exc is None:
        exc = getSystemException()

    # First, Cascade to MUD.
    HandleException(exc = exc)

    # Then, send to player.
    name = getattr(exc[0], '__name__', '<Unnamed>')
    tb = exc[2]

    # Skip forward frames as long as possible.
    while frame_skip > 0 and tb.tb_next:
        tb = tb.tb_next
        frame_skip -= 1

    # Find (second to?) last frame.
    while tb.tb_next:
        if full_traceback and tb.tb_next:
            print >> peer, ShowFrame(tb.tb_frame, name)

        tb = tb.tb_next

    print >> peer, '&%s%s&N' % (error_color, ShowFrame(tb.tb_frame, name, exc))

    # Whether or not command error was handled -- which it was.
    return True

# Interactive Organization.
def getPlayerCommands(peer):
    return getSharedCommands()

def getPlayerScope(peer):
    ##    if hasattr(peer, 'namespace'):
    ##        return peer.namespace
    ##    if peer.avatar and hasattr(peer.avatar, 'namespace'):
    ##        return peer.avatar.namespace

    return getSharedScope()

def getSharedCommands():
    from mud.player.interfaces import getCommandCenter
    return getCommandCenter(getSharedScope())

def getSharedScope():
    if 'namespace' not in globals():
        global namespace
        import new

        namespace = new.module('mud.player.namespace')

    return namespace

# Gross -- Scope before Commands?  Decoupled.
# This should just be put in mud.player.interfaces
# (at least i _think_ it's that simple)
shared = getSharedCommands()
ACMD = shared.assign

from mud.tools.cmdln import Cmdln, Option
def ACMDLN(verbName, *options, **kwd):
    cmdln = Cmdln(verbName, *options, **kwd)
    if '*' not in verbName:
        verbName += '*'

    def makeCommandHandler(function):
        @ACMD(verbName)
        def doCommand(peer, cmd, argstr):
            try: parsed = cmdln.parseCommand(cmd, argstr)
            except cmdln.HelpExit: return True
            else:
                result = function(peer, parsed)
                if isinstance(result, generator):
                    peer.page('\n'.join(result) + '\n')
                    return True

                return bool(result)

        return doCommand
    return makeCommandHandler

def Showing(peer, caption = None, none = None):
    # Use as decorator to generate a paged-string from content and optional caption.
    # Optional 'none' argument shows this as string if no results were obtained.
    def showResults(results):
        def s():
            if caption:
                yield stylizedHeader(caption)

            for r in view():
                yield r

            yield ''

        peer.page('\r\n'.join(s()))

    if none:
        def showOrNone(view):
            results = list(view())
            if results:
                showResults(results)
            else:
                print >> peer, none

            return view

        return showOrNone

    def show(view):
        showResults(view())
        return view

    return show
