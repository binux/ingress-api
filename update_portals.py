#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2013-01-24 21:38:09

import api
import database

_cookie = None
try:
    _cookie = open('cookie.web').read()
except:
    pass

areas = {
        'beijing.kmz': [39798197,116014895,40125552,116709780],
        'tianjin.kmz': [38868573,116904655,39459514,117871452],
        'hongkong.kmz': [22111713,113755012,22755276,114502083],
        'macao.kmz': [21990794,113332039,22322754,113738533],
        'guangzhou.kmz': [22794529,112736030,23402124,113705574],
        'taiwan.kmz': [21582731,119000984,25595080,123010994],
        'shanghai.kmz': [30004290,119934822,31665645,122170540],
        'wuhan.kmz': [30336721,114095588,30749497,114606453],
        'guilin.kmz': [25050136,110038887,25426521,110514046],
        'congqing.kmz': [29175535,106012398,30136209,107209907],
        'cengdu.kmz': [30500149,103837105,30820284,104298530],
        'nanjing.kmz': [31910505,118615527,32188697,118939624],
        }
#capturedRegion
def fetch(coords=areas['beijing.kmz'], cookie=_cookie, type='portalV2'):
    ingress = api.IngressDashboradAPI()
    ingress.login(cookie)

    for result in ingress.getThinnedEntitiesV2(*coords, split=False, minLevelOfDetail=0):
        result = result and result.get('result')
        result = result and result.get('map')
        for qk, entities in result.iteritems():
            for guid, uptime, info in entities.get('gameEntities', []):
                if type not in info:
                    continue
                yield guid, uptime, info

def get_level(info):
    return sum([x and x['level'] or 0 for x in info['resonatorArray']['resonators']]) / 8.0

def get_enery(info):
    return sum([x and x['energyTotal'] or 0 for x in info['resonatorArray']['resonators']])

def update_database():
    session = database.Session()
    for guid, uptime, info in fetch():
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
    for guid, uptime, info in fetch():
        pnt = kml.newpoint(name=info['portalV2']['descriptiveText']['TITLE'],
                description='Level: %s\nhttp://www.ingress.com/intel?latE6=%d&lngE6=%d&z=17' % (
                    get_level(info), info['locationE6']['latE6'], info['locationE6']['lngE6']),
                coords = [(info['locationE6']['lngE6']*1e-6, info['locationE6']['latE6']*1e-6),])
        pnt.style.iconstyle.icon.href = icon_map[info['controllingTeam']['team']]
    kml.save('beijing.kml')

def count_mus():
    mus = {
            'ALIENS': 0,
            'RESISTANCE': 0,
            'NEUTRAL': 0}
    for guid, uptime, info in fetch(type='capturedRegion'):
        mus[info['controllingTeam']['team']] += int(info['entityScore']['entityScore'])
    return mus

if __name__ == '__main__':
    update_database()
