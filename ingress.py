#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2013-01-26 10:14:59

import time
import logging

import api
import utils
import database

class Item(object):
    @staticmethod
    def is_item(info):
        if 'resource' in info:
            return True
        elif 'resourceWithLevels' in info:
            return True
        elif 'modResource' in info:
            return True
        return False

    def __init__(self, guid, info):
        self.guid = guid
        self.info = info

    @property
    def type(self):
        """PORTAL_LINK_KEY, EMP_BURSTER, EMITTER_A, RES_SHIELD, MEDIA"""
        info = self.info
        return (info.get('resource')\
                    or info.get('resourceWithLevels')\
                    or info.get('modResource')).get('resourceType')

    @property
    def level(self):
        info = self.info
        return info.get('resourceWithLevels') and info['resourceWithLevels']['level']

    @property
    def portal_guid(self):
        info = self.info
        return info.get('portalCoupler') and info['portalCoupler']['portalGuid']

    @property
    def mitigation(self):
        info = self.info
        return info.get('modResource') and info['modResource']['stats']['MITIGATION']

    @property
    def rarity(self):
        info = self.info
        return info.get('modResource') and info['modResource']['rarity']

    @property
    def latlng(self):
        location = self.info.get('locationE6')
        if not location:
            return None
        return utils.LatLng(location['latE6']*1e-6, location['lngE6']*1e-6)

    def __repr__(self):
        if self.type == 'PORTAL_LINK_KEY':
            return '<PortalKey#%s>' % self.portal_guid
        elif self.type == 'EMP_BURSTER':
            return '<L%d Burster>' % self.level
        elif self.type == 'EMITTER_A':
            return '<L%d Resonator>' % self.level
        elif self.type == 'RES_SHIELD':
            return '<Shield:%s>' % self.rarity
        elif self.type == 'MEDIA':
            return '<L%d Media>' % self.level
        else:
            return repr(self.info)

class Portal(object):
    @staticmethod
    def  is_portal(info):
        if 'portalV2' in info:
            return True
        return False

    def __init__(self, guid, info):
        self.guid = guid
        self.info = info

    @property
    def latlng(self):
        location = self.info.get('locationE6')
        if not location:
            return None
        return utils.LatLng(location['latE6']*1e-6, location['lngE6']*1e-6)

    @property
    def controlling(self):
        return self.info['controllingTeam']['team']

    @property
    def image(self):
        return self.info.get('imageByUrl', {}).get('imageUrl')

    @property
    def title(self):
        info = self.info.get('portalV2')
        return info['descriptiveText']['TITLE']

    @property
    def links(self):
        info = self.info.get('portalV2')
        return info.get('linkedEdges', [])

    @property
    def mods(self):
        info = self.info.get('portalV2')
        return info.get('linkedModArray', [])

    @property
    def resonators(self):
        return self.info.get('resonatorArray', {}).get('resonators', [])

    @property
    def full(self):
        full = True
        for res in self.resonators:
            if not res:
                full = False
                break
        return full

    @property
    def level(self):
        return sum([x['level'] if x else 0 for x in self.resonators]) / 8.0

    @property
    def energy(self):
        return sum([x['energyTotal'] if x else 0 for x in self.resonators])

    def __repr__(self):
        return '<Portal#%s +%d @%s>' % (self.guid, self.level, self.latlng)

class Bag(object):
    PORTAL_LINK_KEY = PORTAL_KEY = 'PORTAL_LINK_KEY'
    EMP_BURSTER = BURSTER = 'EMP_BURSTER'
    EMITTER_A = RES = RESONATOR = 'EMITTER_A'
    RES_SHIELD = SHIELD = 'RES_SHIELD'
    MEDIA = 'MEDIA'

    def __init__(self):
        self.inventory = {}
        self.group = {}
        self.get = self.inventory.get
        self.keys = self.group

    def _group(self, item):
        type = item.type
        if type in ('EMP_BURSTER', 'EMITTER_A', 'MEDIA', ):
            return '%s|%s' % (type, item.level)
        elif type in ('RES_SHIELD', ):
            return '%s|%s' % (type, item.mitigation)
        elif type in ('PORTAL_LINK_KEY', ):
            return type
        else:
            return 'UNKNOW'

    def add(self, item):
        self.inventory[item.guid] = item
        group = self._group(item)
        self.group.setdefault(group, []).append(item.guid)

    def rm(self, guid):
        if guid not in self.inventory:
            return
        item = self.inventory[guid]
        group = self._group(item)
        del self.inventory[guid]
        self.group[group].remove(guid)

    def get_by_group(self, group, adding=None):
        if '|' in group:
            guid = self.group.get(group) and self.group[group][0]
            if not guid:
                return
            return self.inventory[guid]

        if not adding:
            if group in ('EMP_BURSTER', 'MEDIA', ):
                for i in xrange(8, 0, -1):
                    if self.group.get('%s|%s' % (group, i)):
                        guid = self.group['%s|%s' % (group, i)][0]
                        return self.inventory[guid]
            elif group in ('RES_SHIELD', 'EMITTER_A', ):
                for i in xrange(1, 11):
                    if self.group.get('%s|%s' % (group, i)):
                        guid = self.group['%s|%s' % (group, i)][0]
                        return self.inventory[guid]
            elif group == 'PORTAL_LINK_KEY':
                for guid in self.group[group]:
                    if self.inventory[guid].portal_guid == adding:
                        return self.inventory[guid]
        else:
            if group == 'PORTAL_LINK_KEY' and self.group.get(group):
                return self.group[group][0]
            else:
                return self.get_by_group('%s|%s' % (group, adding))

        return None

    def __len__(self):
        return len(self.inventory)

class Ingress(object):
    hack_range = 40
    energyGlobGuids_limit = 100
    pickup_limit = 40
    fake_cell = '358b400000000000'
    res_limit = [0, 8, 4, 4, 4, 2, 2, 1, 1, ]

    def __init__(self, speed_limit=15.0):
        self.api = api.IngressAPI()
        self.latlng = None
        self.arrive_time = 0
        self.speed_limit = speed_limit
        self.session = database.Session()
        self.bag = Bag()
        self.inventory_update = 0
        self.target = None

        self.nickname = None
        self.player_id = None
        self.player_team = None
        self.player_info = {}
        self.max_energy = 0
        self.knobSyncTimestamp = 0

    ap_level = list(reversed([0, 1, 3, 7, 15, 30, 60, 120]))
    @property
    def player_level(self):
        ap = int(self.player_info.get('ap', 0)) / 10000.0
        for i, need_ap in enumerate(self.ap_level):
            if ap >= need_ap:
                return 8-i
        return 0

    def login(self, cookie=None):
        #load default cookie
        if not cookie:
            try:
                cookie = open('cookie.api').read()
            except:
                pass
        ret = self.api.login(cookie)
        assert ret['result']['canPlay']
        self.nickname = ret['result']['nickname']
        self.player_id = ret['result']['playerEntity'][0]
        self.player_team = ret['result']['playerEntity'][2]['controllingTeam']['team']
        #u'ap': u'25309',
        #u'clientLevel': 9,
        #u'energy': 4000,
        #u'energyState': u'XM_OK',
        self.player_info = ret['result']['playerEntity'][2]['playerPersonal']
        self.max_energy = max(3000, self.player_info['energy'])
        if ret['result']['pregameStatus']['dialogText']:
            logging.error(ret['result']['pregameStatus'] )
            raise Exception

    def goto(self, to, wait=True):
        if hasattr(to, 'latlng'):
            to = to.latlng
        if not self.latlng:
            self.latlng = to
            return 0
        else:
            dist = to - self.latlng
            need_time = dist / self.speed_limit - time.time() + self.arrive_time

            #wait
            if need_time > 0 and wait:
                for i in range(0, int(need_time), 10):
                    time.sleep(min(need_time - i, 10))
                    move_distance = min(need_time - i, 10) * self.speed_limit
                    self.latlng = self.latlng.goto(to, move_distance)
                    self.report_location()

                need_time = 0

            if need_time <= 0:
                self.latlng = to
                need_time = 0
            return need_time

    def report_location(self):
        assert self.latlng
        ret = self.api.playerUndecorated_getPaginatedPlexts(
                [self.fake_cell, ],
                knobSyncTimestamp=self.knobSyncTimestamp,
                playerLocation=self.at())
        self.updateGameBasket(ret.get('gameBasket'))
        return ret

    def hack(self, portal=None):
        if portal is None:
            portal = self.target

        assert portal
        assert self.latlng
        assert portal.latlng - self.latlng <= self.hack_range

        ret = self.api.gameplay_collectItemsFromPortal(
                portal.guid,
                knobSyncTimestamp=self.knobSyncTimestamp,
                playerLocation=self.at())
        self.updateGameBasket(ret.get('gameBasket'))
        return ret

    def scan(self, meters=100):
        assert self.latlng

        #find cells
        sw = self.latlng.goto(225, meters)
        ne = self.latlng.goto(45, meters)
        cells = list(set([x[0] for x in self.session.query(database.GEOCell.cell)\
                    .filter(sw.lat*1e6 < database.GEOCell.latE6)\
                    .filter(database.GEOCell.latE6 < ne.lat*1e6)\
                    .filter(sw.lng*1e6 < database.GEOCell.lngE6)\
                    .filter(database.GEOCell.lngE6 < ne.lng*1e6).limit(40).all()]))
        if not cells:
            return []

        ret = self.api.gameplay_getObjectsInCells(
                cells,
                [0, ]*len(cells),
                knobSyncTimestamp=self.knobSyncTimestamp,
                playerLocation=self.at())
        self.updateGameBasket(ret.get('gameBasket'))
        result = []
        for guid, _, info in ret.get('gameBasket', {}).get('gameEntities', []):
            if Item.is_item(info):
                result.append(Item(guid, info))
            elif Portal.is_portal(info):
                result.append(Portal(guid, info))
        return result

    def deploy(self, item, portal=None, slot=255):
        if portal is None:
            portal = self.target
        if isinstance(item, Item):
            item = item.guid
        if isinstance(portal, Portal):
            portal = portal.guid
        if isinstance(item, basestring):
            item = [item, ]

        assert item
        assert portal
        assert self.latlng

        ret = self.api.gameplay_deployResonatorV2(
                item,
                portal,
                slot,
                knobSyncTimestamp=self.knobSyncTimestamp,
                location=self.at())
        self.updateGameBasket(ret.get('gameBasket'))
        return ret

    def upgrade(self, item, portal=None, slot=0):
        if portal is None:
            portal = self.target
        if isinstance(item, Item):
            item = item.guid
        if isinstance(portal, Portal):
            portal = portal.guid

        assert item
        assert portal
        assert self.latlng

        ret = self.api.gameplay_upgradeResonatorV2(
                item,
                portal,
                slot,
                knobSyncTimestamp=self.knobSyncTimestamp,
                location=self.at())
        self.updateGameBasket(ret.get('gameBasket'))
        return ret

    def add_mod(self, item, portal=None, index=0):
        if portal is None:
            portal = self.target
        if isinstance(item, Item):
            item = item.guid
        if isinstance(portal, Portal):
            portal = portal.guid

        assert item
        assert portal
        assert self.latlng

        ret = self.api.gameplay_addMod(
                item,
                portal,
                index,
                knobSyncTimestamp=self.knobSyncTimestamp,
                playerLocation=self.at())
        self.updateGameBasket(ret.get('gameBasket'))
        return ret

    def collect_xm(self, meters=100):
        assert self.latlng

        sw = self.latlng.goto(225, meters)
        ne = self.latlng.goto(45, meters)
        cells = list(set([x[0] for x in self.session.query(database.GEOCell.cell)\
                    .filter(sw.lat*1e6 < database.GEOCell.latE6)\
                    .filter(database.GEOCell.latE6 < ne.lat*1e6)\
                    .filter(sw.lng*1e6 < database.GEOCell.lngE6)\
                    .filter(database.GEOCell.lngE6 < ne.lng*1e6).limit(40).all()]))
        if not cells:
            return {}

        ret = self.api.gameplay_getObjectsInCells(
                cells,
                [0, ]*len(cells),
                knobSyncTimestamp=self.knobSyncTimestamp,
                playerLocation=self.at())
        self.updateGameBasket(ret.get('gameBasket'))
        nearby = ret.get('gameBasket', {})
        if not nearby.get('energyGlobGuids'):
            return {}

        ret2 = self.api.gameplay_getObjectsInCells(
                cells,
                [self.knobSyncTimestamp, ]*len(cells),
                energyGlobGuids=nearby['energyGlobGuids'][:self.energyGlobGuids_limit],
                knobSyncTimestamp=self.knobSyncTimestamp,
                playerLocation=self.at())
        self.updateGameBasket(ret2.get('gameBasket'))

        return ret2

    def drop(self, item):
        if isinstance(item, Item):
            item = item.guid

        assert item
        assert self.latlng

        ret = self.api.gameplay_dropItem(
                item,
                playerLocation=self.at())
        self.updateGameBasket(ret.get('gameBasket'))
        return ret

    def pickup(self, item):
        assert item
        assert self.latlng

        if item.latlng - self.latlng <= self.pickup_limit:
            ret = self.api.gameplay_pickUp(
                    item.guid,
                    knobSyncTimestamp=self.knobSyncTimestamp,
                    playerLocation=self.at())
            if ret.get('error'):
                logging.error(ret.get('error'))
            self.updateGameBasket(ret.get('gameBasket'))
            for _guid, _, _info in ret.get('gameBasket', {}).get('inventory', []):
                items.append(self.bag.get(_guid) or Item(guid, _info))
        return items

    def updateGameBasket(self, basket):
        if not basket:
            return
        if basket.get('knobBundleUpdate'):
            self.knobSyncTimestamp = basket['knobBundleUpdate']['syncTimestamp']
        for guid, _, info in basket.get('gameEntities', []):
            if self.target and self.target.guid == guid:
                self.target = Portal(guid, info)
        if basket.get('playerEntity'):
            self.player_info = basket['playerEntity'][2]['playerPersonal']
            self.max_energy = max(self.max_energy, self.player_info['energy'])
        if basket.get('deletedEntityGuids'):
            for guid in basket['deletedEntityGuids']:
                self.bag.rm(guid)
        if basket.get('inventory'):
            for guid, uptime, info in basket['inventory']:
                self.bag.add(Item(guid, info))
        if basket.get('levelUp'):
            level_up_msg = basket['levelUp']['newLevelUpMsgId']
            if getattr(self, '_level_up_msg', 0) != level_up_msg:
                self._level_up_msg = level_up_msg
                self.api.player_levelUp(level_up_msg)
        for each in basket.get('apGains', []):
            logging.info('%s +%saps' % (each['apTrigger'], each['apGainAmount']))
        for each in basket.get('playerDamages', []):
            logging.warning('%s -%sxms' % (each['weaponSerializationTag'], each['damageAmount']))

    def update_inventory(self):
        ret = self.api.playerUndecorated_getInventory(self.inventory_update)
        self.inventory_update = int(ret.get('result'))
        self.updateGameBasket(ret.get('gameBasket'))
        return ret

    def at(self):
        self.arrive_time = time.time()
        return self.latlng
