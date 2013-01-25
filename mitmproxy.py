#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2013-01-19 12:01:07

import os
import json
import urllib2
import simplekml
from libmproxy import controller, proxy

def get_common(string_list):
    if not string_list:
        return ''
    common_prefix = string_list[0]
    for each in string_list[1:]:
        for i in range(min(len(common_prefix), len(each))):
            if common_prefix[i] != each[i]:
                common_prefix = common_prefix[:i]
                break
    return common_prefix


def hex_decode(num):
    num = int(num, 16)
    if num & 0x80000000:
        return -((num ^ 0xffffffff) + 1)
    return num
def decode_coor(string):
    a = string.split(',')
    if len(a) != 2:
        return ()
    return (hex_decode(a[0])*1e-6, hex_decode(a[1])*1e-6)

coords = []
lat = (40.0, 41.0)
lng = (116.0, 117.0)
for i in range(50):
    for j in range(50):
        coords.append((lat[0]+(lat[1]-lat[0])/20.0*i,
                      lng[0]+(lng[1]-lng[0])/20.0*j))

class StickyMaster(controller.Master):
    def __init__(self, server):
        controller.Master.__init__(self, server)
        self.stickyhosts = {}
        self.saved_point = set()
        self.kml = simplekml.Kml()

    def run(self):
        try:
            return controller.Master.run(self)
        except KeyboardInterrupt:
            self.shutdown()
            self.kml.save('area_3_detail.kml')

    def handle_request(self, msg):
        if msg.get_url() == 'http://mobilemaps.clients.google.com/glm/mmap':
            msg._ack(None)
        if msg.get_url().startswith('https://betaspike.appspot.com/rpc'):
            msg._ack(None)

        if msg.get_url() == 'https://betaspike.appspot.com/rpc/gameplay/getObjectsInCells':
            msg.decode()
            request = json.loads(msg.content)
            if not isinstance(request.get('params'), dict):
                print 'params error'
                return
            if not request['params'].get('cellsAsHex'):
                print 'no cellsAsHex'
                return
            if not request['params'].get('playerLocation'):
                print 'no playerLocation'
                return

            if coords:
                coord = coords.pop()
                print 'goto %s, %d togo' % (coord, len(coords))
                urllib2.urlopen("http://127.0.0.1:9292/adb/geo_location?latitude=%f&longitude=%f" % coord)

            cell = get_common(request['params']['cellsAsHex'])
            coor = decode_coor(request['params']['playerLocation'])
            if coor in self.saved_point:
                print 'saved point'
                return
            if cell and coor:
                self.saved_point.add(coor)
                print cell, coor
                self.kml.newpoint(name=cell,
                                  description=str(coor),
                                  coords = [coor[::-1],])
        msg._ack()
                cell.latE6 = coor[0]
                cell.lngE6 = coor[1]
        print msg.request.get_url()
                cell.cell = each
                self.session.merge(cell)

    def handle_response(self, msg):
        msg._ack()

config = proxy.ProxyConfig(
    cacert = os.path.expanduser("~/.mitmproxy/mitmproxy-ca.pem")
)
server = proxy.ProxyServer(config, 8080)
m = StickyMaster(server)
m.run()
