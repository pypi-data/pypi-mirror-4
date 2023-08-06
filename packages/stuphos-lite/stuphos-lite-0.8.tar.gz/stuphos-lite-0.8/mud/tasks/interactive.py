# Interactive -- Should go into tools or its own module.
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
# For user interface with task subsystem.
import sys, Queue
from time import sleep, time as now
from traceback import print_exc as traceback
from thread import start_new_thread as nth
from profile import Profile

try: import select
except ImportError: pass

try: import readline
except ImportError: pass

def isException(this):
    try: return issubclass(this, Exception)
    except (AttributeError, TypeError): pass

    try: return issubclass(this.__class__, Exception)
    except (AttributeError, TypeError): pass

    return False

class Interactive:
    from sys import stdout

    def __init__(self, ns = {}, prompt = 'girl> ', profile = None):
        self.__prompt = prompt
        self.ns = ns
        self.input_queue = Queue.Queue()
        self.command_queue = Queue.Queue()
        self.pulse = heartbeat().next
        self.processing = False
        self.profile_filename = profile
        if profile:
            self.profiler = Profile()
        else:
            self.profiler = None

    def get_prompt(self):
        return self.__prompt
    def set_prompt(self, prompt):
        self.__prompt = prompt

    def loop(self, performance, *args, **kwd):
        self.pulse() # Initialize.
        try:
            while True:
                # Todo: inject timing simulation into client routine.
                if self.profiler is None:
                    performance(*args, **kwd)
                else:
                    self.profiler.runcall(performance, *args, **kwd)

                # self.interact()
                self.pulse()

        except (EOFError, KeyboardInterrupt):
            print
        except SystemExit:
            pass

        finally:
            if self.profiler is not None:
                self.profiler.dump_stats(self.profile_filename)

            self.command_queue.put(EOFError)

    def readline(self, single = False):
        if not self.processing:
            self.processing = True
            nth(self.process_input, (single,))

        try: msg = self.input_queue.get() # _nowait()
        except Queue.Empty:
            pass
        else:
            if isException(msg):
                self.processing = False
                raise msg

            if type(msg) is str:
                self.command_queue.put(None)
                # self.interpret_line(msg)
                return msg

    def process_input(self, single = False):
        # Bootstrap self.
        self.command_queue.put(None)

        try:
            while True:
                # Process commands posted by the interactive controller.
                try: cmd = self.command_queue.get()
                except Queue.Empty:
                    pass
                else:
                    if isException(cmd):
                        raise cmd

                # Do the input poll and post result.
                self.input_queue.put(raw_input(self.get_prompt()))
                if single:
                    raise EOFError

        except EOFError, e:
            self.input_queue.put(e)

        except:
            traceback()

        finally:
            # Empty the command queue
            try:
                while True:
                    self.command_queue.get()

            except Queue.Empty:
                pass

    def interact(self):
        self.interpret_line(self.readline())

    def interpret_line(self, line):
        return self.user_line_input(line) or evaluate_python(self.__prompt, self.ns, line)

    def user_line_input(self, line):
        return False

# Interactive Patterns.
def evaluate_python(source, ns, line):
    line = line.strip()
    if line:
        try: exec compile(line, source, 'single') in ns, ns
        except:
            traceback()

    return True

def heartbeat(timeslice = 0.1):
    # Start NOW!
    start = now()
    yield

    while True:
        dur = now() - start
        start += dur

        if dur > timeslice:
            dur = (timeslice - abs(dur % timeslice))
        else:
            dur = timeslice - dur

        sleep(dur)
        yield
