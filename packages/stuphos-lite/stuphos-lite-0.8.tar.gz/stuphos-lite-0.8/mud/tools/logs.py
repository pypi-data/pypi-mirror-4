# Error and Informational Logging Routines.
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
# These are loaded into runtime.core module.
from . import getSystemException, getModuleFileBasename
from traceback import extract_tb

__all__ = ['log', 'logWarning', 'logError', 'logException', 'logWizards']

def log(*args, **kwd):
    global log
    from game import syslog
    log = syslog # Rewrite.
    syslog(*args, **kwd)

def logWarning(message):
    log('Warning: %s' % message)
def logError(message):
    log('Error: %s' % message)

LOGINDENT = ' ' * 27
PADINDENT = ' ' * 2
FULLINDENT = LOGINDENT + PADINDENT
FULLINDENT2 = FULLINDENT + ' ' * 2

def logException(etype = None, value = None, tb = None, traceback = False):
    # Construct a traceback suitable for logging to syslog file.
    # Todo: serialize the exception data to another file.
    if etype is None and value is None and tb is None:
        (etype, value, tb) = getSystemException()

    if traceback:
        def _():
            for (file, lineno, name, source) in extract_tb(tb):
                file = getModuleFileBasename(file)
                yield '%s[%s:%d] %s' % (FULLINDENT, file, lineno, name)
                if source:
                    yield '%s%s' % (FULLINDENT2, source.strip())

        log('%s: %s\n%s' % (etype.__name__, value, '\n'.join(_())))
    else:
        log('%s: %s' % (etype.__name__, value))

DEFAULT_WIZLOG_LEVEL = 115
DEFAULT_WIZLOG_TYPE = 'Complete'

def logWizards(message, level = None, type = DEFAULT_WIZLOG_TYPE, tofile = False):
    if level is None:
        level = DEFAULT_WIZLOG_LEVEL

    elif not isinstance(level, int):
        from world import mobile
        if isinstance(level, mobile):
            level = mobile.level
        else:
            raise TypeError(type(level).__name__)

    from game.system import mudlog
    mudlog(message, level, type)

    if tofile:
        from game import syslog
        syslog(message)

wizlog = logWizards
