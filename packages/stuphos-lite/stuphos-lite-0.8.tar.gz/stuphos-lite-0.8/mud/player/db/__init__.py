'The player module is a relative of interaction, but contains just player persistant stuff.'
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
import mud, mud.player.db

# __all__ = ['scan', 'format', 'RecordObject', 'page', 'loadPlayerFile', 'DBRecord']
import new

from os.path import exists
from pprint import pprint, pformat

try:
    from pysqlite2.dbapi2 import connect as sqlite_connect
except:
    def sqlite_connect(*args):
        raise NotImplementedError

import playerfile
from mud.player.db.playerfile import *

DEFAULT_PLRFL = 'etc/players'
EXTENDED_BASE = 'plrfiles'

## Implement scanning tools
def scan():
    'Generates a source of player tuples.'
    from mud.player.db.playerfile import (read_player_entries, DEFAULT_PLRFL)
    return iter(read_player_entries(DEFAULT_PLRFL))

def format(i, ncol, fmt = '%-15.15r'):
    """
    Function that beautifies a sequence of player records i over f(or)m(a)t
    by generating lines of ncol(umns).

    """

    fmt = ' '.join([fmt] * ncol)

    for plr in i:
        if type(plr) is sequence:
            yield fmt % tuple(plr[:ncol])
        elif instanceof(plr, PlayerFile):
            yield fmt % tuple(plr.record[:ncol])
        else:
            raise TypeError # or pass

## Implementation of individualized player files:
# Pickled data that is saved to file by name in lib/plrfiles/X-X/name.pkl
# It can be installed into a player's avatar on world.enterGame.
#
# Make addressable by mud.persistance?  The registry mechanism could call
# back to the plrfiles FS defined here.  Configure getPlayerFileName

class PlayerFile(object):
    'map(PlayerFile, scan())'

    ## For looking up player-files.
    initialMap = {
        'a':'A-E', 'b':'A-E', 'c':'A-E', 'd':'A-E', 'e':'A-E',
        'f':'F-J', 'g':'F-J', 'h':'F-J', 'i':'F-J', 'j':'F-J',
        'k':'K-O', 'l':'K-O', 'm':'K-O', 'n':'K-O', 'o':'K-O',
        'p':'P-T', 'q':'P-T', 'r':'P-T', 's':'P-T', 't':'P-T',
        'u':'U-Z', 'v':'U-Z', 'w':'U-Z', 'x':'U-Z', 'y':'U-Z',

        'A':'A-E', 'B':'A-E', 'C':'A-E', 'D':'A-E', 'E':'A-E',
        'F':'F-J', 'G':'F-J', 'H':'F-J', 'I':'F-J', 'J':'F-J',
        'K':'K-O', 'L':'K-O', 'M':'K-O', 'N':'K-O', 'O':'K-O',
        'P':'P-T', 'Q':'P-T', 'R':'P-T', 'S':'P-T', 'T':'P-T',
        'U':'U-Z', 'V':'U-Z', 'W':'U-Z', 'X':'U-Z', 'Y':'U-Z',

        # 'z':'U-Z', 'Z':'U-Z',
    }

    from cPickle import load as loadext, dump as dumpext
    from os.path import join

    loadext = staticmethod(loadext)
    dumpext = staticmethod(dumpext)
    join = staticmethod(join)

    def pack(self, record = None):
        import mud.player.db.playerfile as plr
        return plr.pack(plr.pfilel_fmt, record or self.record)

    def __init__(self, record = None, player = None):
        self.record = record
        self.player = player

    def extendedFilename(self, player = None):
        ## Load a resource file into the avatar records.
        player = player or self.player

        if name is None:
            if type(player) is world.peer:
                player = player.avatar
            if type(player) is world.mobile:
                name = player.name

        assert name
        return join(EXTENDED_BASE, self.initialMap.get(name.lower()[0], 'ZZZ'), name, '.pkl')

    def applyExtendedRecord(self, record):
        'A sub-procedure of loading.'
        if record is None:
            record = self.record = self.loadExtendedRecord()

        player = self.player

        if type(record) is dict:
            # Update avatar dictionary
            for (k, v) in record.iteritems():
                if not k.startswith('_'):
                    setattr(player, k, v)
        elif type(record) not in (list, generator):
            # Rebind pack/tobuffer methods to record-cell
            packed = str(record)
            buf = buffer(packed)

            def pack():
                return packed
            def tobuffer():
                return buf

            self.pack = pack
            self.tobuffer = tobuffer
        else:
            record = tuple(record)

        if type(record) is tuple:
            # Rebind pack/tobuffer methods to record-cell 
            packrec = self.pack
            rec2buf = self.tobuffer

            def pack():
                return packrec(record)
            def tobuffer():
                return rec2buf(record)

            self.pack = pack
            self.tobuffer = tobuffer

    def loadExtendedRecord(self, player = None):
        '''
        playerfls = map(mud.player.db.PlayerFile, mud.player.db.scan())

        p = playerfls[0]
        p.applyExtendedRecord(p.loadExtendedRecord())

        '''

        return self.loadext(self.extendedFilename(player or self.player))

    def dumpExtendedRecord(self, player = None, record = None):
        fl = open(self.extendedFilename(player or self.player), 'w')
        self.dumpext(fl, record or self.record)
        fl.flush()
        fl.close()

    def __repr__(self):
        from itertools import izip as zip
        d = {}

        for (n, v) in zip(mud.player.db.playerfile.pfilel_names, self.record):
            d[n] = v

        from pprint import pformat as pf
        pf = pf(d).strip()

        return '<Player %r %s>' % (self.player and self.player.name or '', pf)

# Todo: subclass PlayerFile with a positional element interfacing the position-dependent
# functions in mud.player.db.playerfile with the positional record for full database access.

def page(peer, ncol = 6):
    'Peer-friendly output for paging the results of a single scan.'
    peer.page('\r\n'.join(map(str, format(scan(), ncol))))


## Implementation of SQL save-points.
CORRUPT_SAVE_POINT_DBFL = 'etc/players-corrupt.db'

def playerSavePoint_1(player, i):
    store_tuple = unpack_player(buffer(player.store))

    e = not exists(CORRUPT_SAVE_POINT_DBFL)
    c = sqlite_connect(CORRUPT_SAVE_POINT_DBFL)
    x = c.cursor().execute

    if e:
        # print 'No file %r, creating:' % CORRUPT_SAVE_POINT_DBFL
        # print playerfile.NEW_PLAYERS_TABLE

        x(playerfile.NEW_PLAYERS_TABLE)

    # print 'Executing and commiting SQL:'
    # print playerfile.NEW_PLAYER
    # print pformat(store_tuple)[:100]

    x(playerfile.NEW_PLAYER, store_tuple)
    c.commit()

    del x
    c.close()


## SQLObject interface.

from os.path import abspath

try:
    from sqlobject import sqlhub, connectionForURI
except:
    def connectionForURI(*args):
        raise NotImplementedError

DEFAULT_SAVEPOINT_DBFL = 'etc/players-sqlobject-2.db'

def cstring(s):
    i = s.find('\x00')
    if i >= 0:
        return s[:i]
    return s

def store2dict(store):
    from itertools import izip
    store_tuple = unpack_player(buffer(store))

    store_dict = {}
    for (n, v) in izip(playerfile.pfilel_names, store_tuple):
        store_dict[n] = v

    # Cleanse
    store_dict['skills']    = ''
    store_dict['talks']     = ''
    store_dict['affected']  = ''
    store_dict['color']     = ''

    # host should already be in clean form (take cstring then)
    store_dict['host']      = cstring(store_dict['host'])
    store_dict['name']      = cstring(store_dict['name'])
    store_dict['email']     = cstring(store_dict['email'])
    store_dict['pwd']       = cstring(store_dict['pwd'])

    store_dict['lastlogin'] = int(store_dict.get('lastlogin') or 0)

    return store_dict

def openPlayerStore(protocol = 'sqlite', path = DEFAULT_SAVEPOINT_DBFL, reload_schema = False):
    path = abspath(path)
    # e = exists(path)

    sqlhub.processConnection = \
        connectionForURI('%s:%s' % (protocol, path))

    import sql

    if reload_schema:
        reload(sql)

    if not sql.PlayerStore.tableExists():
        sql.PlayerStore.createTable()

    return sql.PlayerStore

def playerSavePoint(player, i):
    if 1:
        save_point = store2dict(player.store)
        save_point['save_point_indication'] = str(i)

        if player.peer:
            save_point['host'] = player.peer.host

        playerSave = openPlayerStore('sqlite', DEFAULT_SAVEPOINT_DBFL)

        # Save record
        playerSave(**save_point) # .id

    world.corelog('SAVE-POINT [%s (%s)]' % (player.name, i))

def loadPlayerStore(name, store, pfilepos):
    # Search Youngest Save Points (PlayerSave table) and extract information into store.
    # Do grouping sort into record-ids with compound select?
    #
    # playerStore = openPlayerStore()
    # lastSavePoint = playerStore.selectBy(name = name, orderBy = 'lastlogon', limit = 1).reversed()
    #
    # columns = playerStore.sqlmeta.columns.keys() or playerfile.pfilel_fmt
    # for n in columns:
    #   if hasattr(store, n):
    #       setattr(store, n, getattr(lastSavePoint, n))
    #
    #
    world.corelog('LOAD-STORE [%s (position #%d; length %d)]' % (name, pfilepos, len(buffer(store))))
    # return store
