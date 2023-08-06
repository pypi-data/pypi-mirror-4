# MUD Runtime Object Registry.
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
# Todo: get this from common tools.
_undefined = object()

class RegistryNotInstalled(RuntimeError):
    pass
class ObjectAlreadyRegistered(RuntimeError):
    pass

class Access(object): # todo: inherit from runtime.structure.Object? and builtin.object
    # VHLL object access interface and runtime base class.
    class Node(object):
        def __init__(self, parent, name):
            self._parent = parent
            self._name = name

        def _buildName(self):
            if self._parent:
                return '%s::%s' % (self._parent._buildName(), self._name)

            return self._name

        def __getattr__(self, name):
            if not name.startswith('_'):
                # The basic goal here is to return a sub-node with priority
                # over attributes on the real, registered object, but support
                # dynamically access to those members secondarily.  This means
                # dynamic access to those members, except where eclipsed by
                # an inferior sub-node.
                #
                # This works effectively if the sub-objects are initialized
                # before the main object.  Otherwise, you'll have to use the
                # explicit get/registerObject toplevel routines if you know
                # for sure that it has a similarly named attribute.
                sub = Access.Node(self, name) # for reference.

                # Try to get the inferior object as named.
                if getObject(sub._buildName()) is None:
                    # Try to find an attribute on this named object.
                    o = getObject(self._buildName())
                    if o is not None:
                        # Only if there is an explicit attribute, and this isn't
                        # eclipsed by a registered sub-node object.
                        try: return object.__getattribute__(o, name)
                        except AttributeError:
                            pass # in this case, use unregistered sub-node:

                # Return the inferior node (not the object).
                # This means explicitly registered:
                #   Object::API
                #
                # will override the runtime['Object'].API real attribute,
                # that would be dereferenced above.
                #
                # By returning the node, instead of the object, sub-inferior
                # objects can still be referenced, even if there's an object
                # at Object, Object::API and Object::API:SubApi.
                #
                # This way, the real registered object is never returned by
                # this attribute lookup, only ever nodes.  Use explicit
                # getObject dereferencing to achieve this:
                #
                #   runtime['Object'].API
                #
                return sub

            return object.__getattribute__(self, name)

        def __call__(self, create, *args, **kwd):
            # runtime.Resource.Pool.Master(dict)
            # Q: Should this use registerObject? (to raise an error..)
            return getObject(self._buildName(),
                             create = lambda:create(*args, **kwd))

        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    def __getattr__(self, name):
        # Create Top-level Accessor.
        # XXX Also, prevents top-level object names from being accessed
        # directly, this way (because Access is not an Access.Node).
        #
        return object.__getattribute__(self, name) \
               if name.startswith('_') \
                  else Access.Node(None, name)

    def __getitem__(self, node):
        if isinstance(node, self.Node):
            node = node._buildName()

        assert isinstance(node, basestring)
        return getObject(node)

    def __delitem__(self, node):
        if isinstance(node, self.Node):
            node = node._buildName()

        assert isinstance(node, basestring)
        return delObject(node)

    def api(self, fon):
        return registerApi(fon)

# Construction:
def _createRegistry():
    return dict()

# The registry must be created initially.
# ---
# The registry storage object is a part of the runtime object,
# which is a component of the system module:
#    (systemModule->)runtime->(registryAccess)
#
# Both of these objects are composed with the following routines.

RUNTIME_OBJECT_NAME = 'runtime'
def getRuntimeObject():
    import sys as systemModule

    # Try to get from container module cache.
    try: return getattr(systemModule, RUNTIME_OBJECT_NAME)
    except AttributeError:
        pass

    # The Runtime class implementation is in a superior module,
    # (which derives from registry.Access)
    from mud.runtime import MudRuntime
    runtime = MudRuntime()
    runtime.system = runtime.System #: Cache this node.

    # Put into runtime container module.
    setattr(systemModule, RUNTIME_OBJECT_NAME, runtime)

    from mud.tools import registerBuiltin
    registerBuiltin(runtime, RUNTIME_OBJECT_NAME)

    return runtime

# XXX Want to set 'registry' on runtime, but the attribute lookup dynamically
# builds an Access.Node for anything that doesn't start with '_'
RUNTIME_REGISTRY_NAME = '_registry'
def getRegistry(create = False):
    runtimeObject = getRuntimeObject()

    try: registry = getattr(runtimeObject, RUNTIME_REGISTRY_NAME)
    except AttributeError:
        if create not in (None, False, 0):
            registry = _createRegistry()
            setattr(runtimeObject, RUNTIME_REGISTRY_NAME, registry)
            # runtimeObject.registry = registry

            # Hook shutdown game event with registry-cleanup function:
            #   This expects a certain kind of object (Binding) to
            #   be passed as 'create' parameter.  Otherwise, ignores.
            #
            #   (Admittedly, a weird convention).
            #
            try: create.shutdownGame(deleteAllObjects)
            except AttributeError:
                pass
        else:
            registry = None

    return registry

# Access API:
def getObject(name, create = None, **kwd):
    reg = getRegistry()
    if reg is None:
        raise RegistryNotInstalled('Registry not installed.')

    obj = reg.get(name, _undefined)
    if obj is _undefined:
        if callable(create):
            obj = reg[name] = create(**kwd)
        else:
            obj = None

    return obj

def setObject(name, value):
    reg = getRegistry()
    if reg is not None:
        if isinstance(name, Access.Node):
            name = name._buildName()

        reg[name] = value
    else:
        raise RegistryNotInstalled('Registry not installed.')

def registerObject(name, value):
    reg = getRegistry()
    if reg is not None:
        if isinstance(name, Access.Node):
            name = name._buildName()

        if name in reg:
            raise ObjectAlreadyRegistered(name)

        reg[name] = value
    else:
        raise RegistryNotInstalled('Registry not installed.')

def registerApi(fon, apiObject = None): # function-or-name
    if isinstance(fon, Access.Node):
        fon = fon._buildName()

    if isinstance(fon, basestring):
        if apiObject is not None:
            # Just directly register the object as an api.
            registerObject(fon, apiObject)
            return

        def makeNamedApiRegistry(object):
            registerObject(fon, object)
            return object

        return makeNamedApiRegistry

    # Expect a decorator style.
    assert apiObject is None

    def makeDefaultApiRegistry(object):
        # This style looks for a pre-programmed name.
        registerObject(object.NAME, object)
        return object

    return makeDefaultApiRegistry

def callObject(name, *args, **kwd):
    object = getObject(name)
    if callable(object):
        return object(*args, **kwd)

def callObjectMethod(name, methodName, *args, **kwd):
    object = getObject(name)
    if object is not None:
        try: method = getattr(object, methodName)
        except AttributeError: pass
        else: return method(*args, **kwd)

def _doDelete(object):
    # Todo: Maybe call this __unregister__?
    try: delete = getattr(object, '__registry_delete__', None)
    except ValueError:
        # This occurs if the object is a builtin entity handle
        # that has become invalid (through game-play).
        delete = None

    if not callable(delete):
        return True

    result = delete()
    if result is None:
        return True

    return bool(result)

def delObject(name, registry = None):
    if registry is None: # Err, why am I doing this?  Don't do this...
        registry = getRegistry()

    if registry is not None and name in registry:
        if _doDelete(registry[name]):
            del registry[name]
            return True

    return False

def deleteAllObjects(unused):
    from traceback import print_exc as traceback

    reg = getRegistry()
    for obj in reg.values():
        try: _doDelete(obj)
        except:
            traceback()

    reg.clear()

# Runtime-Access Usage:
##    # Creation:
##    r_pool = runtime.System.Resource.Pool(dict)
##
##    # Deletion:
##    del runtime['System::API']
##    del runtime[runtime.System.API]
##
##    # Method-decorator-based registration.
##    @registerApi('System::API')
##    class SystemAPI:
##        pass
##
##    @registerApi(runtime.System.API)
##    class SystemAPI:
##        pass
##
##    @registerApi
##    class SystemAPI:
##        NAME = 'System::API'
##
##    # Runtime-access-decorator-based registration.
##    @runtime.api('System::API')
##    class SystemAPI:
##        pass
##
##    @runtime.api(runtime.System.API)
##    class SystemAPI:
##        pass
##
##    @runtime.api
##    class SystemAPI:
##        NAME = 'System::API'
##
##    # Exact object lookup:
##    runtime[runtime.System.API]
##    runtime['System::API']

# Application example:
##    # Cache this lazy accessor for immediate invocation:
##    cmApi = runtime.system.CommandMessaging.API
##    def HandlePayload(self, payload):
##        cmApi.ExecuteTrustedCommandMessage(self.getUrlBase(), payload)

# Todo: Allow another kind of access:
# '@penobscotrobotics.us/modules/fraun/conf;1'
