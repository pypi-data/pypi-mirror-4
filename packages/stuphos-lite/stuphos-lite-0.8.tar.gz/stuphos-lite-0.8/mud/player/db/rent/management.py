'Implements the events invoked from Crash_ in objsave.'
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

def deleteRentFile(name, info, filename):
    world.corelog('(DeletingRent:%s:%s)' % (name, filename))
    # showRentInfo(info)

from new import instancemethod as bind

class RentManagement:
    msgfmt = '(PC) %(Name)s %(Code)s%(Action)s from %(Filename)r at [%(Timestamp)s]'

    def loadNotifiers(self, a):
        'Load the rent handlers.'
        def logAction(action, player, info, filename):
            info = self.unpackRentInfo(info)
            info = {'Name':player.name, 'Code':info[0], 'Action':action,
                    'Timestamp':info[1], 'Filename':filename}

            world.corelog(self.msgfmt % info)

        a.rentStart       = lambda *args:logAction('SaveStart',    *args)
        a.rentComplete    = lambda *args:logAction('SaveComplete', *args)
        a.unrentStart     = lambda *args:logAction('LoadStart',    *args)
        a.unrentComplete  = lambda *args:logAction('LoadComplete', *args)

    __init__ = loadNotifiers

    from struct import unpack
    unpack = staticmethod(unpack)

    # time, code, perdiem, gold, acct, nitems, <8 spares>
    structfmt_rent_info = '14i'
    rent_info_member_names = ('time', 'code', 'perdiem', 'gold', 'acct', 'nitems')

    rent_codes = { 1: 'Crash', 2: 'Rented', 4: 'Forced', 5: 'Timed-Out' }

    from time import ctime
    ctime = staticmethod(ctime)

    def unpackRentInfo(self, info):
        'Unpack the rent_info buffer and parse rent-code, time.'
        data = self.unpack(self.structfmt_rent_info, str(info))

        # 2-tuple
        return (self.rent_codes.get(data[1]) or ('#%d ' % data[1]), self.ctime(data[0]))

        # [for (x, n) in zip(data[:6], self.rent_info_member_names)]

