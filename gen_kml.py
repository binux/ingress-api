#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2013-01-24 21:38:09

import api
import time
import simplekml

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
        'zhengzhou.kmz': [34640644,113487396,34888839,113831405],
        'taiyuan.kmz': [37635664,112425842,37944960,112793884],
        }
styles = {
        'ALIENS_0_0': 'http://s.binux.me/ingress/icons/smallSQGreenIcons/blank.PNG',
        'ALIENS_1_0': 'http://s.binux.me/ingress/icons/smallSQGreenIcons/marker1.png',
        'ALIENS_2_0': 'http://s.binux.me/ingress/icons/smallSQGreenIcons/marker2.png',
        'ALIENS_3_0': 'http://s.binux.me/ingress/icons/smallSQGreenIcons/marker3.png',
        'ALIENS_4_0': 'http://s.binux.me/ingress/icons/smallSQGreenIcons/marker4.png',
        'ALIENS_5_0': 'http://s.binux.me/ingress/icons/smallSQGreenIcons/marker5.png',
        'ALIENS_6_0': 'http://s.binux.me/ingress/icons/smallSQGreenIcons/marker6.png',
        'ALIENS_7_0': 'http://s.binux.me/ingress/icons/smallSQGreenIcons/marker7.png',
        'ALIENS_8_0': 'http://s.binux.me/ingress/icons/smallSQGreenIcons/marker8.png',

        'ALIENS_0_1': 'http://s.binux.me/ingress/icons/largeTDGreenIcons/blank.png',
        'ALIENS_1_1': 'http://s.binux.me/ingress/icons/largeTDGreenIcons/marker1.png',
        'ALIENS_2_1': 'http://s.binux.me/ingress/icons/largeTDGreenIcons/marker2.png',
        'ALIENS_3_1': 'http://s.binux.me/ingress/icons/largeTDGreenIcons/marker3.png',
        'ALIENS_4_1': 'http://s.binux.me/ingress/icons/largeTDGreenIcons/marker4.png',
        'ALIENS_5_1': 'http://s.binux.me/ingress/icons/largeTDGreenIcons/marker5.png',
        'ALIENS_6_1': 'http://s.binux.me/ingress/icons/largeTDGreenIcons/marker6.png',
        'ALIENS_7_1': 'http://s.binux.me/ingress/icons/largeTDGreenIcons/marker7.png',
        'ALIENS_8_1': 'http://s.binux.me/ingress/icons/largeTDGreenIcons/marker8.png',

        'ALIENS_0_2': 'http://s.binux.me/ingress/icons/smallSQGreenRedIcons/blank.PNG',
        'ALIENS_1_2': 'http://s.binux.me/ingress/icons/smallSQGreenRedIcons/marker1.png',
        'ALIENS_2_2': 'http://s.binux.me/ingress/icons/smallSQGreenRedIcons/marker2.png',
        'ALIENS_3_2': 'http://s.binux.me/ingress/icons/smallSQGreenRedIcons/marker3.png',
        'ALIENS_4_2': 'http://s.binux.me/ingress/icons/smallSQGreenRedIcons/marker4.png',
        'ALIENS_5_2': 'http://s.binux.me/ingress/icons/smallSQGreenRedIcons/marker5.png',
        'ALIENS_6_2': 'http://s.binux.me/ingress/icons/smallSQGreenRedIcons/marker6.png',
        'ALIENS_7_2': 'http://s.binux.me/ingress/icons/smallSQGreenRedIcons/marker7.png',
        'ALIENS_8_2': 'http://s.binux.me/ingress/icons/smallSQGreenRedIcons/marker8.png',

        'RESISTANCE_0_0': 'http://s.binux.me/ingress/icons/smallSQBlueIcons/blank.PNG',
        'RESISTANCE_1_0': 'http://s.binux.me/ingress/icons/smallSQBlueIcons/marker1.png',
        'RESISTANCE_2_0': 'http://s.binux.me/ingress/icons/smallSQBlueIcons/marker2.png',
        'RESISTANCE_3_0': 'http://s.binux.me/ingress/icons/smallSQBlueIcons/marker3.png',
        'RESISTANCE_4_0': 'http://s.binux.me/ingress/icons/smallSQBlueIcons/marker4.png',
        'RESISTANCE_5_0': 'http://s.binux.me/ingress/icons/smallSQBlueIcons/marker5.png',
        'RESISTANCE_6_0': 'http://s.binux.me/ingress/icons/smallSQBlueIcons/marker6.png',
        'RESISTANCE_7_0': 'http://s.binux.me/ingress/icons/smallSQBlueIcons/marker7.png',
        'RESISTANCE_8_0': 'http://s.binux.me/ingress/icons/smallSQBlueIcons/marker8.png',

        'RESISTANCE_0_1': 'http://s.binux.me/ingress/icons/largeTDBlueIcons/blank.png',
        'RESISTANCE_1_1': 'http://s.binux.me/ingress/icons/largeTDBlueIcons/marker1.png',
        'RESISTANCE_2_1': 'http://s.binux.me/ingress/icons/largeTDBlueIcons/marker2.png',
        'RESISTANCE_3_1': 'http://s.binux.me/ingress/icons/largeTDBlueIcons/marker3.png',
        'RESISTANCE_4_1': 'http://s.binux.me/ingress/icons/largeTDBlueIcons/marker4.png',
        'RESISTANCE_5_1': 'http://s.binux.me/ingress/icons/largeTDBlueIcons/marker5.png',
        'RESISTANCE_6_1': 'http://s.binux.me/ingress/icons/largeTDBlueIcons/marker6.png',
        'RESISTANCE_7_1': 'http://s.binux.me/ingress/icons/largeTDBlueIcons/marker7.png',
        'RESISTANCE_8_1': 'http://s.binux.me/ingress/icons/largeTDBlueIcons/marker8.png',

        'RESISTANCE_0_2': 'http://s.binux.me/ingress/icons/smallSQBlueRedIcons/blank.PNG',
        'RESISTANCE_1_2': 'http://s.binux.me/ingress/icons/smallSQBlueRedIcons/marker1.png',
        'RESISTANCE_2_2': 'http://s.binux.me/ingress/icons/smallSQBlueRedIcons/marker2.png',
        'RESISTANCE_3_2': 'http://s.binux.me/ingress/icons/smallSQBlueRedIcons/marker3.png',
        'RESISTANCE_4_2': 'http://s.binux.me/ingress/icons/smallSQBlueRedIcons/marker4.png',
        'RESISTANCE_5_2': 'http://s.binux.me/ingress/icons/smallSQBlueRedIcons/marker5.png',
        'RESISTANCE_6_2': 'http://s.binux.me/ingress/icons/smallSQBlueRedIcons/marker6.png',
        'RESISTANCE_7_2': 'http://s.binux.me/ingress/icons/smallSQBlueRedIcons/marker7.png',
        'RESISTANCE_8_2': 'http://s.binux.me/ingress/icons/smallSQBlueRedIcons/marker8.png',

        'NEUTRAL_0_0': 'http://s.binux.me/ingress/icons/smallSQRedIcons/blank.PNG',
        'NEUTRAL_0_1': 'http://s.binux.me/ingress/icons/smallSQRedIcons/blank.PNG',
        'NEUTRAL_0_2': 'http://s.binux.me/ingress/icons/smallSQRedIcons/blank.PNG',
        }
for key, value in list(styles.items()):
    tmp = simplekml.Style()
    tmp.iconstyle.icon.href = value
    styles[key] = tmp
try:
    _cookie = open('cookie.web').read()
except:
    _cookie = None


def get_level(info):
    return sum([x and x['level'] or 0 for x in info['resonatorArray']['resonators']]) / 8.0

def get_enery(info):
    return sum([x and x['energyTotal'] or 0 for x in info['resonatorArray']['resonators']])

energyMax = [ 0, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 6000 ];
def about_to_nature(info):
    for x in info['resonatorArray']['resonators']:
        if x and x['energyTotal'] > energyMax[int(x['level'])]*0.1:
            return False
    return True

def not_full(info):
    for x in info['resonatorArray']['resonators']:
        if not x:
            return True
    return False

def fetch_portals(coords, cookie=_cookie):
    ingress = api.IngressDashboradAPI()
    ingress.login(cookie)

    for result in ingress.getThinnedEntitiesV2(*coords, split=False, minLevelOfDetail=0):
        result = result and result.get('result')
        result = result and result.get('map')
        for qk, entities in result.iteritems():
            for guid, uptime, info in entities.get('gameEntities', []):
                if 'portalV2' not in info:
                    continue
                yield guid, uptime, info

def build_kml(city, coords):
    kml = simplekml.Kml()
    for guid, uptime, info in fetch_portals(coords):
        level = get_level(info)
        pnt = kml.newpoint(name=info['portalV2']['descriptiveText']['TITLE'],
                description='Level: %s\nhttp://www.ingress.com/intel?latE6=%d&lngE6=%d&z=17' % (
                    level, info['locationE6']['latE6'], info['locationE6']['lngE6']),
                coords = [(info['locationE6']['lngE6']*1e-6, info['locationE6']['latE6']*1e-6),])
        if about_to_nature(info):
            portal_type = 2
        elif not_full(info):
            portal_type = 1
        else:
            portal_type = 0
        style = styles.get('%s_%d_%d' % (
            info['controllingTeam']['team'],
            level,
            portal_type), None)
        if style:
            pnt.style = style
    kml.savekmz('/srv/ingress/'+city)

if __name__ == '__main__':
    for city, coords in areas.iteritems():
        print city, coords
        build_kml(city, coords)
