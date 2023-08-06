# Runtime Error Handling.
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
__all__ = ['HandleException', 'ShowFrame',
           'getSystemException', 'getSystemExceptionString',
           'reraiseSystemException', 'reraise',
           'getModuleFileBasename']

from traceback import format_exc
from sys import exc_info as getSystemException

from . import getline, basename

# Utilities.
def getSystemExceptionString():
    return str(format_exc())
def reraiseSystemException():
    reraise(*getSystemException())
def reraise(type, value, tb):
    raise type, value, tb

def getModuleFileBasename(filename):
    from sys import path as system_path
    for p in system_path:
        if p:
            if filename.startswith(p):
                return filename[len(p)+1:]

    return filename

# Game-Level Routines.
# Todo: rewrite this because obviously it's doing what .logs does.
def HandleException(exc = None):
    from mud import log

    if exc is None:
        exc = getSystemException()

    (tp, val, tb) = exc

    # Find (second to?) last frame.
    while tb.tb_next:
        tb = tb.tb_next

    frame = tb.tb_frame
    code  = frame.f_code

    log('%s(%s): %s (%s:%d)' % (getattr(tp, '__name__', '<Unnamed>'),
                                code.co_name, str(val),
                                code.co_filename, frame.f_lineno))

def ShowFrame(frame, name, exc = None, use_basename = True):
    code = frame.f_code
    filename = code.co_filename

    line = getline(filename, frame.f_lineno).strip()

    if use_basename:
        filename = basename(filename)

    if exc:
        return '%s in %s: %s\n -> (%s:%d) %s' % \
               (name, code.co_name, exc[1], filename, frame.f_lineno, line)

    return '    (%s:%d:%s) %s' % (filename, frame.f_lineno, code.co_name, line)
