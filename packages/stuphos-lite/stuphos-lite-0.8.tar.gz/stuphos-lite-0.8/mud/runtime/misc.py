# Miscellaneous Runtime Tools.
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
# Note: These things aren't really used anymore.
# (This stuff can come from common tools anyway)

# Instrument the Runtime Frame Stack.
from sys import _getframe as thisFrame

def show(order = None):
    for frame in order or stack():
        print string(frame)

def traceback(frame = None, n = -1):
    frame = frame or thisFrame()
    while frame:
        if n > 0:
            n -= 1
            if n > 0:
                frame = frame.f_back
                continue

        yield frame
        frame = frame.f_back

def stack():
    # Generate return in reverse order from grand-parent calling frame.
    return reversed(list(traceback(n = 2)))

def bottom():
    return list(traceback())[-1]

def string(frame):
    from linecache import getline
    code = frame.f_code
    return '%s:%s:%s%s' % (code.co_name, code.co_filename, code.co_firstlineno,
                           (frame.f_trace and ' (%s)' % frame.f_trace.__name__) or '')

def search(name = None, ascending = False):
    for frame in (ascending and stack() or traceback()):
        if frame.f_code.co_name == name:
            yield frame

def find(*args, **kwd):
    frames = search(*args, **kwd)

    try: return frames.next()
    except StopIteration:
        raise NameError(name)

# Debugger legacy:
##    def set_byframename(name):
##        self.reset()
##        stack = FrameStack.search(name = name, ascending = True)
##
##        try: main = iter(stack).next()
##        except StopIteration:
##            raise NameError(name)
##
##        else:
##            self.set_trace(main)
##            self.set_continue()


# Unused Patterns:
class Bundle:
    # Curry/Delegate Pattern.
    def __init__(self, function, *args, **kwd):
        self.function = function
        self.args = args
        self.kwd = kwd

    def __call__(self, *args, **kwd):
        args = self.args + args
        kwd.update(self.kwd)
        return self.function(*args, **kwd)
