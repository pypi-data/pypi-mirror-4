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
import thread
import mud

from pprint import pprint
class ThreadingManager:
    def enqueueHeartbeatTask(self, peer, task, *args, **kwd):
        'Manages the creation/destruction/start/stop of the private shell heartbeat task instance and its messaging.'

        import world
        world.heartbeat.enqueueTask(self.withPeerHead, peer, task, *args, **kwd)

    def spawnTask(self, peer, task, *args, **kwd):
        '''
        spawn(<peer>, <task>, *args, **kwd)

        Processes a <task - 2nd arg> with *args and **kwd IN A SEPARATE THREAD.
        It posts the result to the heartbeat task by handling it in that context.

        If there's an error in the task (exception), show that to the player in
        the heartbeat thread.

        If the task succeeds, show the result to the player in the heartbeat.

        '''

        from sys import exc_info

        # wraps output/result/exception/toplevel in peer head anchored in heartbeat.
        def handleError(exc):
            mud.player.HandleCommandError(peer, exc)

        def handleResult(result):
            if result is not None:
                if type(result) is str:
                    peer.page(result)

                else:
                    try   : pprint(result, peer)
                    except: mud.player.HandleCommandError(peer, exc_info())

        def taskReport(task, args, kwd):
            # Thread tasks - processes invocation and posts an event task as response.
            try   : ev = handleResult, task    (*args, **kwd)
            except: ev = handleError,  exc_info(            )

            import world
            world.heartbeat.enqueueTask(*ev)

        return thread.start_new_thread(taskReport, (task, args, kwd))
