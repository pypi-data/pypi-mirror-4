# World-Class Serialization.
 #-
 # Copyright (c) 2003 - 2013 Clint Banis (hereby known as "The Author")
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
from mud.tools import fromJsonFile, fromJsonString, toJsonFile, toJsonString

# Affected by equipments:
# ['aff_charisma', 'aff_constitution', 'aff_dexterity', 'aff_intelligence',
#  'aff_strength', 'aff_strength_addition', 'aff_wisdom']
# ['armorclass', 'damroll', 'hitroll']
# ['carry_items', 'carry_weight']
# ['breath', 'height', 'weight']

BASIC_MOBILE_DATA = ['alignment', 'attack_type', 'charisma', 'constitution',
                     'damnodice', 'damsizedice', 'default_pos', 'description', 'dexterity',
                     'experience', 'gold_on_hand', 'intelligence', 'last_dir',
                     'level', 'long_descr', 'name', 'position', 'sex', 'short_descr',
                     'strength', 'strength_addition', 'timer', 'track_timer', 'waitState',
                     'walk_type', 'was_in_room', 'wisdom', 'affections']

BASIC_ITEM_DATA =  ['detailed_description', 'exdescs', 'keywords', 'name',
                    'room_description', 'type', 'value1', 'value2', 'value3', 'value4']

VERSION = 1

class RealWorld:
    def __init__(self):
        from world import zone, room, item, mobile, iterate_entities
        from world.player import players
        from game import syslog
        self.RealZone = zone
        self.RealRoom = room
        self.ItemPrototype = item
        self.MobilePrototype = mobile
        self.IterateEntities = iterate_entities
        self.PlayingConnections = players
        self.syslog = syslog

class WorldFreezer(RealWorld):
    CRITERIA = ['exits', 'combat', 'empty_zones', 'all']
    def __init__(self, options):
        RealWorld.__init__(self)
        self.version = VERSION

        # Initialize criteria.
        for n in self.CRITERIA:
            setattr(self, n, False)

        # Detect general criteria.
        if options.complete or options.world == 'complete':
            for n in self.CRITERIA:
                setattr(self, n, True)

        # Set specific criteria.
        elif options.world:
            for n in options.world.split(','):
                if n in self.CRITERIA:
                    setattr(self, n, True)

        self.item_ref = {}
        self.mobile_ref = {}
        self.player_ref = {}

    def nextItemId(self, item):
        try: return self.item_ref[item]
        except KeyError:
            nr = self.item_ref[item] = len(self.item_ref)
            return nr

    def nextMobileId(self, mobile):
        try: return self.mobile_ref[mobile]
        except KeyError:
            nr = len(self.mobile_ref)
            if mobile.isPlayer:
                nr = -nr

            self.mobile_ref[mobile] = nr
            return nr

    def getItemId(self, item):
        return self.item_ref.get(item)
    def getMobileId(self, mobile):
        return self.mobile_ref.get(mobile)

    def getPlayerData(self, player):
        nr = self.nextMobileId(player)
        try: return self.player_ref[nr]
        except KeyError:
            data = self.player_ref[nr] = {'idnum': player.idnum,
                                          'name': player.name}
            return data

    def flagSet(self, name, instance, prototype):
        instance = getattr(instance, name).set
        if prototype is None:
            return instance

        prototype = getattr(prototype, name).set
        return list(set(instance).difference(prototype))

    def doFlagSet(self, data, name, *args):
        value = self.flagSet(name, *args)
        if value:
            data[name] = value

    def doMaxValueSet(self, data, name, instance):
        maxname = 'max_%s' % name
        v = getattr(instance, name)
        max = getattr(instance, maxname)
        if v != max:
            data[name] = v
            data[maxname] = max

    ##    def doItemValueSet(self, data, item, prototype):
    ##        if prototype is not None:
    ##            for n in xrange(1, 5):
    ##                n = 'value%d' % n
    ##                v1 = getattr(item, n)
    ##                v2 = getattr(prototype, n)
    ##                if v1 != v2:
    ##                    data[n] = v1
    ##
    ##        else:
    ##            for n in xrange(1, 5):
    ##                n = 'value%d' % n
    ##                data[n] = getattr(item, n)

    def itemData(self, item):
        # Get basic item data.  Filter out prototypical-similarities.
        data = {}
        prototype = item.prototype
        for n in BASIC_ITEM_DATA:
            try:
                v = getattr(item, n)
                if getattr(prototype, n) != v:
                    data[n] = v

            except AttributeError:
                pass

        # Now add in more complex data.
        # self.doItemValueSet(data, item, prototype)

        self.doFlagSet(data, 'anticlass', item, prototype)
        self.doFlagSet(data, 'antiflags', item, prototype)
        self.doFlagSet(data, 'extraflags', item, prototype)
        self.doFlagSet(data, 'wearflags', item, prototype)

        contents = map(self.itemData, item.contents)
        if contents: data['contents'] = contents

        # writing (mail, note, etc.)

        if prototype is not None:
            data['vnum'] = item.vnum

        data['instance.id'] = self.nextItemId(item)
        return data

    def npcData(self, mobile):
        # Get basic mobile data. Filter out prototypical-similarities.
        data = {}
        prototype = mobile.prototype
        for n in BASIC_MOBILE_DATA:
            try:
                v = getattr(mobile, n)
                if getattr(prototype, n) != v:
                    data[n] = v

            except AttributeError:
                pass

        # Now add in more complex data.
        self.doFlagSet(data, 'affectflags', mobile, prototype)
        self.doFlagSet(data, 'npcflags', mobile, prototype)

        self.doMaxValueSet(data, 'fatigue', mobile)
        self.doMaxValueSet(data, 'hit', mobile)
        self.doMaxValueSet(data, 'mana', mobile)

        for n in ('opponent', 'master', 'holding', 'mount'):
            o = getattr(mobile, n)
            if o:
                data[n] = self.nextMobileId(o)

        inventory = map(self.itemData, mobile.inventory)
        if inventory: data['inventory'] = inventory

        if mobile.tracking >= 0:
            data['tracking'] = mobile.tracking

        # equipment

        # If any specific data is available, then generate new instance.id
        if data or self.all:
            # Vnum is always present, directly.
            data['vnum'] = mobile.vnum
            data['instance.id'] = self.nextMobileId(mobile)
            return data

    def playerData(self, player):
        o = player.opponent
        if o and self.combat:
            data = self.getPlayerData(player)
            data['opponent'] = self.nextMobileId(o)

    def mobileData(self, mobile):
        if mobile.npc:
            return self.npcData(mobile)

        return self.playerData(mobile)

    def isHouse(self, room):
        return bool(room.house) and room.flags.House

    BASIC_EXIT_STATE = set(['Closed', 'Locked'])

    def roomData(self, room):
        items = None
        if not self.isHouse(room):
            items = [i for i in (self.itemData(i) for i in room.contents) if i]

        exits = None
        if self.exits:
            exits = ((e, self.BASIC_EXIT_STATE.intersection(e.flags.set)) for e in room.exits)
            exits = dict((e.direction, list(flags)) for (e, flags) in exits if flags)

        mobiles = [m for m in (self.mobileData(m) for m in room.people) if m]
        if items or mobiles or exits:
            data = dict(vnum = room.vnum)
            if items:
                data['items'] = items
            if mobiles:
                data['mobiles'] = mobiles
            if exits:
                data['exits'] = exits

            return data

    def isFreezable(self, zone):
        # Internal definition of is_empty:
        #   Linked player (with descriptor)
        #   in CON_PLAYING state
        #   must be level 105 or lower
        return self.empty_zones or not zone.empty

    def zoneData(self, zone):
        if self.isFreezable(zone):
            data = dict(vnum = zone.vnum, age = zone.age)
            rooms = [r for r in (self.roomData(r) for r in zone.rooms) if r]
            if rooms:
                data['rooms'] = rooms

            return data

    def iterateZones(self):
        return self.IterateEntities(self.RealZone)

    def dump(self):
        from world import iterent, zone as ZoneType
        players = self.player_ref
        zones = [z for z in (self.zoneData(z) for z in self.iterateZones()) if z]

        data = dict(version = self.version)
        if players:
            data['players'] = players
        if zones:
            data['zones'] = zones

        return data

class WorldUnfreezer(RealWorld):
    def __init__(self):
        RealWorld.__init__(self)
        self.item_ref = {}
        self.mobile_ref = {}

    def doSetFlags(self, bitv, flags):
        if flags:
            for f in flags:
                setattr(bitv, f, True)

    def restoreItem(self, location, data):
        try: vnum = data['vnum']
        except KeyError:
            # XXX oldgen not implemented
            self.syslog("COPYOVER: OLDGEN Object not supported <%d>!" % data['instance.id'])
            return

        warned_of = set()
        item = self.ItemPrototype(vnum).new(location)
        for name in BASIC_ITEM_DATA:
            try: setattr(item, name, data[name])
            except KeyError:
                pass
            except AttributeError:
                # Note: the AttributeError is for non-writable binding members.
                if name not in warned_of:
                    warned_of.add(name)
                    self.syslog('COPYOVER: Non-Writable Mobile Attribute: %s' % name)

        for name in xrange(1, 5):
            name = 'value%d' % name

            try: setattr(item, name, data[name])
            except (KeyError, AttributeError):
                pass

        for name in ('anticlass', 'antiflags', 'extraflags', 'wearflags'):
            self.doSetFlags(getattr(item, name), data.get(name))

        self.item_ref[data['instance.id']] = (item, data)
        return item

    def restoreMobile(self, location, data):
        warned_of = set()
        mobile = self.MobilePrototype(data['vnum']).instantiate(location)
        for name in BASIC_MOBILE_DATA:
            try: setattr(mobile, name, data[name])
            except KeyError:
                pass
            except AttributeError:
                # Note: the AttributeError is for non-writable binding members.
                if name not in warned_of:
                    warned_of.add(name)
                    self.syslog('COPYOVER: Non-Writable Item Attribute: %s' % name)

        for name in ('affectflags', 'npcflags'):
            self.doSetFlags(getattr(mobile, name), data.get(name))

        for name in ('fatigue', 'hit', 'mana', 'max_fatigue', 'max_hit', 'max_mana'):
            try: setattr(mobile, name, data[name])
            except KeyError:
                pass
            except AttributeError:
                self.syslog('COPYOVER: Non-Writable Mobile Attribute: %s' % name)

        self.mobile_ref[data['instance.id']] = (mobile, data)
        return mobile

    def restoreRoom(self, room, data):
        # todo: traverse these things backwards...
        for item in data.get('items') or []:
            self.restoreItem(room, item)
        for mobile in data.get('mobiles') or []:
            self.restoreMobile(room, mobile)

        for (exit, state) in data.get('exits', {}).iteritems():
            exit = getattr(room, exit)
            if exit is not None:
                self.doSetFlags(exit.flags, state)

    def findLoadedPlayerByIdnum(self, idnum):
        for player in self.PlayingConnections():
            if player.avatar and player.avatar.idnum == idnum:
                return player.avatar

    def restorePlayers(self, players):
        ref = {}
        if players:
            for (nr, data) in players.iteritems():
                loaded = self.findLoadedPlayerByIdnum(data['idnum'])

                assert loaded
                assert loaded.name == data['name']
                ref[nr] = loaded

                try: loaded.opponent = self.mobile_ref[data['opponent']][0]
                except IndexError:
                    pass

        return ref

    def load(self, data):
        for zone in data.get('zones') or []:
            real_zone = self.RealZone(zone['vnum'])
            real_zone.age = zone['age']

            for room in zone.get('rooms') or []:
                self.restoreRoom(self.RealRoom(room['vnum']), room)

        # Now fixup references.
        player_ref = self.restorePlayers(data.get('players'))

        for (nr, (mobile, data)) in self.mobile_ref.iteritems():
            for attribute in ('opponent', 'master', 'holding', 'mount'):
                try: o = data[attribute]
                except KeyError: pass
                else:
                    if o >= 0: o = self.mobile_ref[o][0]
                    else: o = player_ref[o]

                    try: setattr(mobile, attribute, o)
                    except AttributeError:
                        # Note: the AttributeError is for non-writable binding members (or values).
                        self.syslog('COPYOVER: Non-writable Mobile Attribute: %s' % attribute)

            try: o = data['tracking']
            except KeyError: pass
            else: mobile.tracking = o

            try: inventory = data['inventory']
            except KeyError: pass
            else:
                # todo: reverse order??
                for item in inventory:
                    self.restoreItem(mobile, item)

            # todo: equipment

        all_item_ref = {}
        while self.item_ref:
            item_ref = self.item_ref
            self.item_ref = {}

            # Save master copy.
            all_item_ref.update(item_ref)

            for (nr, (item, data)) in item_ref.iteritems():
                try: contents = data['contents']
                except KeyError: pass
                else:
                    # todo: reverse order??
                    for contained in contents:
                        self.restoreItem(item, contained)

        self.item_ref = all_item_ref

# Programming Interface.
def getCmdlnParser():
    from optparse import OptionParser
    parser = OptionParser(prog = 'copyover')
    parser.add_option('--world')
    parser.add_option('--complete', action = 'store_true')

    parser.add_option('--format')
    parser.add_option('--analyze', action = 'store_true')
    return parser

def getValidCmdlnOptions(args):
    from mud.tools import parseOptionsOverSystem
    parser = getCmdlnParser()
    (options, args) = parseOptionsOverSystem(parser, args)

    if args:
        # This form of invocation doesn't accept non-option arguments,
        # so print usage and do a conventional parser-abort.
        parser.print_help()
        raise SystemExit
    else:
        return options

def parseCmdln(args):
    from mud.tools import parseOptionsOverSystem
    return parseOptionsOverSystem(getCmdlnParser(), args)

def getFormatHandler(filename, format = None):
    if format:
        try: return FORMATS[str(format).lower()]
        except KeyError: pass

    from os.path import splitext
    try: return FORMATS[splitext(filename)[1].lower()]
    except KeyError: pass

    return FORMATS['default']

class BinaryHandler:
    import marshal
    def loadFile(self, filename):
        return self.marshal.loads(open(filename).read().decode('base64').decode('zlib'))
    def dumpFile(self, data, filename):
        open(filename, 'wt').write(self.marshal.dumps(data).encode('zlib').encode('base64'))

class PickledHandler:
    # XXX integers automatically converted to longs??
    import cPickle
    def loadFile(self, filename):
        return self.cPickle.load(open(filename))
    def dumpFile(self, data, filename):
        self.cPickle.dump(data, open(filename, 'wt'))

class JsonHandler:
    def loadFile(self, filename):
        return fromJsonFile(open(filename))
    def dumpFile(self, data, filename):
        toJsonFile(data, open(filename, 'wt'))

class PythonHandler:
    import pprint
    def loadFile(self, filename):
        return eval(open(filename).read().strip().replace('\n', ''))
    def dumpFile(self, data, filename):
        self.pprint.pprint(data, open(filename, 'wt'))

FORMATS = dict(binary = BinaryHandler(),
               pickled = PickledHandler(),
               json = JsonHandler(),
               default = PythonHandler())

FORMATS[ '.bin'] = FORMATS[ 'binary']
FORMATS['.json'] = FORMATS[   'json']
FORMATS[ '.pkl'] = FORMATS['pickled']
FORMATS[  '.py'] = FORMATS['default']

def dumpFile(data, filename, format = None):
    return getFormatHandler(filename, format = format).dumpFile(data, filename)
def loadFile(filename, format = None):
    return getFormatHandler(filename, format = format).loadFile(filename)

def dumpWorldData(options):
    return WorldFreezer(options).dump()
def loadWorldData(data):
    return WorldUnfreezer().load(data)

# Testing.
def analyzeFreezeData(data):
    from world import mobile as MobilePrototype, room as RealRoom
    memo = {}
    for zone in data.get('zones') or []:
        for room in zone.get('rooms') or []:
            room_vnum = room['vnum']
            for mobile in room.get('mobiles') or []:
                vnum = mobile['vnum']
                memo.setdefault((vnum, room_vnum), []).append(mobile)

    for ((vnum, room), instances) in memo.iteritems():
        yield '%s: %s' % (RealRoom(room), MobilePrototype(int(vnum)))
        for data in instances:
            yield '    <%s>' % data['instance.id']
            for (name, value) in data.iteritems():
                if name not in ['vnum', 'instance.id']:
                    yield '      %s: %r' % (name, value)

def doFreezeWorld(peer, cmd, args):
    if peer.avatar and peer.avatar.level >= 115:
        import sys
        if not hasattr(sys, 'argv'):
            sys.argv = ['']

        try: (options, args) = parseCmdln(args)
        except SystemExit:
            return True

        filename = args and args[0] or 'data.py'
        format = getFormatHandler(filename, options.format)

        if options.analyze:
            data = format.loadFile(filename)
            peer.page_string('\r\n'.join(analyzeFreezeData(data)) + '\r\n')
        else:
            data = dumpWorldData(options)
            format.dumpFile(data, filename)

        return True

try: from mud.player import ACMD
except ImportError: pass
else: ACMD('freeze-w*orld')(doFreezeWorld)
