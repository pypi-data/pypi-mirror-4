# General-purpose, performance-bound utility timing dispatch multiplexor.
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
from time import time as getCurrentSystemTime
from sys import platform
# thread.allocate_lock()

if platform == 'cygwin':
    # Cygwin: no virtual timer, so use real alarm clock.
    from signal import SIGALRM as SIGALRM_TYPE
    from signal import ITIMER_REAL as ITIMER_TYPE
    from signal import setitimer, getitimer, signal

# Composite GCF interval should cut down imprecision in sighandler-dispatch overhead.

class VTPool:
    def registerRealtimeAdapter(self, function, pulse):
        return self.registerAdapter(function, pulse)
        # Sort adapter into collection ascending timeouts.
        # Engage the timer mechanism with shortest time:
        #   recognize pending shortest timeout and readjust interval.
    def unregisterRealtimeAdapter(self, function):
        return self.unregisterAdapter(function)

    def engageTimer(self):
        last_signal_handler = signal(SIGALRM_TYPE, self.realtimeInterruptHandler)
        last_timer = getitimer(ITIMER_TYPE)

        ##    # XXX These things really should be done independently.
        ##    self.stack.append((last_signal, timer))
        ##
        ##    setitimer(TIMER_TYPE, self.interval, self.interval)

    def disengageTimer(self):
        pass

    def realtimeInterruptHandler(self, signr, frame):
        # Strategy: exit handler as quick as possible, by taking
        # a snapshot of its state and deferring all processing to
        # the event queue.
        self.enqueueTask(self.processRealtimeAdapters, getCurrentSystemTime())

    def processRealtimeAdapters(self, epoch):
        # Rotate adapter state, acquire shortest adapter timeout.
        # Regenerate virtual timer using next timeout minus overhead since sighandler epoch.
        pass

    def __init__(self):
        self.RealtimeAdapters = []
        self.realtime_engaged = False


# Extract system-call interaction algorithms:
##    class Timeslicing(object):
##        def __init__(self, interval, routine = None):
##            if routine is not None:
##                self.routine = routine
##
##            self.interval = interval
##            self.stack = []
##
##        def __enter__(self):
##            last_signal = signal(SIGVTALRM, self)
##            timer = getitimer(TIMER_TYPE)
##
##            # XXX These things really should be done independently.
##            self.stack.append((last_signal, timer))
##
##            setitimer(TIMER_TYPE, self.interval, self.interval)
##            return self
##
##        def __exit__(self, etype = None, value = None, tb = None):
##            # Try to restore previous timing state.
##            try: (h, t) = self.stack[-1]
##            except IndexError: pass
##            else:
##                del self.stack[-1]
##                (n, s) = t
##                if n and s:
##                    setitimer(TIMER_TYPE, n, s)
##
##                # XXX This should be done in the signal handler,
##                # because there still might be a pending itimer
##                # caught up.  Which means explicit client usage...
##                if h is not None:
##                    signal(SIGVTALRM, h)
##
##        def __call__(self, *args, **kwd):
##            # Curry this timing object.
##            return self.routine(self, *args, **kwd)
##
##        def routine(self, *args, **kwd):
##            # Default timing implementation (nothing).
##            # Reset signal handler.
##            pass
##
##    class Engine:
##        def __init__(self, interval, max):
##            self.instructions = 0
##            self.max = max
##            self.running = True
##            self.last = getCurrentSystemTime() # 0
##            self.timing = Timeslicing(interval, self.interrupt)
##
##        def interrupt(self, timer, signr, frame):
##            ##    i = self.instructions
##            ##    n = i - self.last
##            ##    self.last = n
##
##            n = getCurrentSystemTime()
##            print round(n - self.last, 7)
##            self.last = n
##
##            # print '%s: %s' % (i, n / float(self.interval))
##            # print frame.f_code.co_name, ':', frame.f_lineno
##            if self.instructions > self.max:
##                self.running = False
##
##        def __call__(self):
##            with self.timing:
##                while self.running:
##                    self.instructions += 1
##
##    if __name__ == '__main__':
##        from optparse import OptionParser
##        parser = OptionParser()
##        parser.add_option('-i', '--interval', type = float, default = .1)
##        parser.add_option('-m', '--max', type = int, default = 20000000)
##        (options, args) = parser.parse_args()
##
##        run = Engine(options.interval, options.max)
##        run()
