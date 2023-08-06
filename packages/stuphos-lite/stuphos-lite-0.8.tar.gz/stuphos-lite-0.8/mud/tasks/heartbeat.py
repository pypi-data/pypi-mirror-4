# Monolithic Synchronization Driver (circle).
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
import Queue
import sys
import contextlib

from threading import Thread
from time import sleep, time as getCurrentTime

from mud.tasks import Procedure
from mud.tasks.vtpool import VTPool as RealtimeAPI
from mud.tools import reraise

# Conformation Protocol.
CORE_PULSE = (0, 0)

class Heartbeat(RealtimeAPI):
    class Adapter(Procedure):
        def run(self, pulse, cumm):
            pass

    class Yield(Exception): # virtual.Machine.Task.Yield?
        pass

    def __init__(self):
        self.Cummulative = 0L
        self.Adapters = dict()
        self.TaskQ = Queue.Queue()
        self.ScheduledEvents = []

    # Consider bridged pulse events:
    #    OneSecond is much more efficient, but currently disabled.
    def pulse(self, secs, usecs):
        with self.lifecycle(secs, usecs) as withinPulseTimeslice:
            cumm = self.Cummulative = self.Cummulative + 1

            # Standard, Circle-looking behavior.
            for (function, pulse) in self.computeAdapters(cumm):
                self.dispatchTask(function, (pulse, cumm), {})

            # Scheduled Events.
            for event in self.fireScheduledEvents(getCurrentTime()):
                self.dispatchEvent(event)

            try:
                # Middleware.  Timeslicing operation part of lifecycle.
                # Note: hasPendingOperations not needed anymore.
                while withinPulseTimeslice(): #  and self.hasPendingOperations():
                    task, args, kwd = self.TaskQ.get_nowait()
                    self.dispatchTask(task, *args, **kwd)

            except (Queue.Empty, self.Yield):
                pass

    __call__ = pulse

    @contextlib.contextmanager
    def lifecycle(self, *args):
        self.pulseStart(*args)
        exc = None
        try:
            # XXX Does capturing exceptions here even work?
            try: yield self.withinPulseTimeslice
            except: exc = sys.exc_info()

        finally:
            self.pulseEnd(exc)

    def pulseStart(self, *args):
        pass
    def pulseEnd(self, exc = None):
        pass

    def withinPulseTimeslice(self):
        return True

    def dispatchTask(self, task, *args, **kwd):
        if callable(task):
            return task(*args, **kwd)

        elif Procedure.instanceOf(task):
            return task.run(self, *args, **kwd)

    def dispatchEvent(self, event):
        # In-Heartbeat:
        if type(event) in (list, tuple):
            if len(event) == 3:
                (action, args, kwd) = event
                action(*args, **kwd)

            elif callable(event):
                event()

    def hasPendingOperations(self):
        # Check for running heartbeat.
        if not self.TaskQ.empty():
            return True
        if self.Adapters:
            return True
        if self.ScheduledEvents:
            return True

    pendingOperations = hasPendingOperations

    def addScheduledEvent(self, delay, event, *args, **kwd):
        self.ScheduledEvents.append((getCurrentTime() + delay, (event, args, kwd)))

    def fireScheduledEvents(self, now):
        regen = []
        current = self.ScheduledEvents
        self.ScheduledEvents = []

        for ev in current:
            if now > ev[0]:
                yield ev[1]
            else:
                regen.append(ev)

        # Put (procedurally-not-chronologically) older events before newer ones:
        self.ScheduledEvents = regen + self.ScheduledEvents 

    def computeAdapters(self, cumm):
        # Pre-load all items:
        items = tuple(self.Adapters.items())
        for (function, pulse) in items:
            # p = long(pulse[0]) * 100000L + long(pulse[1])
            p = long(pulse[0]) * 10L + long(pulse[1])
            if not p or not cumm % p:

            # if not pulse[0] and not pulse[1] or \
            #    cumm % (long(pulse[0]) * 100000L + pulse[1]):

                yield (function, pulse)

    def enqueueTask(self, task, *args, **kwd):
        # Interrupt the select() poll -- only in NETCOMA!!
        # kill(os.getpid(), signal.SIGIO)
        self.TaskQ.put_nowait((task, args, kwd))

    # This should just function as an internal pulse-adapter.
    class TimeKeeping(Thread):
        def __init__(self):
            Thread.__init__(self)
            self.__running = False

            # XXX Need another synchronization mechanism.
            self.q = Queue.Queue()

        # XXX WRONG!
        def addSchedule(self, timeout, function, *args, **kwd):
            self.q.put((timeout, function, args, kwd))
            self.startOnce()

        def __iadd__(self, (timeout, function, args, kwd)):
            self.addSchedule(timeout, function, *args, **kwd)
            return self

        def startOnce(self):
            if not self.__running:
                self.__running = True
                self.start()

        def run(self):
            while True:
                try: (timeout, function, args, kwd) = self.q.get_nowait()
                except Queue.Empty:
                    break

                self.doTimeout(timeout)
                self.dispatchTask(function, *args, **kwd)

        def doTimeout(self, n):
            sleep(n)

        def dispatchTask(self, function, *args, **kwd):
            return function(*args, **kwd)

    def getTimeKeeper(self):
        # XXX Single-timer-per-timeout.
        return self.TimeKeeping()

        try: return self.timeKeeper
        except AttributeError:
            tk = self.timeKeeper = self.TimeKeeping()
            return tk

    def invokeTimeoutForHeartbeat(self, timeout, function, *args, **kwd):
        # Executed in time-keeping thread, posting back to heartbeat:
        args = (function,) + args
        self.getTimeKeeper().addSchedule(timeout, self.enqueueTask, *args, **kwd)

    def invokeTimeout(self, timeout, function, *args, **kwd):
        # Execute entirely in time-keeping thread.
        self.getTimeKeeper().addSchedule(timeout, function, *args, **kwd)

    # Timekeeping folded into heartbeat pulse functionality:
    # NOTE: This ignores above TimeKeeper functionality.
    invokeTimeoutForHeartbeat = invokeTimeout
    addSchedule = addScheduledEvent
    def invokeTimeout(self, timeout, function, *args, **kwd):
        # Execute entirely in time-keeping thread.
        self.addScheduledEvent(timeout, function, *args, **kwd)
    def getTimeKeeper(self):
        return self

    def deferredTask(self, task, *args, **kwd):
        from sys import exc_info
        response_q = Queue.Queue() # Just a synchronization mechanism.

        def inlineWrapper():
            # If the put operation doesn't work immediately,
            # there's something wrong...
            try    : result = self.dispatchTask(task, *args, **kwd)
            except : response_q.put_nowait((False, exc_info()))
            else   : response_q.put_nowait((True,  result))

        # Post task request.
        self.enqueueTask(inlineWrapper)

        # Process results, blocking.
        (success, result) = response_q.get()
        if success:
            return result

        # On error, propogate exception state.
        reraise(*result)

    executeInline = deferredTask

    def registerAdapter(self, function, pulse):
        # What about Procedures?
        # assert callable(function), '%r is not callable!' % (function,)
        self.Adapters[function] = pulse

        # Todo: implement sequential slices

    def unregisterAdapter(self, function):
        if function in self.Adapters:
            del self.Adapters[function]

        return self
