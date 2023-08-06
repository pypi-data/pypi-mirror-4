# MUD Runtime.
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
class Facility:
    # Generic.
    # XXX Abstract!
    NAME = 'Default::Facility'
    AUTOCREATE = False # todo: metaclass
    AUTOMANAGE = False # todo: metaclass
    COMPONENT = False

    @classmethod
    def get(self, create = False):
        from mud.runtime.registry import getObject
        return getObject(self.NAME, create = \
                         create and self.create)

    @classmethod
    def create(self):
        if self.COMPONENT:
            from mud.runtime import newComponent
            return newComponent(self)

        return self()

    @classmethod
    def CreateNew(self, andManage = False):
        cell = [False]
        def creationWrapper():
            result = self.create()
            cell[0] = True # Only signal if creation succeeded.
            return result

        # Create and track if it's new or not.
        from mud.runtime.registry import getObject
        getObject(self.NAME, create = creationWrapper)

        if andManage:
            self.manage()

        return cell[0]

    @classmethod
    def destroy(self):
        from mud.runtime.registry import delObject
        return delObject(self.NAME)

    @classmethod
    def manage(self, *args, **kwd):
        # This should address the derived manager on the derived Facility.
        return self.Manager(self, *args, **kwd)

    def getStatus(self):
        return str(self)

    # XXX Eww.. a command manager in runtime.facilities?  Should go in mud.player...
    class Manager:
        IMPLEMENTOR = 115

        MINIMUM_LEVEL = IMPLEMENTOR
        VERB_NAME = '*'

        def __init__(self, facility):
            self.facility = facility

            from mud.player import ACMD
            if self.VERB_NAME and self.VERB_NAME not in ['*']:
                assignCommand = ACMD(self.VERB_NAME)
                self.doCommand = assignCommand(self.doCommand)

        def doCommand(self, peer, cmd, args):
            if peer.avatar and peer.avatar.level >= self.MINIMUM_LEVEL:
                largs = args and args.strip().lower() or ''
                args = args and args.split() or ()

                try:
                    if not largs or args[0] in ['show', 'status']:
                        instance = self.facility.get()
                        if instance is not None:
                            peer.page_string(instance.getStatus())
                        else:
                            print >> peer, 'Not installed.'

                    elif args[0] == 'start':
                        print >> peer, self.facility.get(create = True)
                    elif args[0] in ['stop', 'destroy']:
                        print >> peer, self.facility.destroy() and \
                              'Destroyed.' or 'Unknown facility.'
                    elif not self.doSubCommand(peer, cmd, args):
                        print >> peer, "Unknown command: '%s'" % largs

                except RuntimeError, e:
                    print >> peer, '&r%s&N' % e

                return True

        def doSubCommand(self, peer, parent, args):
            name = 'do_%s' % (args[0],)
            subcmd = getattr(self, name, None)

            if callable(subcmd):
                subcmd(peer, parent, args[1:])
                return True

            try: usage = self.usage
            except AttributeError: pass
            else: peer.page_string(usage(peer, args))

        def do_help(self, peer, cmd, args):
            from mud.tools import columnize, capitalize
            subcmds = [attr[3:] for attr in dir(self) if attr.startswith('do_')]
            longest = max(map(len, subcmds))

            PAGE_WIDTH = 80
            title = self.VERB_NAME.replace('*', '')
            title = '-'.join(map(capitalize, title.split('-')))
            title = title + ' Subcommands'
            peer.page_string('&y%s&N\r\n&r%s&N\r\n\r\n%s' % \
                             (title, '=' * len(title),
                              columnize(subcmds, PAGE_WIDTH / longest - 1, longest + 4)))

def CreateFacility(facilityClass, andManage = False):
    # Idiom.  Todo: andManage
    facility = facilityClass.get(create = True)
    if getattr(facility, 'AUTOMANAGE', False):
        facility.manage()

    return facility

def LoadFacility(facilityFQN):
    # LoadFacility('web.adapter.session.SessionManager')
    facilityFQN = facilityFQN.split('.')
    module = __import__('.'.join(facilityFQN[:-1]), globals(), locals(), fromlist = [''])
    return CreateFacility(getattr(module, facilityFQN[-1]))
