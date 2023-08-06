# MUD Runtime -- Event Objects.
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
# Todo: from the component library/support module.
from ..tools import getLetters, listSortInsert

from sys import exc_info as getExceptionInfo
from traceback import print_exception as printException

# Event Handler Model.
class EventResult(Exception):
    def __init__(self, result):
        self.result = result
        # raise self

def eventResult(result):
    raise EventResult(result)

class MutableInstanceMethodObject:
    # Hack to be able to snap other members onto it.
    def __init__(self, method):
        self.__method = method
        self.__repr__ = method.__repr__
        self.__name__ = method.__name__
        self.__doc_ = method.__doc__

    def __call__(self, *args, **kwd):
        return self.__method(*args, **kwd)

class EventController:
    def __init__(self, event_name):
        self.event_name = event_name
        self.handlers = []

        # Because: See Binding.__getattr__
        self.decorator = MutableInstanceMethodObject(self.decorator)
        self.decorator.last = self.last
        self.decorator.first = self.first

    def __call__(self, *args, **kwd):
        for h in self.handlers:
            try: self.callHandler(h, *args, **kwd)
            except EventResult, e:
                return e.result

    def callHandler(self, handler, *args, **kwd):
        try: return handler(self, *args, **kwd)
        except EventResult:
            raise
        except:
            self.handleException(*getExceptionInfo())

    def handleException(self, cls, value, tb):
        printException(cls, value, tb)

    def registerHandler(self, handler):
        # Facilitate module reloading by removing all equivilant handlers.
        removal = []
        for h in self.handlers:
            if h == handler:
                removal.append(h)

        for h in removal:
            self.handlers.remove(h)

        # Now insert via priority.
        listSortInsert(self.handlers, handler,
                       key = lambda h: h.priority)

    def __iadd__(self, handler):
        self.registerHandler(handler)
        return self

    def decorator(self, function):
        self.registerHandler(Concretion(function))
        return function

    def last(self, function):
        self.registerHandler(Concretion(function, priority = HandlerBase.PRIORITY_LAST))
        return function

    def first(self, function):
        self.registerHandler(Concretion(function, priority = HandlerBase.PRIORITY_FIRST))
        return function

    def __repr__(self):
        return '%s(%s): %d handlers' % (self.__class__.__name__, self.event_name, len(self.handlers))

class Binding(object):
    def __init__(self, module):
        self.module = module

    def getController(self, name):
        try: ctlr = getattr(self.module, name)
        except AttributeError:
            ctlr = EventController(name)
            setattr(self.module, name, ctlr)
        else:
            assert issubclass(ctlr.__class__, EventController)

        return ctlr

    def __getattr__(self, name):
        if not name.startswith('_'):
            # See EventController.__init__
            return self.getController(name).decorator

        return object.__getattr__(self, name)

def declareEventController(name, **others):
    controllerClass = others.get('Controller', EventController)
    Module = others.get('Module')

    ctlr = controllerClass(name)
    if type(Module) is str:
        try: Module = __import__(Module)
        except ImportError:
            Module = None

    if Module is not None:
        setattr(Module, name, ctlr)

    return ctlr

def declare(module, events):
    for name in events:
        if not hasattr(module, name):
            ctlr = EventController(name)
            setattr(module, name, ctlr)

class EventBridge:
    class Calling:
        def __init__(self, name):
            self.name = name
        def __call__(self, *args, **kwd):
            from game import bridgeModule
            bridgeModule = bridgeModule()
            if bridgeModule:
                function = getattr(bridgeModule, self.name, None)
                if callable(function):
                    return function(*args, **kwd)

        def __repr__(self):
            print 'Calling: %r' % self.name
        __str__ = __repr__

    def __setattr__(self, name, value):
        self.__dict__[name] = self.Calling(value)

# Handler Types.
class HandlerBase:
    PRIORITY_FIRST = 0
    PRIORITY_LAST = 10000
    PRIORITY_NORMAL = (PRIORITY_LAST - PRIORITY_FIRST) / 2

    def __init__(self, priority = None):
        self.priority = priority

    def __call__(self, ctlr, *args, **kwd):
        pass

    def sameClass(self, other):
        try:
            thisClass = self.__class__
            otherClass = other.__class__

            return thisClass.__module__ == otherClass.__module__ and \
                   thisClass.__name__   == otherClass.__name__

        except AttributeError:
            return False

    def __eq__(self, other):
        return self.sameClass(other)
    def __cmp__(self, other):
        return cmp(self.priority, other.priority)

    @property
    def priority(self):
        return getattr(self, '_priority', self.PRIORITY_NORMAL)

    @priority.setter
    def priority(self, value):
        self._priority = self.PRIORITY_NORMAL \
                         if priority is None \
                            else int(priority)

class MemberResolutionHandler(HandlerBase):
    def __init__(self, method_name):
        method_name = method_name.split()[0].split('.')

        self.module = '.'.join(method_name[:-1])
        self.method = method_name[-1]

    def __call__(self, ctlr, *args, **kwd):
        try: module = self._import_module(self.module)
        except ImportError: pass
        else:
            if module:
                method = getattr(module, self.method, None)
                if callable(method):
                    return method(*args, **kwd)

    def _import_module(self, name):
        # Todo: import parts of name, in case the trailing items
        # are not submodules, but members.
        # (see mud/__init__: world.heartbeat.pulse)
        module = __import__(name)
        for m in name.split('.')[1:]:
            module = getattr(module, m)

        return module

    def __eq__(self, other):
        return self.sameClass(other) and \
               self.module == other.module and \
               self.method == other.method

    def __repr__(self):
        return 'resolve %s.%s' % (self.module, self.method)

class LoggingHandler(HandlerBase):
    def logEvent(self, ctlr, *args, **kwd):
        tab = '\n\t\t\t\t'

        msg = tab.join(map(repr, args))
        msg = '%s:%s%s' % (ctlr.event_name, tab, msg)

        if kwd:
            from pprint import pformat
            msg += tab
            msg += pformat(kwd)

        from mud import log
        log(msg)

    def __call__(self, ctlr, *args, **kwd):
        self.logEvent(ctlr, *args, **kwd)

class Concretion(HandlerBase):
    def __init__(self, function, *args, **kwd):
        HandlerBase.__init__(self, *args, **kwd)
        self.function = function

    def __call__(self, ctlr, *args, **kwd):
        # XXX todo: curry ctlr??
        return self.function(*args, **kwd)

    def __eq__(self, other):
        if self.sameClass(other):
            return self.function.__module__ == other.function.__module__ and \
                   self.function.func_name == other.function.func_name

    def __repr__(self):
        return repr(self.function)

# Parsing.
COMMENT_CHAR  = '#'
SECTION_LEFT  = '['
SECTION_RIGHT = ']'

def parseEvents(events, handler = None):
    for line in events.split('\n'):
        line = line.strip()
        if not line or line[0] == COMMENT_CHAR:
            continue

        if line[0] == SECTION_LEFT and line[-1] == SECTION_RIGHT:
            handler = line[1:-1]
        else:
            ws = line.find(' ')
            if ws < 0:
                yield line, handler, ''
            else:
                yield line[:ws], handler, line[ws + 1:].lstrip()

# A Configuration Layer.
_builtin_handlers = {'MemberResolution': MemberResolutionHandler,
                     'Logging'         : LoggingHandler}

def loadOnto(events, module):
    # Algorithm.
    for (name, handler, method) in parseEvents(events):
        ctlr = getattr(module, name, None)
        if ctlr is None:
            ctlr = EventController(name)
            setattr(module, name, ctlr)

        handlerClass = getHandlerClass(handler)
        if issubclass(handlerClass, HandlerBase):
            if method:
                ctlr += handlerClass(method)
            else:
                ctlr += handlerClass()

def getHandlerClass(name):
    return _builtin_handlers.get(getLetters(name))

def getEventNames(module):
    # Broad-spectrum:
    from mud.runtime import EVENT_NAMES
    return EVENT_NAMES
