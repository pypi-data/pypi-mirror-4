# Initialize Management Services for Bootstrap.
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
from .services import AutoServices

class ManagementServices(AutoServices):
    CONFIG_OBJECT_NAME = 'MUD::Configuration'
    CONFIG_SECTION_NAME = 'Management'

    def loadPentacleServices(self, conf):
        from mud.runtime.pentacle import partner
        partner.bootPartnerAspect()

    def loadSessionAdapter(self, conf):
        from web.adapter.sessions import SessionManager
        SessionManager.get(create = True) # CreateFacility(SessionManager)

    def loadEmbeddedWebserver(self, conf):
        from web.stuph.embedded.service import DjangoService
        DjangoService.get(create = True) # CreateFacility(DjangoService)

    # Some lesser features.
    def loadSystemShell(self, conf):
        from mud.management import shell
        shell.SystemShell.get(create = True)
        # CreateFacility(shell.SystemShell)

    def loadSubdaemonManager(self, conf):
        from mud.management import subdaemon
        subdaemon.SubDaemonManager.get(create = True)
        # CreateFacility(subdaemon.SubDaemonManager)

    def loadSyslogScanner(self, conf):
        from mud.management import syslog

initForCore = ManagementServices(setup_deferred = True)
