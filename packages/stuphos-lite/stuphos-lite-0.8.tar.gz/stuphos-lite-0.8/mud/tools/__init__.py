# MUD Tools.
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

# Tool Primitives.
def registerBuiltin(object, name = None):
    if name is None:
        name = object.__name__

    __builtins__[name] = object

def asBuiltin(function):
    registerBuiltin(function)
    return function

registerBuiltin(asBuiltin)


# System Tools.
import types

from os.path import basename, join as joinpath, dirname, normpath, abspath, splitext
from time import time as getCurrentSystemTime

import linecache
from linecache import getline as getLineFromCache, clearcache as clearLineCache, checkcache as checkLineCache
from linecache import getline

try: from json import load as fromJsonFile, loads as fromJsonString, dump as toJsonFile, dumps as toJsonString
except ImportError:
    try: from simplejson import load as fromJsonFile, loads as fromJsonString, dump as toJsonFile, dumps as toJsonString
    except ImportError:
        def jsonNotAvailable(*args, **kwd):
            raise NotImplementedError('Json methods not installed!')

        fromJsonFile = fromJsonString = toJsonFile = toJsonString = jsonNotAvailable

try: from collections import OrderedDict as ordereddict
except ImportError:
    # Provide our own implementation for < 2.7
    from collections_hack import OrderedDict as ordereddict

from thread import start_new_thread as _nth
def nth(function, *args, **kwd):
    return _nth(function, args, kwd)


# Sub-tools.
from debugging import breakOn, traceOn, remoteBreak, remoteTrace
from debugging import enter_debugger, debugCall, debugCall as runcall
asBuiltin(breakOn)
asBuiltin(traceOn)
asBuiltin(remoteBreak)
asBuiltin(remoteTrace)

from .errors import *
from .strings import *
from .misc import *
from .logs import *
from .cmdln import *

import timing

setupSubmodule(vars(), '.hashlib', 'hashlib',
               ('new', 'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512'))

# Pygments.
try: from .pyg_colorizer import stuphColorFormat
except ImportError:
    pyg_colorizer = False

    def stuphColorFormat(string):
        # Identity.
        return string
