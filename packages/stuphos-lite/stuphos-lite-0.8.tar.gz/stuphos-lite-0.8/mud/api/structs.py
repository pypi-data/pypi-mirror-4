'''
Contains all of the Circle/StuphMUD structures.

'''
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

from ctypes import c_int, c_char_p, c_char, c_byte, c_ubyte, c_float
from ctypes import c_void_p, c_short, c_ushort, c_long, c_ulong
from ctypes import Structure, cast, _Pointer as PointerType
from ctypes import POINTER, CFUNCTYPE, _CFuncPtr, _FUNCFLAG_CDECL

# C Typedefs
c_time_t = c_int
c_bool = c_byte
c_size_t = c_int
c_socket_t = c_int

c_int_p = POINTER(c_int)
c_int_pp = POINTER(c_int_p)

c_char_pp = POINTER(c_char_p)

FILE_P = c_void_p

#
# This is intended for use as a void return type for cdecl convention,
# assuming that void equates to a c_int on the stack.  It seems perfectly
# reasonable to use `None` in this capacity, but that only crashes the
# interpreter.
#
# XXX `None` *should* be a valid restype!  (according to examples)
# c_void = None
#
c_void = c_int

# Standard library types
FILE = c_void_p

class TimeValue(Structure):
    _fields_ = []

TimeValue.P = POINTER(TimeValue)
c_timeval = TimeValue

# Return Value Conversion Facility
    #
    #  Is this true?
    #   [There seems to be a matter of POINTER types, even to simple
    #    ctypes data types, being invalid result types (???)]
    #

_c_default_retval = c_int
_conversion_functype_cache = {}
def AUTOFUNCTYPE(data_type, *argtypes):
    'Automatically install conversion function for pointer data type.'
    try:
        return _conversion_functype_cache[(data_type, argtypes)]
    except:
        class ConversionFunctionType(_CFuncPtr):
            _data_type_ = data_type

            _argtypes_ = argtypes
            _restype_ = _c_default_retval
            _flags_ = _FUNCFLAG_CDECL

            def __init__(self, *args, **kwd):
                _CFuncPtr.__init__(self, *args, **kwd)

                # Override the restype on the instance.
                self.restype = self.__cast_data__

                # I can't decide whether or not to implement this:
                # self.data_type = self._data_type_

            def __cast_data__(self, address):
                # The conversion routine expects an integer address.
                return cast(address, self._data_type_)

        _conversion_functype_cache[(data_type, argtypes)] = ConversionFunctionType
        return ConversionFunctionType

# MUD Typedefs
RealNumber = c_int
VirtualNumber = c_int

generic_rnum = RealNumber
generic_vnum = VirtualNumber

room_rnum = RealNumber
room_vnum = VirtualNumber

obj_rnum = RealNumber
obj_vnum = VirtualNumber

mob_rnum = RealNumber
mob_vnum = VirtualNumber

zone_rnum = RealNumber
zone_vnum = VirtualNumber

# Should we support these?
# sh_int = c_short

# Constants
MAX_INPUT_LENGTH = 256
MAX_RAW_INPUT_LENGTH = 512
SMALL_BUFSIZE = 4096
MAX_NAME_LENGTH = 20
MAX_EMAIL_LENGTH = 80

# Todo: re-cast all types that are unsigned.  I forgot that `ctypes`
# offered unsigned varities of the primitives.

# MUD Entities

class EventOperations(Structure):
    'EventOperations'
    _fields_ = \
        [('boot_start', CFUNCTYPE(c_void)),
         ('boot_complete', CFUNCTYPE(TimeValue.P)),
         ('world_reset_start', CFUNCTYPE(c_void)),
         ('world_reset_complete', CFUNCTYPE(c_void)),
         ('heartbeat_pulse', CFUNCTYPE(c_char_p, c_int)),
         ('heartbeat_timeout', CFUNCTYPE(TimeValue.P)),
         ('do_python', CFUNCTYPE(CharacterData.P, c_char_p, c_int, c_int))]
        # Unfinished

EventOperations.P = POINTER(EventOperations)

# Todo: reconfigure getvalues to use the autofunc.
class MUDOperations(Structure):
    'MUDOperations'

    _fields_ = []

MUDOperations.P = POINTER(MUDOperations)
