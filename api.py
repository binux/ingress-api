#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2013-01-15 21:00:15

import re
import sys
import time
import json
import cmath
import utils
import logging
import requests

def hex_encode(num):
    if num < 0:
        num = abs(num)
        num = (num - 1) ^ 0xffffffff
        pass
    return '{0:0=8x}'.format(num)

def hex_decode(num):
    num = int(num, 16)
    if num & 0x80000000:
        return -((num ^ 0xffffffff) + 1)
    return num

class IngressAPI(object):
    basepath = 'https://m-dot-betaspike.appspot.com'
    #nemesisSoftwareVersion = '2012-12-20T21:55:07Z 887b00b46b68 opt'
    #nemesisSoftwareVersion = '2013-01-15T22:12:53Z ae145d098fc5 opt'
    nemesisSoftwareVersion = '2013-01-24T11:26:38Z bfb6a817656f opt'
    deviceSoftwareVersion = '4.1.1'

    def __init__(self):
        self.session = requests.session()
        self.session.headers = {
                'Accept-Encoding': 'gzip',
                'User-Agent': 'Nemesis (gzip)',
                }
        self.xsrf = None

    def login(self, cookie):
        if not cookie:
            print 'visite "https://www.google.com/accounts/ServiceLogin?service=ah&passive=true&continue=https://appengine.google.com/_ah/conflogin%3Fcontinue%3Dhttps%3A%2F%2Fm-dot-betaspike.appspot.com"'
            print 'get cookie SACSID of domain betaspike.appspot.com'
            cookie = raw_input('SACSID:')
        self.session.cookies['SACSID'] = cookie
        return self.handshake()

    def handshake(self):
        response = self.session.get(self.basepath+'/handshake', params={
            'json': json.dumps({
                'nemesisSoftwareVersion': self.nemesisSoftwareVersion,
                'deviceSoftwareVersion': self.deviceSoftwareVersion,
                }),
            })
        logging.debug(response.content)
        content = response.content.replace('while(1);', '')
        res = json.loads(content)
        if res and res.get('result') and res['result'].get('xsrfToken'):
            self.xsrf = res['result']['xsrfToken']
        return res

    def call(self, method, *args, **kwargs):
        if not self.xsrf:
            raise "no xsrf token, run api.handshake() first"
        response = self.session.post(self.basepath+'/rpc/'+'/'.join(method.split('_')),
                data = json.dumps({
                    'params': kwargs or args or [],
                    }),
                headers = {
                    'Content-Type': 'application/json;charset=UTF-8',
                    'X-XsrfToken': self.xsrf,
                    })
        logging.debug((method, args, kwargs))
        logging.debug(response.content)
        try:
            return response.json()
        except ValueError:
            logging.error(response)
            logging.error(response.text)
            raise

    def _call_proxy(self):
        _frame = sys._getframe(1)
        kwargs = dict(_frame.f_locals)
        kwargs.pop('self')
        return self.call(_frame.f_code.co_name, **kwargs)

    def hex_location(self, location):
        def hex_format(num):
            if isinstance(num, float) and num < 180:
                num *= 1e6
            num = int(num)
            if num < 0:
                num = abs(num) ^ 0xffffffff
            return '{0:0=8x}'.format(num)

        if isinstance(location, utils.LatLng):
            location = (location.lat, location.lng)
        if isinstance(location, (tuple, list)):
            return '%s,%s' % (hex_format(location[0]), hex_format(location[1]))
        return location

    def playerUndecorated_getGameScore(self):
        return self._call_proxy()

    def playerUndecorated_getPaginatedPlexts(self,
            cellsAsHex,
            ascendingTimestampOrder=False,
            desiredNumItems=100,
            energyGlobGuids=None,
            factionOnly=False,
            knobSyncTimestamp=None,
            maxTimestampMs=-1,
            minTimestampMs=0,
            clientBasket={'clientBlob': None},
            playerLocation=None):
        playerLocation = self.hex_location(playerLocation)
        return self._call_proxy()

    def playerUndecorated_getInventory(self,
            lastQueryTimestamp=0):
        return self._call_proxy()

    def playerUndecorated_getNickNamesFromPlayerIds(self, playerid):
        return self._call_proxy()

    def playerUndecorated_redeemReward(self, passcode):
        return self.call('playerUndecorated_redeemReward', passcode) 

    def gameplay_getObjectsInCells(self,
            cellsAsHex,
            dates,
            cells=None,
            energyGlobGuids=[],
            knobSyncTimestamp=0,
            clientBasket={'clientBlob': None},
            playerLocation=None): #"0261afb7,06f0df2e"
        playerLocation = self.hex_location(playerLocation)
        return self._call_proxy()

    def gameplay_collectItemsFromPortal(self,
            itemGuid,
            energyGlobGuids=[],
            knobSyncTimestamp=0,
            clientBasket={'clientBlob': None},
            playerLocation=None):
        playerLocation = self.hex_location(playerLocation)
        return self._call_proxy()

    def gameplay_getLinkabilityImpediment(self,
            originPortalGuid,
            portalLinkKeyGuidSet, #[id, id]
            energyGlobGuids=[],
            knobSyncTimestamp=0, #1358260316574
            clientBasket={'clientBlob': None},
            playerLocation=None):
        playerLocation = self.hex_location(playerLocation)
        return self._call_proxy()

    def gameplay_createLink(self,
            linkKeyGuid,
            originPortalGuid,
            destinationPortalGuid,
            clientBasket={'clientBlob': None},
            energyGlobGuids=[],
            knobSyncTimestamp=0,
            playerLocation=None):
        playerLocation = self.hex_location(playerLocation)
        return self._call_proxy()

    def gameplay_fireUntargetedRadialWeapon(self,
            itemGuid,
            playerLocation,
            energyGlobGuids=[],
            clientBasket={'clientBlob': None},
            knobSyncTimestamp=0):
        playerLocation = self.hex_location(playerLocation)
        return self._call_proxy()

    def gameplay_dropItem(self,
            itemGuid,
            playerLocation,
            energyGlobGuids=[],
            clientBasket={'clientBlob': None},
            knobSyncTimestamp=0):
        playerLocation = self.hex_location(playerLocation)
        return self._call_proxy()

    def gameplay_pickUp(self,
            itemGuid,
            playerLocation,
            energyGlobGuids=[],
            clientBasket={'clientBlob': None},
            knobSyncTimestamp=0):
        playerLocation = self.hex_location(playerLocation)
        return self._call_proxy()

    def gameplay_addMod(self,
            modResourceGuid,
            modableGuid,
            index=0,
            energyGlobGuids=[],
            knobSyncTimestamp=0,
            clientBasket={'clientBlob': None},
            playerLocation=None):
        playerLocation = self.hex_location(playerLocation)
        return self._call_proxy()

    def gameplay_deployResonatorV2(self,
            itemGuids,
            portalGuid,
            preferredSlot=255,
            location=None,
            energyGlobGuids=[],
            clientBasket={'clientBlob': None},
            knobSyncTimestamp=0):
        location = self.hex_location(location)
        return self._call_proxy()

    def gameplay_upgradeResonatorV2(self,
            emitterGuid,
            portalGuid,
            resonatorSlotToUpgrade=0,
            energyGlobGuids=[],
            knobSyncTimestamp=0,
            clientBasket={'clientBlob': None},
            location=None):
        location = self.hex_location(location)
        return self._call_proxy()

    def gameplay_rechargeResonatorsV2(self,
            portalGuid,
            portalKeyGuid=None,
            location=None,
            resonatorSlots=[0,1,2,3,4,5,6,7],
            energyGlobGuids=[],
            clientBasket={'clientBlob': None},
            knobSyncTimestamp=0):
        location = self.hex_location(location)
        return self._call_proxy()

    def player_say(self,
            message,
            factionOnly=False,
            playerLocation=None):
        playerLocation = self.hex_location(playerLocation)
        return self._call_proxy()

    def player_levelUp(self, level):
        return self.call('player_levelUp', level)

class Ze(object):
    """
    var Xe = 256;
    function Ye(a) {
      return a * (Math.PI / 180)
    }
    function Ze(a) {
      this.z = a;
      this.Ob = new google.maps.Point(this.z / 2, this.z / 2);
      this.Pb = this.z / 360;
      this.Qb = this.z / (2 * Math.PI);
      this.R = 1 << ZOOM_LEVEL - (this.z / Xe - 1)
    }
    function $e(a) {
      for(var b = [], c = ZOOM_LEVEL;c > 0;c--) {
        var d = 0, e = 1 << c - 1;
        (a.x & e) != 0 && d++;
        (a.y & e) != 0 && (d++, d++);
        b.push(d)
      }
      return b.join("")
    }
    Ze.prototype.fromLatLngToPoint = function(a, b) {
      var c = b || new google.maps.Point(0, 0), d = this.Ob;
      c.x = d.x + a.lng() * this.Pb;
      var e;
      e = Math.sin(Ye(a.lat()));
      -0.9999 != l && (e = Math.max(e, -0.9999));
      0.9999 != l && (e = Math.min(e, 0.9999));
      c.y = d.y + 0.5 * Math.log((1 + e) / (1 - e)) * -this.Qb;
      return c
    };
    Ze.prototype.fromPointToLatLng = function(a) {
      var b = this.Ob;
      return new google.maps.LatLng((2 * Math.atan(Math.exp((a.y - b.y) / -this.Qb)) - Math.PI / 2) / (Math.PI / 180), (a.x - b.x) / this.Pb)
    };
    function af(a, b) {
      return new google.maps.Point(b.x * a.z / a.R, b.y * a.z / a.R)
    }
    function bf(a, b) {
      var c = new google.maps.Point(b.x, b.y + 1), d = new google.maps.Point(b.x + 1, b.y), c = a.fromPointToLatLng(af(a, c)), d = a.fromPointToLatLng(af(a, d)), e = {};
      e.sw = c;
      e.ne = d;
      return e
    }
    function cf(a, b) {
      return new google.maps.Point(Math.floor(b.x / a.z), Math.floor(b.y / a.z))
    }
    ;"""
    pass

class IngressDashboradAPI(object):
    lat_split = 8427
    lng_split = 10986

    def __init__(self):
        self.session = requests.session()
        self.session.headers = {
                  'Accept': 'application/json, text/javascript, */*; q=0.01',
                  'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                  'Accept-Encoding': 'gzip,deflate,sdch',
                  'Accept-Language': 'en-US,en;q=0.8',
                  'Connection': 'keep-alive',
                  'Content-Type': 'application/json; charset=UTF-8',
                  'Host': 'www.ingress.com',
                  'Origin': 'http://www.ingress.com',
                  'Referer': 'http://www.ingress.com/intel',
                  'User-Agent': (
                      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) '
                      'Chrome/23.0.1271.97 Safari/537.11'),
                  'X-Requested-With': 'XMLHttpRequest',
                }
        self.xsrf = None

    def login(self, cookie=None):
        if not cookie:
            print 'visite "https://www.google.com/accounts/ServiceLogin?service=ah&passive=true&continue=https://appengine.google.com/_ah/conflogin%3Fcontinue%3Dhttp://www.ingress.com/intel&ltmpl=gm&shdf=ChMLEgZhaG5hbWUaB0luZ3Jlc3MMEgJhaCIU9ygNTr2_Yc5Lp2ZdvcgU78p3ggQoATIUSqjGiHQZFZbW83BI1iWbY93qYg4"'
            print 'get Cookie of domain http://www.ingress.com/intel'
            cookie = raw_input('Cookie:')
        self.xsrf = re.findall('csrftoken=(\w+)', cookie)[0]
        self.session.cookies['csrftoken'] = self.xsrf
        self.session.cookies['ACSID'] = re.findall('ACSID=([^;]+)', cookie)[0]

    def getThinnedEntitiesV2(self, minLat, minLng, maxLat, maxLng, split=False, minLevelOfDetail=-1):
        assert self.xsrf

        qk = minLat ^ minLng
        bounds = []
        if split:
            for lat in xrange(minLat, maxLat, self.lat_split):
                for lng in xrange(minLng, maxLng, self.lng_split):
                    _qk = utils.int2base(qk, 4); qk += 1
                    bounds.append({
                        'id': _qk,
                        'maxLatE6': min(maxLat, lat+self.lat_split),
                        'maxLngE6': min(maxLng, lng+self.lng_split),
                        'minLatE6': lat,
                        'minLngE6': lng,
                        'qk': _qk,
                        })
        else:
            _qk = utils.int2base(qk, 4)
            bounds.append({
                'id': _qk,
                'maxLatE6': maxLat,
                'maxLngE6': maxLng,
                'minLatE6': minLat,
                'minLngE6': minLng,
                'qk': _qk,
                })

        for group in [bounds[i:i+5] for i in range(0, len(bounds), 5)]:
            r = self.session.post('http://www.ingress.com/rpc/dashboard.getThinnedEntitiesV2',
                    data=json.dumps({
                        'method': "dashboard.getThinnedEntitiesV2",
                        'minLevelOfDetail': minLevelOfDetail,
                        'zoom': minLevelOfDetail,
                        'boundsParamsList': group,
                        }),
                    headers={
                        'X-CSRFToken': self.xsrf,
                        })
            yield r.json()




global_cell_info = {
        '6': (0, 40, 90, 135),
        }
grid_info = {
        '0': (-2, -2),
        '1': (-2, -1),
        '2': (-1, -1),
        '3': (-1, -2),
        '4': (1, -2),
        '5': (2, -2),
        '6': (2, -1),
        '7': (1, -1),
        '8': (1, 1),
        '9': (2, 1),
        'a': (2, 2),
        'b': (1, 2),
        'c': (-1, 2),
        'd': (-1, 1),
        'e': (-2, 1),
        'f': (-2, 2),
        }
grid_type = {
        '0': (0, 1),
        '6': (0, 1),
        '5': (0, 1),
        '9': (0, 1),
        'a': (0, 1),
        'f': (0, 1),

        '1': (1, 1),
        '2': (1, 1),
        '4': (1, 1),
        '8': (1, 1),

        '3': (0, -1),
        'c': (0, -1),

        '7': (1, -1),
        'b': (1, -1),
        'd': (1, -1),
        'e': (1, -1),
        }

def decode_cell(cellhex):
    if not cellhex:
        return None
    if cellhex[0] not in global_cell_info:
        return None
    cellhex = cellhex.lower()
    pre_cell = cellhex[0]
    area = list(global_cell_info[pre_cell])
    for each in cellhex[1:]:
        if each == '0':
            break
        grid = list(grid_info[each])
        cell_type = grid_type[pre_cell]
        if cell_type[0] == 1:
            grid = grid[::-1]
        if cell_type[1] == -1:
            grid = map(lambda x: -x, grid)

        lat_split = (area[1]-area[0])/4.0
        lng_split = (area[3]-area[2])/4.0
        if grid[0] < 0:
            grid[0] += 2
        else:
            grid[0] += 1
        if grid[1] < 0:
            grid[1] += 2
        else:
            grid[1] += 1
        area = [area[0]+grid[1]*lat_split,
                area[0]+(grid[1]+1)*lat_split,
                area[2]+grid[0]*lat_split,
                area[2]+(grid[0]+1)*lng_split]
        pre_cell = each
        print each, grid[::-1], area
    return area

if __name__ == '__main__':
    print decode_cell('6be3593fa0000000')
