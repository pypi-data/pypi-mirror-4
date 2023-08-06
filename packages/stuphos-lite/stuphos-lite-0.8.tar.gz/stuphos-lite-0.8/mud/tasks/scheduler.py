# Implements timeslicing for the virtual machine (and heartbeat).
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
from mud.tasks.heartbeat import Heartbeat
from mud.tasks import tasklog
from mud.tools import ordereddict

from time import time as getCurrentSystemTime
import contextlib

class CooperativeVT: # (RealtimeAPI)
    # POSIX Virtual Timer against machine multi-task schedule.
    # Timeslice should adapt to current machine load including prioritization.
    # Virtual timer implemented here in cooperation with all other tasks/system operations.
    class Schedule:
        def __init__(self, machine, task):
            self.machine = machine
            self.task = task
            self.activate()

        def isActive(self):
            return False

        # Todo: enable virtual timer.
        # !! Use machine/heartbeat's VTPool parent API !!
        def activate(self):
            pass
        def deactivate(self):
            pass

    @contextlib.contextmanager
    def schedule(self, task):
        yield self.Schedule(self, task).isActive

class Pulse:
    # Heartbeat Pulse Timeslice Scheduling.
    OPT_SEC = 0.1
    def calculateTimeslice(self): # todo: rename to calculateEndTime
        # Crude, but the gist.
        return getCurrentSystemTime() + self.OPT_SEC

    def pulseStart(self, *args):
        self.startOfPulseEpoch = getCurrentSystemTime()
        self.endOfPulseTime = self.calculateTimeslice()
    def pulseEnd(self, exc = None):
        if exc:
            import traceback
            traceback.print_exception(*exc)

        del self.startOfPulseEpoch
        del self.endOfPulseTime

    def withinPulseTimeslice(self):
        # return getCurrentSystemTime() < self.endOfPulseTime
        remaining = self.endOfPulseTime - getCurrentSystemTime()
        tasklog('pulse:', remaining)
        return remaining > 0

class RoundRobin(Pulse):
    # Single-instruction timeslicing:
    class OnceAround:
        def __init__(self):
            self.nonce = True
        def __call__(self):
            try: return self.nonce
            finally: self.nonce = False

    @contextlib.contextmanager
    def schedule(self, task):
        yield self.OnceAround()

class Timesliced(Pulse):
    # Simply execute until the slice is up!
    @contextlib.contextmanager
    def schedule(self, task):
        endTime = getCurrentSystemTime() + self.getTimeslice(task)
        def checkRunningTime():
            return getCurrentSystemTime() < endTime

        yield checkRunningTime

    OPT_SEC = 0.1
    def getTimeslice(self, task):
        return self.OPT_SEC

class CooperativeSegmentation(Pulse):
    # provide adaptive, cooperative timeslices per frame of pulse.
    # a frame of pulse actually segments the pulse into activated
    # runtime schedules.  This means that there could be multiple
    # segments in the pulse where tasks are scheduled to run
    # multiple times.

    HARD_OVERHEAD = 0.004
    ALLOWANCE = 0.008
    SOFT_OVERHEAD = HARD_OVERHEAD + ALLOWANCE
    MINIMA = 0.01

    @contextlib.contextmanager
    def schedule(self, task):
        # Build schedule:
        startOfTimesliceEpoch = getCurrentSystemTime()
        remaining = self.endOfPulseTime - startOfTimesliceEpoch

        total = remaining - self.SOFT_OVERHEAD
        if total <= 0:
            # Do not complete this schedule.
            raise self.TimeUp

        try:
            if break_task_run:
                import pdb; pdb.set_trace()

        except NameError:
            pass

        # todo: adapt minimum allowed timeslice from remaining, given heavy load (lots of runningTasks)
        if not self.segments:
            tasklog('no segments!')
            yield (lambda:False)
            return

        runningTasks = len(self.segments[0])
        timeslice = float(total) / runningTasks

        # lame
        timeslice = max(timeslice, self.MINIMA)

        # is this cell shared? XXX
        ##    end = startOfTimesliceEpoch + timeslice
        ##    def withinCurrentTimeslice():
        ##        # Native calls should be able to interrupt this so that they can yield
        ##        # to following tasks they may be relying on, just because they're being
        ##        # kind, or because they've suspended completely.
        ##
        ##        remaining = end - getCurrentSystemTime()
        ##        # print 'timeslice:', remaining
        ##        if remaining > 0:
        ##            return True

        class Timeslice:
            def __init__(self, end):
                self.end = end
            def __call__(self):
                remaining = self.end - getCurrentSystemTime()
                tasklog('timeslice:', remaining)
                return remaining > 0

        withinCurrentTimeslice = Timeslice(startOfTimesliceEpoch + timeslice)

        # Yield context.
        try: yield withinCurrentTimeslice
        finally: self.scheduleComplete(task)

    # XXX proper segmentation management?
    # todo: rewrite schedule segments into task objects instead of using a dictionary.
    def scheduleTask(self, task):
        try: segments = self.segments
        except AttributeError:
            self.segments = segments = []

        nr = 0
        for s in segments:
            try:
                if s[task]:
                    tasklog('already scheduled this segment')
                    return

            except KeyError:
                tasklog('scheduled segment', nr, 'already scheduled:', getattr(task, 'scheduled', False))
                s[task] = True
                task.scheduled = True
                return

            nr += 1
            continue
            if s.setdefault(task, True):
                # If it's already pending or not yet exists in this segment, we're done.
                # Otherwise, it already ran in this segment, so keep searching.
                return

        # Create new segment.
        tasklog('new segment, already scheduled:', getattr(task, 'scheduled', False))
        seg = ordereddict()
        seg[task] = True
        task.scheduled = True
        segments.append(seg)

    def scheduleComplete(self, task):
        for s in self.segments:
            if s.get(task):
                # No longer pending.
                tasklog('completing schedule')
                s[task] = False
                task.scheduled = False
                break

    # Lifecycle Provision.
    def pulseStart(self, *args):
        Pulse.pulseStart(self, *args)

        import mud
        e = mud.tools.timing.Elapsed()

        tasklog('pulse-start')
        # Regenerate tasks that were scheduled for run last pulse but didn't have time: Try again.
        try: pending = self.pendingSchedules
        except AttributeError: pass
        else:
            if pending:
                tasklog('pending:', len(pending))

            for task in pending:
                # self.Start(task)
                self.scheduleTask(task)

        self.pendingSchedules = []
        tasklog('rescheduling:', e)
        tasklog('tasks:', sum(map(len, getattr(self, 'segments', []))))
        tasklog('queued:', len(self.TaskQ.queue))

    def pulseEnd(self, exc = None):
        Pulse.pulseEnd(self, exc)

        tasklog('pulse-end')
        # Dump scheduled tasks that didn't run back into the regeneration list.
        def regenerateTasks(segments):
            nr = 0
            done = 0
            for s in segments:
                for (task, pending) in s.iteritems():
                    nr += 1
                    if pending:
                        yield task
                    else:
                        done += 1

            tasklog('segmented-tasks: nr/done:', nr, '/', done)

        def collectTasks(segments):
            # build ordered set.
            result = []
            for task in regenerateTasks(segments):
                if task not in result:
                    result.append(task)

            return result

        # Todo: Maybe these could be factored together with the appropriate algorithm:
        # this would really cut down on overhead alot (not having to breakdown/rebuild schedules)!!!!
        # this might be absolutely necessary since overhead can choke the whole system...
        segments = getattr(self, 'segments', [])
        if segments:
            tasklog('segments:', len(segments))
            tasklog('tasks:', sum(map(len, segments)))
            tasklog('queued:', len(self.TaskQ.queue), (', '.join(map(repr, self.TaskQ.queue)))[:100])

            self.pendingSchedules = collectTasks(segments)
            if self.pendingSchedules:
                tasklog('pending-schedules:', len(self.pendingSchedules))
        else:
            self.pendingSchedules = []

        self.segments = []

    # Provide VM task start mechanism.
    def Start(self, task, *args, **kwd):
        # Schedule and start task with this machine.
        self.scheduleTask(task)
        task.Start(self, *args, **kwd)

Scheduling = CooperativeSegmentation # Timesliced # RoundRobin # CooperativeVT
