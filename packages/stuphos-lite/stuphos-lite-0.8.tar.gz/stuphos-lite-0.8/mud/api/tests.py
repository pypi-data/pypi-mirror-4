'Test Application'
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
from ctypes import *
import structs
import sys

_ctypes = CDLL({'win32': '_ctypes.pyd',
                'cygwin': 'python2.5/lib-dynload/_ctypes'}[sys.platform])

def make_char():
    return structs.CharacterData()

def make_string(o):
    # Creates a mutable copy.
    return string_at(addressof(o), sizeof(o))

class LibrarySymbol:
    class FrozenTable(Structure):
         _fields_ = [("name", c_char_p),
                     ("code", POINTER(c_ubyte)),
                     ("size", c_int)]

    FrozenTable.P = POINTER(FrozenTable)
    FrozenTable.table = FrozenTable.P.in_dll(pythonapi, "PyImport_FrozenModules")

    CHOP_LENGTH = 10

    @classmethod
    def show_frozen_table(cls):
        print "%-27s   [  Address/Size ]  'Code'" % 'Frozen Module Name'
        for item in cls.FrozenTable.table:
            name = item.name
            if name is None:
                break

            size = item.size
            if size < 0:
                size = -size # abs
                check = '*'
            else:
                check = ' '

            # How to obtain the integer value of the code variable?
            addr = frag = item.code
            addr = 0

            if frag > 0 and False:
                frag = string_at(addr, min(item.size, cls.CHOP_LENGTH))

            print "  %-25s  %c[ 0x%08x/%4d ]  %r" % (name, check, addr, size, frag)

def main():
    global c, s, b

    c = make_char()
    s = make_string(c)
    b = buffer(c)

    # LibrarySymbol.show_frozen_table()

def test():
    from _ctypes import PyObj_FromPtr as fp

    CD = structs.CharacterData
    CD.P = POINTER(CD)
    z = sizeof(CD)

    b = create_string_buffer(z)
    a = addressof(b)

    # return CD.P.from_address(a)

    return CD, CD.P, b, a, z
    print b, a

    b2 = (c_char * z)
    b2 = b2(*['x'] * z)

    a = addressof(b2)
    print b2, a

    global p, m

    # Decide pointer original value.
    # p = fp(a) # b2
    p = b # 2

    # Perform type-conversion via a cast.
    p = cast(p, CD.P)
    m = p[0]

    m.player.name = 'Fraun'
    print m.player.name

class C:
    class Informative:
        def __init__(self, __name, **kwd):
            self.__dict__.update(kwd)
            self.__name = __name
            self.__keys = kwd.keys()

        def __str__(self):
            parts = ['[%s]' % self.__name]
            parts.extend('%-30s : %r' % (k, getattr(self, k, None)) \
                         for k in self.__keys)

            return '\n\t'.join(parts)

        __repr__ = __str__

    StructType = type(Structure)
    v = locals()

    import structs
    g = structs.__dict__

    for (name, cls) in g.iteritems():
        if type(cls) is StructType:
            try: f = getattr(cls, '_fields_')
            except AttributeError:
                continue

            v[name] = Informative(name, **dict(f))

    del StructType, v, g, name, cls, f

## Test Application -- to be removed.
class CStruct:
    # Create an informative list.
    StructType = type(Structure)
    Assoc = dict()

    # Populate the list.
    for (name, cls) in globals().iteritems():
        if type(cls) is StructType:
            Assoc[name] = cls

    # Cleanup.
    del name, cls

def test():
    Class = MUDOperations
    PointerType = type(POINTER(c_int))
    Primitives = (c_int, c_long, c_char_p, c_size_t) # c_void_p

    # Filter out all func-ptr fields with primitive
    # return types or pointers to primitive types.
    for (name, field) in Class._fields_:
        field = getattr(Class, name)
        field = field.__get__(field)
        restype = field.restype

        if restype in Primitives:
            continue
        if type(restype) is PointerType:
            if restype._type_ in Primitives:
                continue

        print '%s: %s' % (name, restype)

def test():
    from ctypes import Structure, POINTER
    class I(Structure):
        _fields_ = [('x', c_int)]

    ##    @memory
    ##    def Callback():
    ##        return I(42)

    procdef = AUTOFUNCTYPE(POINTER(I))
    proc = procdef(memory(lambda: I(42)))

    print proc()[0].x
    return proc


# This is example functionality not necessary in the final product.
def memory(function):
    'Automatically stores reference to ctypes value and returns its address.'
    # (Which is probably what you want.)

    from ctypes import addressof
    def wrapper(*args, **kwd):
        # Expect a ctypes data type.
        value = function(*args, **kwd)
        function.memory = value

        ##    try: memory = function.memory
        ##    except AttributeError:
        ##        memory = function.memory = list()
        ##
        ##    # Can't use set() because ctypes aren't hashable.
        ##    if value not in memory:
        ##        memory.append(value)

        return addressof(value)

    return wrapper


main = test
(__name__ == '__main__') and main()
