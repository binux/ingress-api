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

    def __init__(self, info):
        self.info = info

    @property
    def type(self):
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
    def __init__(self, info):
        self.info = info

    @property
    def latlng(self):
        location = self.info.get('locationE6')
        if not location:
            return None
        return utils.LatLng(location['latE6']*1e-6, location['lngE6']*1e-6)

class Ingress(object):
    hack_range = 40
    energyGlobGuids_limit = 100
    pickup_limit = 40
    fake_cell = '358b400000000000'

    def __init__(self, speed_limit=15.0):
        self.api = api.IngressAPI()
        self.latlng = None
        self.arrive_time = 0
        self.speed_limit = speed_limit
        self.session = database.Session()

        self.nickname = None
        self.player_id = None
        self.player_team = None
        self.player_info = {}
        self.max_energy = 0
        self.knobSyncTimestamp = 0

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
        self.inventory = {}
        self.inventory_update = 0
        if ret['result']['pregameStatus']['dialogText']:
            logging.error(ret['result']['pregameStatus'] )
            raise Exception

    def goto(self, to, wait=True):
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
        ret = self.api.playerUndecorated_getPaginatedPlexts(
                [self.fake_cell, ],
                knobSyncTimestamp=self.knobSyncTimestamp,
                playerLocation=self.at())
        self.updateGameBasket(ret.get('gameBasket'))
        return ret

    def hack(self, portal):
        assert self.latlng
        if utils.LatLng(portal.latE6*1e-6, portal.lngE6*1e-6) - self.latlng > self.hack_range:
            return None
        ret = self.api.gameplay_collectItemsFromPortal(
                portal.guid,
                knobSyncTimestamp=self.knobSyncTimestamp,
                playerLocation=self.at())
        self.updateGameBasket(ret.get('gameBasket'))
        return ret

    def scan(self, meters=100):
        #find cells
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
        return ret.get('gameBasket', {})

    def collect_xm(self, nearby=None):
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

        if nearby is None:
            nearby = self.scan()
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
        ret = self.api.gameplay_dropItem(
                item,
                playerLocation=self.at())
        self.updateGameBasket(ret.get('gameBasket'))
        return ret

    def pickup(self, nearby=None):
        if nearby is None:
            nearby = self.scan()
        items = []
        for guid, _, info in nearby.get('gameEntities', []):
            if Item.is_item(info):
                item = Item(info)
                if self.latlng - item.latlng > self.pickup_limit:
                    continue
                ret = self.api.gameplay_pickUp(
                        guid,
                        knobSyncTimestamp=self.knobSyncTimestamp,
                        playerLocation=self.at())
                self.updateGameBasket(ret.get('gameBasket'))
                for _guid, _, _info in ret.get('gameBasket', {}).get('inventory', []):
                    items.append(self.inventory.get(_guid) or Item(_info))
        return items

    def updateGameBasket(self, basket):
        if not basket:
            return
        if basket.get('knobBundleUpdate'):
            self.knobSyncTimestamp = basket['knobBundleUpdate']['syncTimestamp']
        if basket.get('playerEntity'):
            self.player_info = basket['playerEntity'][2]['playerPersonal']
            self.max_energy = max(self.max_energy, self.player_info['energy'])
        if basket.get('deletedEntityGuids'):
            for each in basket['deletedEntityGuids']:
                if each in self.inventory:
                    del self.inventory[each]
        if basket.get('inventory'):
            for guid, uptime, info in basket['inventory']:
                self.inventory[guid] = Item(info)

    def update_inventory(self):
        ret = self.api.playerUndecorated_getInventory(self.inventory_update)
        self.inventory_update = int(ret.get('result'))
        self.updateGameBasket(ret.get('gameBasket'))
        return ret

    def at(self):
        self.arrive_time = time.time()
        return self.latlng
