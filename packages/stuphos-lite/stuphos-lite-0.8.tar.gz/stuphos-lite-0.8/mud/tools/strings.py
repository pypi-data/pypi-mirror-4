# String Routines.
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

# Todo: use regexprs..?
# Todo: test against regexprs.
def buildNonletters():
    return ''.join(chr(c) for c in xrange(0, ord('A'))) + \
           ''.join(chr(c) for c in xrange(ord('Z') + 1, ord('a'))) + \
           ''.join(chr(c) for c in xrange(ord('z') + 1, 256))

def buildAscii():
    return ''.join(chr(c) for c in xrange(0, 256))

try: from curses.ascii import isprint as isPrintable
except ImportError:
    _printable_chr = '\' !"#$%&\\\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\''
    def isPrintable(c):
        return c in _printable_chr

def buildNonprintable():
    return ''.join(chr(c) for c in xrange(0, 256) \
                   if not chr(c) == '\n' and not isPrintable(chr(c)))

_nonletters = buildNonletters()
_ascii = buildAscii()

_nonprintable = buildNonprintable()

def getLetters(string):
    return string.translate(_ascii, _nonletters)

def getPrintable(string):
    return string.translate(_ascii, _nonprintable)

def splitOne(s, x):
    # Command-line argument passing routine.
    s = s.lstrip()
    parts = s.split(x, 1)
    if not parts:
        return ('', '')

    if len(parts) == 1:
        return (parts[0], '')

    return (parts[0], parts[1])

chopOne = splitOne

def SORP(n):
    return '' if n == 1 else 's'

def ANORA(s):
    return 'an' if s[:1].lower() in 'aeiou' else 'a'


VARIABLE_CODE = '$'
def InterpolateStringVariables(string, **values):
    parts = []
    position = 0

    while True:
        start = string.find(VARIABLE_CODE, position)
        if start < 0:
            break

        end = string.find(VARIABLE_CODE, start + 1)
        if end < 0:
            raise ValueError('Unterminated variable name: %s' % (string[start:]))

        if start > position:
            parts.append(string[position:start])

        name = string[start+1:end]
        if name:
            parts.append(values.get(name, ''))
        else:
            parts.append(VARIABLE_CODE)

        position = end + 1

    if position < len(string):
        parts.append(string[position:])

    return ''.join(parts)

# Other interpolation tools.
import re
SUBMETHOD_PATTERN = re.compile(r'(%(identifier)s)\$(%(identifier)s)\s*\(\s*(\))?' % \
                               dict(identifier = '[a-zA-Z]+[a-zA-Z0-9_]*'))

def TranslateSubmethodPatterns(string):
    def t():
        i = SUBMETHOD_PATTERN.scanner(string)
        c = 0

        while True:
            m = i.search()
            if m is None:
                break

            (s, e) = m.span()
            if s > c:
                yield string[c:s]

            c = e

            (a, b, p) = m.groups()
            if p:
                yield "call(%s, '%s')" % (a, b)
            else:
                yield "call(%s, '%s', " % (a, b)

        if c < len(string):
            yield string[c:]

    return ''.join(t())

# "{percentage(me.hit, me.max_hit)}"

class Expression(str):
    def __call__(self, sandbox):
        # Should, in practice, separate globals, locals
        return sandbox.eval(self)

def TokenizeInterpolatedExpression(string):
    s = 0
    n = len(string)

    while True:
        i = string.find('{', s)
        if i < 0:
            break

        if i > s:
            yield string[s:i]

        # Find ending '}' lexically (looking for nests and quotes).
        v = 0
        q = False

        i += 1
        for e in xrange(i, n):
            k = string[e]
            if q:
                # Handle quoted matter.
                if k == q:
                    if t != '\\':
                        q = False
                else:
                    q = k

                t = k # always gets set

            elif k == '{':
                v += 1 # deepness
            elif k == '}':
                if v:
                    v -= 1
                else:
                    break
        else:
            raise SyntaxError('No terminating }')

        yield Expression(string[i:e])
        s = e + 1

    if s < n:
        yield string[s:n]

class Interpolated(str):
    @classmethod
    def translateValue(self, sandbox, value):
        def i(t):
            if isinstance(t, Expression):
                return str(t(sandbox))
            if isinstance(t, basestring):
                return t

            return str(t)

        return ''.join(i(t) for t in TokenizeInterpolatedExpression(value))

    def __call__(self, sandbox):
        return self.translateValue(sandbox, self)

    __mod__ = __call__

class Interpolated2(Interpolated):
    @classmethod
    def translateValue(self, sandbox, value):
        # Convert submethod syntax patterns in string.
        value = TranslateSubmethodPatterns(value)
        return Interpolated.translateValue(sandbox, value)
