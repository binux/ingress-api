#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2013-01-24 21:38:09

import api
import time
import ingress as _ingress
import simplekml

from map_offset import gps2gmap
from urllib import quote

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
        'haerbin.kmz': [45591128,126376676,45923124,126891660],
        }
styles = {
        'ALIENS_0_0': 'http://s.binux.me/ingress/icon/enlightened/1.png',
        'ALIENS_1_0': 'http://s.binux.me/ingress/icon/enlightened/1.png',
        'ALIENS_2_0': 'http://s.binux.me/ingress/icon/enlightened/2.png',
        'ALIENS_3_0': 'http://s.binux.me/ingress/icon/enlightened/3.png',
        'ALIENS_4_0': 'http://s.binux.me/ingress/icon/enlightened/4.png',
        'ALIENS_5_0': 'http://s.binux.me/ingress/icon/enlightened/5.png',
        'ALIENS_6_0': 'http://s.binux.me/ingress/icon/enlightened/6.png',
        'ALIENS_7_0': 'http://s.binux.me/ingress/icon/enlightened/7.png',
        'ALIENS_8_0': 'http://s.binux.me/ingress/icon/enlightened/8.png',

        'ALIENS_0_1': 'http://s.binux.me/ingress/icon/enlightened/1.png',
        'ALIENS_1_1': 'http://s.binux.me/ingress/icon/enlightened/1.png',
        'ALIENS_2_1': 'http://s.binux.me/ingress/icon/enlightened/2.png',
        'ALIENS_3_1': 'http://s.binux.me/ingress/icon/enlightened/3.png',
        'ALIENS_4_1': 'http://s.binux.me/ingress/icon/enlightened/4.png',
        'ALIENS_5_1': 'http://s.binux.me/ingress/icon/enlightened/5.png',
        'ALIENS_6_1': 'http://s.binux.me/ingress/icon/enlightened/6.png',
        'ALIENS_7_1': 'http://s.binux.me/ingress/icon/enlightened/7.png',
        'ALIENS_8_1': 'http://s.binux.me/ingress/icon/enlightened/8.png',

        'ALIENS_0_2': 'http://s.binux.me/ingress/icon/enlightened_2/1.png',
        'ALIENS_1_2': 'http://s.binux.me/ingress/icon/enlightened_2/1.png',
        'ALIENS_2_2': 'http://s.binux.me/ingress/icon/enlightened_2/2.png',
        'ALIENS_3_2': 'http://s.binux.me/ingress/icon/enlightened_2/3.png',
        'ALIENS_4_2': 'http://s.binux.me/ingress/icon/enlightened_2/4.png',
        'ALIENS_5_2': 'http://s.binux.me/ingress/icon/enlightened_2/5.png',
        'ALIENS_6_2': 'http://s.binux.me/ingress/icon/enlightened_2/6.png',
        'ALIENS_7_2': 'http://s.binux.me/ingress/icon/enlightened_2/7.png',
        'ALIENS_8_2': 'http://s.binux.me/ingress/icon/enlightened_2/8.png',

        'RESISTANCE_0_0': 'http://s.binux.me/ingress/icon/resistance/1.PNG',
        'RESISTANCE_1_0': 'http://s.binux.me/ingress/icon/resistance/1.png',
        'RESISTANCE_2_0': 'http://s.binux.me/ingress/icon/resistance/2.png',
        'RESISTANCE_3_0': 'http://s.binux.me/ingress/icon/resistance/3.png',
        'RESISTANCE_4_0': 'http://s.binux.me/ingress/icon/resistance/4.png',
        'RESISTANCE_5_0': 'http://s.binux.me/ingress/icon/resistance/5.png',
        'RESISTANCE_6_0': 'http://s.binux.me/ingress/icon/resistance/6.png',
        'RESISTANCE_7_0': 'http://s.binux.me/ingress/icon/resistance/7.png',
        'RESISTANCE_8_0': 'http://s.binux.me/ingress/icon/resistance/8.png',

        'RESISTANCE_0_1': 'http://s.binux.me/ingress/icon/resistance/1.png',
        'RESISTANCE_1_1': 'http://s.binux.me/ingress/icon/resistance/1.png',
        'RESISTANCE_2_1': 'http://s.binux.me/ingress/icon/resistance/2.png',
        'RESISTANCE_3_1': 'http://s.binux.me/ingress/icon/resistance/3.png',
        'RESISTANCE_4_1': 'http://s.binux.me/ingress/icon/resistance/4.png',
        'RESISTANCE_5_1': 'http://s.binux.me/ingress/icon/resistance/5.png',
        'RESISTANCE_6_1': 'http://s.binux.me/ingress/icon/resistance/6.png',
        'RESISTANCE_7_1': 'http://s.binux.me/ingress/icon/resistance/7.png',
        'RESISTANCE_8_1': 'http://s.binux.me/ingress/icon/resistance/8.png',

        'RESISTANCE_0_2': 'http://s.binux.me/ingress/icon/resistance_2/1.png',
        'RESISTANCE_1_2': 'http://s.binux.me/ingress/icon/resistance_2/1.png',
        'RESISTANCE_2_2': 'http://s.binux.me/ingress/icon/resistance_2/2.png',
        'RESISTANCE_3_2': 'http://s.binux.me/ingress/icon/resistance_2/3.png',
        'RESISTANCE_4_2': 'http://s.binux.me/ingress/icon/resistance_2/4.png',
        'RESISTANCE_5_2': 'http://s.binux.me/ingress/icon/resistance_2/5.png',
        'RESISTANCE_6_2': 'http://s.binux.me/ingress/icon/resistance_2/6.png',
        'RESISTANCE_7_2': 'http://s.binux.me/ingress/icon/resistance_2/7.png',
        'RESISTANCE_8_2': 'http://s.binux.me/ingress/icon/resistance_2/8.png',

        'NEUTRAL_0_0': 'http://s.binux.me/ingress/icon/blank.png',
        'NEUTRAL_0_1': 'http://s.binux.me/ingress/icon/blank.png',
        'NEUTRAL_0_2': 'http://s.binux.me/ingress/icon/blank.png',
        }
for key, value in list(styles.items()):
    tmp = simplekml.Style()
    tmp.iconstyle.icon.href = value
    styles[key] = tmp
try:
    _cookie = open('cookie.web').read()
except:
    _cookie = None


def fetch_portals(coords, cookie=_cookie):
    ingress = api.IngressDashboradAPI()
    ingress.login(cookie)

    for result in ingress.getThinnedEntitiesV2(*coords, split=False, minLevelOfDetail=0):
        result = result and result.get('result')
        result = result and result.get('map')
        for qk, entities in result.iteritems():
            for guid, uptime, info in entities.get('gameEntities', []):
                if _ingress.Portal.is_portal(info):
                    yield _ingress.Portal(guid, info)

def build_kml(city):
    kml = simplekml.Kml()
    kml_fixed = simplekml.Kml()

    for portal in fetch_portals(areas[city]):
        if portal.about_to_nature:
            portal_type = 2
        elif not portal.full:
            portal_type = 1
        else:
            portal_type = 0

        name = portal.title
        latlng = portal.latlng
        fixed_latlng = gps2gmap(latlng.lat, latlng.lng)
        desc = '<br />'.join([
                    'Level: %s' % (portal.level)
                    +(' <a href="http://www.ingress.com/intel?latE6=%d&lngE6=%d&z=17" target="_blank">Ingress</a>' % (latlng.lat*1e6, latlng.lng*1e6)),
                    'Resonators: %d/8 | Mods: %d/4 | Energy: %d (%0.f%%)' % (len([x for x in portal.resonators if x]), len([x for x in portal.mods if x]), portal.energy, portal.energy / (portal.total_energy + 0.00000001) * 100.0),
                    '',
                    '<img src="%s" style="max-width: 300px; max-height: 230px;" />' % portal.image,])
                    #+('Map: <a href="https://maps.google.com/maps?q=%s%%40%s,%s" target="_blank">Google</a>' % (quote(name.encode('utf8')), fiexed_latlng[0], fixed_latlng[1])),

        pnt = kml.newpoint(name=portal.title, description=desc, coords = [(latlng.lng, latlng.lat),])
        pnt_fixed = kml_fixed.newpoint(name=portal.title, description=desc, coords = [fixed_latlng[::-1],])

        style = styles.get('%s_%d_%d' % (
            portal.controlling,
            portal.level,
            portal_type), None)
        if style:
            pnt.style = style
            pnt_fixed.style = style

    kml.savekmz('/srv/ingress/'+city)
    kml_fixed.savekmz('/srv/ingress/fixed_'+city)

if __name__ == '__main__':
    for city, coords in areas.iteritems():
        print city, coords
        build_kml(city)
