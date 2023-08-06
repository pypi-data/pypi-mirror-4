# MUD Runtime -- Object Entities.
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
# Todo: probably rename this to 'architecture'
from . import Concretion, declareEventController, EventController

from types import DictionaryType
from new import classobj as newClassObject

# Overall identity constant.
class Undefined(object):
    def __repr__(self):
        return self.__class__.__name__
    __str__ = __unicode__ = __repr__

Undefined = Undefined()

# Design Pattern.
class Singleton(object):
    # This should be further specialized into 'Event' for runtime constructs.
    class Meta(type):
        def __new__(self, name, bases, values):
            cls = type.__new__(self, name, bases, values)
            if Singleton in bases:
                return cls

            ##    postvalues = {}
            ##    for name in values.keys():
            ##        if name in ['__module__', '__doc__']:
            ##            postvalues[name] = values[name]
            ##            del values[name]
            ##
            ##    inst = cls(name, **values)
            ##    inst.__dict__.update(postvalues)
            ##    return inst

            return cls(name, **values)

# Identity.
class Object(object):
    class Meta:
        Attributes = []

        def __init__(self, *attributes, **kwd):
            self.Attributes = list(attributes) + kwd.items()

        @staticmethod
        def formatAttribute(instance, a, default = Undefined):
            def getAttribute(name):
                if callable(name):
                    return name(instance)

                if name.endswith('()'):
                    v = getattr(instance.Meta, name[:-2], default)
                    if callable(v):
                        return v(instance)
                else:
                    return getattr(instance, name, default)

                return Undefined

            if type(a) in (list, tuple):
                if len(a) == 2:
                    return '%s = %r' % (a[0], getAttribute(a[1]))
                if len(a) == 3:
                    return '%s = %r' % (a[0], getAttribute(a[1], a[2]))

            elif type(a) is str:
                return '%s = %r' % (a, getAttribute(a))

        @staticmethod
        def className(instance):
            return instance.__object_name__()

        @classmethod
        def instanceRepr(self, instance):
            meta = instance.Meta
            attribs = ', '.join(meta.formatAttribute(instance, a) for \
                                a in meta.Attributes)
            if attribs:
                return '<%s %s>' % (meta.className(instance), attribs)

            return '<%s>' % meta.className(instance)

    def __init__(self, name = Undefined):
        if name is not Undefined:
            self.__name = name

    def __repr__(self):
        return self.Meta.instanceRepr(self)
    def __str__(self):
        return self.__repr__()

    # This should go in the Meta.
    def __object_name__(self):
        try: return self.__name
        except AttributeError:
            return self.__class__.__name__

    @classmethod
    def instanceOf(self, other):
        return isinstance(other, self)

        ##    try: return issubclass(other.__class__, self)
        ##    except AttributeError:
        ##        return False

def LookupObject(name, raise_import_errors = False):
    'A clever routine that can import an object from a system module from any attribute depth.'
    # XXX This doesn't import modules that aren't imported by their parent package initialization code.
    parts = name.split('.')

    moduleObject = None
    module = None
    n = len(parts)
    x = 0

    while x < n:
        name = '.'.join(parts[:x+1])
        moduleObject = module

        # Try to find the module that contains the object.
        try: module = __import__(name, globals(), locals(), [''])
        except ImportError:
            break

        x += 1

    # No top-level module could be imported.
    assert moduleObject is not None

    object = moduleObject
    while x < n:
        # Now look for the object value in the module.

        # If an attribute can't be found -- this is where we raise the original import-error?
        #
        # This is a good idea: so that LookupObject is consistantly raising ImportError (since)
        # that's basically what its function is -- an import-from).
        #
        ##    if raise_import_errors:
        ##        module = __import__(name, globals(), locals(), [''])

        object = getattr(object, parts[x])
        x += 1

    # todo: raise prior ImportError if it existed because of a problem in the loaded module.
    return object

LookupClassObject = LookupObject

class Synthetic(Object):
    class Meta(Object.Meta):
        Attributes = Object.Meta.Attributes + ['members()']

        @staticmethod
        def members(instance):
            return ', '.join(map(str, instance.__dict__.keys()))

    def __init__(self, dict = None, **values):
        if not isinstance(dict, DictionaryType):
            assert dict is None
            dict = values
        else:
            dict.update(values)

        self.__dict__ = dict

# Component Event Model.
# todo: rename to `Instrument'
# todo: make Singleton behavior part of new, AutoInstrument class.
class Component(Singleton, Concretion):
    # Todo: Rename to Instrument?
    __metaclass__ = Singleton.Meta
    def __init__(self, name, Module = None, **others):
        # Register this component class instance with bridge module.
        self.Target = others.get('Target', self)
        self.bindToRuntime(Module)

        try: init = self.__instance_init__
        except AttributeError: pass
        else: init() # others['__init_args__']

    def __call__(self, ctlr, *args, **kwd):
        method = self.getTriggerFunction(ctlr.event_name)
        if callable(method):
            return method(ctlr, *args, **kwd)

    def __eq__(self, other):
        if self.sameClass(other):
            try:
                return self.__class__.__module__ == \
                         other.__class__.__module__ and \
                       self.__class__.__name__ == \
                         other.__class__.__name__

            except AttributeError:
                return False

    def getTriggerFunction(self, event_name):
        return getattr(self.Target, self.getTriggerName(event_name), None)
    def getTriggerName(self, event_name):
        return getTriggerName(event_name)

    DYNAMIC_TRIGGERS = False
    def bindToRuntime(self, Module = None):
        from mud.runtime.events import getEventNames, Binding

        if Module is None:
            from mud import getBridgeModule
            Module = getBridgeModule()

        binding = Binding(Module)

        # XXX This makes only one spectrum of component to be built.
        # (that is, use of Component is only ever for interned-core
        # events and never for some secondary set of events)
        for event in getEventNames(Module):
            # What this is saying is that it won't bind to events that don't exist.
            if self.DYNAMIC_TRIGGERS or callable(self.getTriggerFunction(event)):
                ctlr = binding.getController(event)
                ctlr.registerHandler(self)

    def __repr__(self):
        return '%s.%s (Component)' % (self.__module__, self.__class__.__name__)

def getTriggerName(event_name):
    return 'on%s%s' % (event_name[0].upper(), event_name[1:])

def newComponent(cls, name = None, **values):
    if name is None:
        # Unfortunately, it ends up taking up the module name that calls newClassObject.
        name = '%s.%s' % (cls.__module__, cls.__name__)

    # values['__instance_init__'] = cls.__init__
    # values['__init_args__'] = (args, kwd)
    return newClassObject(name, (Component, cls), values)

# This should be in events, but it relies on Singleton.
class DeclareEvent(Singleton):
    __metaclass__ = Singleton.Meta

    def __new__(self, *args, **kwd):
        return declareEventController(*args, **kwd)

# Game-Level Objects.
class UnknownFlag(NameError):
    pass

class Bitvector(Object):
    # A pure implementation of the bitvector type in game module.
    class Meta(Object.Meta):
        Attributes = Object.Meta.Attributes + ['set']

    def __init__(self, __bitv = 0, **bits):
        # This is an abstract base class.
        assert self.__class__ is not Bitvector

        self.__bitv = int(__bitv)
        for (name, value) in bits.iteritems():
            setattr(self, name, bool(value))

        self.getUpperBitvNames()

    @classmethod
    def getUpperBitvNames(self):
        try: return self.__UPPER_BITVECTOR_NAMES
        except AttributeError:
            names = self.__UPPER_BITVECTOR_NAMES = \
                [n.upper() for n in self.BITVECTOR_NAMES]

        return names

    BITVECTOR_NAMES = []

    def isBitSet(self, bit):
        return bool(self.__bitv & bit)
    def getFlagBit(self, name):
        try: return (1 << self.getUpperBitvNames().index(name.upper()))
        except ValueError:
            raise UnknownFlag

    def isFlagSet(self, name):
        return self.isBitSet(self.getFlagBit(name))

    @property
    def names(self):
        return self.BITVECTOR_NAMES

    @property
    def set(self):
        return [name for name in self.names if self.isFlagSet(name)]

    @property
    def notset(self):
        return [name for name in self.names if not self.isFlagSet(name)]

    unset = nonset = notset

    def __getattr__(self, name):
        try: return self.isFlagSet(name)
        except UnknownFlag:
            return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        try: bit = self.getFlagBit(name)
        except UnknownFlag: return object.__setattr__(self, name, value)
        else: self.__bitv |= bit if value else ~bit

    def __int__(self):
        return int(self.__bitv)
    def __str__(self):
        return ', '.join(map(str, self.set))
    def __iter__(self):
        return iter(self.set)

class PromptPreferences(Bitvector):
    BITVECTOR_NAMES = ['Mail', 'DataRate']
