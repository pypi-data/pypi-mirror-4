#!/usr/bin/python2.4
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

'Simulate a MUDOperations struct and register it with the game module via ctypes.'

from ctypes import c_void_p, c_int, py_object
from ctypes import CFUNCTYPE, PYFUNCTYPE, POINTER
from ctypes import pythonapi, byref, cast, addressof

## Business Logic.
from structs import EventOperations, MUDOperations, AUTOFUNCTYPE
linkModuleFunction = AUTOFUNCTYPE(EventOperations.P, MUDOperations.P)

PyCObject_AsVoidPtr = pythonapi.PyCObject_AsVoidPtr
PyCObject_AsVoidPtr.restype = c_void_p
PyCObject_AsVoidPtr.argtypes = [py_object]

def registerGameModule(ops):
        '''
        Imports game module and calls its registration method with the supplied ops,
        returning an event bridge.
        '''

        try: from game import register
        except ImportError:
                register = synthesizeGameModule().register

        link = linkModuleFunction(PyCObject_AsVoidPtr(register))
        return link(byref(ops))


## Application Ware.
class API:
        def __init__(self, OPSClass):
                self.ops = OPSClass(*self.getBindings(OPSClass._fields_))

        def getBindings(self, fields):
            for info in fields:
                binding = self.Binding(info, self)
                # yield info[1](binding)

                # Debugging
                try: yield info[1](binding)
                except Exception, e:
                    from traceback import print_exc as traceback
                    from pdb import set_trace as enterDebugger

                    traceback()
                    enterDebugger()

                    raise e

        class Binding:
                # Store field info bound to the api.
                def __init__(self, field_info, api):
                        self.procname, self.procdef = field_info
                        self.api = api

                def __call__(self, *args, **kwd):
                    from mud import log as mudlog
                    mudlog(self.api.callString(self.procname, args, kwd))

                    # Construct new default return type, as expected.
                    return addressof(self._default_result_)

                @property
                def _default_result_(self):
                    try: result = self.__result
                    except AttributeError:
                        try: result = self.procdef._data_type_()
                        except AttributeError:
                            result = self.procdef._restype_()

                        self.__result = result

                    return result

        def callString(self, name, args, kwd):
            scope = self.__class__.__name__
            if name.startswith('getvalue_'):
                return '%s::%s' % (scope, name[9:])

            if name.startswith('setvalue_'):
                return '%s::%s = %s' % (scope, name[9:], args[0])

            args = map(repr, args)
            args.extend('%s = %r' % i for i in kwd.iteritems())
            args = ', '.join(args)

            return '%s::%s(%s)' % (scope, name, args)

        def __getattr__(self, name):
            namestr = str(name)
            try: getvalue = getattr(self.__dict__['ops'],
                                    'getvalue_' + namestr)

            except (AttributeError, KeyError):
                try: return self.__dict__[name]
                except KeyError:
                    # Re-raise so that architecture works.
                    raise AttributeError(name)

            return getvalue()

        def __setattr__(self, name, value):
            namestr = str(name)
            try: setvalue = getattr(self.__dict__['ops'],
                                    'setvalue_' + namestr)

            except (AttributeError, KeyError):
                self.__dict__[name] = value
                return

            setvalue(value)

## Compatability.
def synthesizeGameModule():
        # Cell for the register callback.
        try: import game
        except ImportError:
                import new, sys
                game = sys.modules['game'] = new.module('game')

        # Build registration object.
        PyCObject_FromVoidPtr = pythonapi.PyCObject_FromVoidPtr
        PyCObject_FromVoidPtr.restype = py_object
        PyCObject_FromVoidPtr.argtypes = [c_void_p]

        def registerCallback(mudApi):
                from mud import log as mudlog
                mudlog('[Registering Game Module (%r)]' % mudApi)
                game.mudApi = mudApi

                # Remember reference.
                game.eventBridge = EventOperations()
                return addressof(game.eventBridge)

        # Remember reference.
        game.link = linkModuleFunction(registerCallback)
        game.register = PyCObject_FromVoidPtr(game.link)

        return game

## Test Facility.
class Main(API):
        def __init__(self):
                API.__init__(self, MUDOperations)
                self.eventBridge = registerGameModule(self.ops)

        def __repr__(self):
                return '%s\n  ops: %r\n  eventBridge: %r' % \
                       (self.__class__.__name__,
                        self.ops, self.eventBridge)

        __str__ = __repr__

def main():
    synthesizeGameModule()

    if 0:
        global ops
        ops = Main()
        print ops

if __name__ == '__main__':
    main()
