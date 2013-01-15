#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2013-01-15 21:00:15

import time
import json
import requests

class IngressAPI(object):
    basepath = 'https://betaspike.appspot.com'
    nemesisSoftwareVersion = '2012-12-20T21:55:07Z 887b00b46b68 opt'
    deviceSoftwareVersion = '4.1.1'

    def __init__(self):
        self.session = requests.session()
        self.session.config['base_headers'] = {
                'Accept-Encoding': 'gzip',
                'User-Agent': 'Nemesis (gzip)',
                }
        self.xsrf = None

    def login(self):
        print 'visite "https://www.google.com/accounts/ServiceLogin?service=ah&passive=true&continue=https://appengine.google.com/_ah/conflogin%3Fcontinue%3Dhttps%3A%2F%2Fbetaspike.appspot.com"'
        print 'get cookie SACSID of domain betaspike.appspot.com'
        cookie = raw_input('SACSID:')
        self.session.cookies['SACSID'] = cookie
        self.handshake()

    def handshake(self):
        response = self.session.get(self.basepath+'/handshake', params={
            'json': json.dumps({
                'nemesisSoftwareVersion': self.nemesisSoftwareVersion,
                'deviceSoftwareVersion': self.deviceSoftwareVersion,
                }),
            })
        content = response.content.replace('while(1);', '')
        res = json.loads(content)
        if res and res.get('result') and res['result'].get('xsrfToken'):
            self.xsrf = res['result']['xsrfToken']
        return res

    def call(self, method, *args, **kwargs):
        if not self.xsrf:
            raise "no xsrf token, run api.handshake() first"
        response = self.session.post(self.basepath+'/rpc/'+'/'.join(method.split('.')),
                data = json.dumps({
                    'params': kwargs or args or [],
                    }),
                headers = {
                    'Content-Type': 'application/json;charset=UTF-8',
                    'X-XsrfToken': self.xsrf,
                    })
        print response.content
        return response.json

    def playerUndecorated_getGameScore(self):
        return self.call('playerUndecorated.getGameScore')

    def playerUndecorated_getPaginatedPlexts(self,
            cellsAsHex, #[ "358b400000000000", "358d000000000000", "35f0000000000000", "5e1df00000000000", "5e1e100000000000" ]
            ascendingTimestampOrder=False,
            desiredNumItems=100,
            energyGlobGuids=None,
            factionOnly=False,
            knobSyncTimestamp=None,
            maxTimestampMs=-1,
            minTimestampMs=1358170590903,
            playerLocation=None):
        return self.call('playerUndecorated.getPaginatedPlexts')

    def gameplay_getObjectsInCells(self,
            cellsAsHex,
            dates,
            cells=None,
            energyGlobGuids=[],
            knobSyncTimestamp=0,
            playerLocation=None): #"0261afb7,06f0df2e"
        pass

    def playerUndecorated_getInventory(self, lastQueryTimestamp=0):
        return self.call("playerUndecorated.getInventory", lastQueryTimestamp=lastQueryTimestamp)

    def gameplay_pickUp(self):
        return self.call("gameplay.pickUp",
                itemGuid,
                playerLocation,
                energyGlobGuids=[],
                knobSyncTimestamp=0)

    def playerUndecorated_getNickNamesFromPlayerIds(self, playerid):
        return self.call("playerUndecorated.getNickNamesFromPlayerIds", playerid)

    def gameplay_collectItemsFromPortal(self):
        return self.call("gameplay.collectItemsFromPortal",
                itemGuid,
                energyGlobGuids=[],
                knobSyncTimestamp=0,
                playerLocation=None)

    def gameplay_getLinkabilityImpediment(self):
        return self.call("gameplay.getLinkabilityImpediment",
                originPortalGuid,
                portalLinkKeyGuidSet, #[id, id]
                energyGlobGuids=[],
                knobSyncTimestamp=0, #1358260316574
                playerLocation=None)

    def gameplay_fireUntargetedRadialWeapon(self):
        return self.call("gameplay.fireUntargetedRadialWeapon",
                itemGuid,
                energyGlobGuids=[],
                knobSyncTimestamp=0,
                playerLocation=None)

    def gameplay_dropItem(self):
        return self.call("gameplay.dropItem",
                itemGuid,
                energyGlobGuids=[],
                knobSyncTimestamp=0,
                playerLocation=None)

    def gameplay_addMod(self):
        return self.call("gameplay.addMod",
                modResourceGuid,
                modableGuid,
                index=0,
                energyGlobGuids=[],
                knobSyncTimestamp=0,
                playerLocation=None)

    def gameplay_upgradeResonatorV2(self):
        return self.call("gameplay.upgradeResonatorV2",
                emitterGuid,
                portalGuid,
                resonatorSlotToUpgrade=0,
                energyGlobGuids=[],
                knobSyncTimestamp=0,
                location=None)

    def player_say(self):
        return self.call("player.say",
                message,
                factionOnly=False,
                playerLocation=None)


