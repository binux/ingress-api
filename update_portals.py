#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2013-01-24 21:38:09

import api
import database

def fetch_portals(cookie=None):
    ingress = api.IngressDashboradAPI()
    ingress.login(cookie)

    for result in ingress.getThinnedEntitiesV2(39798197,116014895,40125552,116709780, False, 0):
        result = result and result.get('result')
        result = result and result.get('map')
        for qk, entities in result.iteritems():
            for guid, uptime, info in entities.get('gameEntities', []):
                if 'portalV2' not in info:
                    continue
                yield guid, uptime, info

def get_level(info):
    return sum([x and x['level'] or 0 for x in info['resonatorArray']['resonators']]) / 8.0

def get_enery(info):
    return sum([x and x['energyTotal'] or 0 for x in info['resonatorArray']['resonators']])

def update_database():
    session = database.Session()
    for guid, uptime, info in fetch_portals():
        portal = database.Portal()
        portal.guid = guid
        portal.uptime = uptime
        portal.control = info['controllingTeam']['team']
        portal.latE6 = info['locationE6']['latE6']
        portal.lngE6 = info['locationE6']['lngE6']
        portal.level = get_level(info)
        portal.energy = get_enery(info)
        session.merge(portal)
        session.commit()

icon_map = {
        'ALIENS': 'http://maps.gstatic.com/mapfiles/ms2/micons/green.png',
        'RESISTANCE': 'http://maps.gstatic.com/mapfiles/ms2/micons/blue.png',
        'NEUTRAL': 'https://maps.gstatic.com/mapfiles/ms2/micons/yellow.png',
        }
def build_kml():
    import simplekml
    kml = simplekml.Kml()
    for guid, uptime, info in fetch_portals():
        pnt = kml.newpoint(name=info['portalV2']['descriptiveText']['TITLE'],
                description='Level: %s\nhttp://www.ingress.com/intel?latE6=%d&lngE6=%d&z=17' % (
                    get_level(info), info['locationE6']['latE6'], info['locationE6']['lngE6']),
                coords = [(info['locationE6']['lngE6']*1e-6, info['locationE6']['latE6']*1e-6),])
        pnt.style.iconstyle.icon.href = icon_map[info['controllingTeam']['team']]
    kml.save('beijing.kml')

if __name__ == '__main__':
    update_database()
