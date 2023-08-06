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
from mud.runtime import Object, Undefined
from mud.tasks import Procedure, Heartbeat, Scheduling, tasklog

# First-Class Formalization.
class Machine(Scheduling, Heartbeat, Object):
    class TimeUp(Procedure.Done):
        pass

    class Task(Procedure):
        class Quit(Procedure.Done):
            pass
        class Suspended(Procedure.Done):
            pass

        class Stack(list, Object):
            def push(self, item):
                self.append(item)
                return self
            __iadd__ = push

            def pop(self, nargs = 1):
                # Unconventional, confusing, obseleted:
                ##    if nargs == 1:
                ##        return list.pop(self)

                # I thought of returning a slice (and then deleting it),
                # but this returns things in the order that they're popped
                # (last in, first out)
                return tuple(list.pop(self) for x in xrange(nargs))
            __sub__ = pop

            def __isub__(self, nargs):
                self.pop(nargs)
                return self

        class Frame(Object):
            def __init__(self, procedure, locals = Undefined):
                self.procedure = procedure
                self.locals = {} if locals is Undefined else locals

                ##    from traceback import print_exc as traceback
                ##    self.exception = traceback

            def run(self, task):
                # Todo: Exception-handling!
                self.task = task
                return self.procedure.run(self)

                # This just loops infinitely... (because it doesn't raise Done??)
                ##    try: return self.procedure.run(self)
                ##    except: self.exception()

        def __init__(self):
            self.frames = self.Stack()
            self.stack = self.Stack()

        # Hopefully this operator can move up into Script and be renamed.
        def __iadd__(self, frame):
            if not self.Frame.instanceOf(frame):
                if type(frame) not in (tuple, list):
                    frame = (frame,)

                frame = self.Frame(*frame)

            self.frames.push(frame)
            return self
        __add__ = __iadd__

        def __isub__(self, frame):
            self.frames.remove(frame)
            return self
        __sub__ = __isub__

        def run(self, machine):
            # Run task within its timeslice.
            try:
                if break_task_run:
                    import pdb; pdb.set_trace()

            except NameError:
                pass

            try:
                with machine.schedule(self) as active:
                    while active(): # ..or sighandler raises exception in frame??
                        self.runFrame(self.frames[-1])

            # Wasn't able to run this pulse, but the scheduler is handling this.
            ##    except (machine.TimeUp, self.Done):
            ##        pass
            except machine.TimeUp:
                tasklog('time up')

            # End of Task.
            except self.Done:
                tasklog('done') # print 'frame raised done! %s' % self.scheduled
                return
            except Exception, e:
                tasklog('other exception:', e)
                return

            # Timeslice complete -- normal task regeneration.
            if self.frames:
                machine.Start(self)
                tasklog('regenerated, tasks:', len(machine.TaskQ.queue))
            else:
                tasklog('no more frames -- done')

        def runFrame(self, frame):
            # Frame the next instruction.
            return frame.run(self)

        def Start(self, machine, *args, **kwd):
            # Start self on machine.
            self.machine = machine
            machine.enqueueTask(self, *args, **kwd)

    def __iadd__(self, task):
        self.Start(task)
        return self

    def run(self, *args, **kwd):
        return self.pulse(*args, **kwd)

    __call__ = run

# Buildout Development.
def evaluate(procedure, *args, **kwd):
    try:
        while True:
            procedure.run(*args, **kwd)

    except procedure.Done:
        pass
