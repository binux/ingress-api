#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2013-01-19 12:01:07

import os
import json
import urllib2
import database
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
    return (hex_decode(a[0]), hex_decode(a[1]))

class StickyMaster(controller.Master):
    def __init__(self, server):
        controller.Master.__init__(self, server)
        self.session = database.Session()

    def run(self):
        try:
            return controller.Master.run(self)
        except KeyboardInterrupt:
            self.shutdown()

    def handle_request(self, msg):
        print msg.get_url()
        msg._ack()

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

            cells = request['params']['cellsAsHex']
            coor = decode_coor(request['params']['playerLocation'])
            for each in cells:
                cell = database.GEOCell()
                cell.latE6 = coor[0]
                cell.lngE6 = coor[1]
                cell.cell = each
                self.session.merge(cell)
                self.session.commit()

    def handle_response(self, msg):
        msg._ack()

config = proxy.ProxyConfig(
    cacert = os.path.expanduser("~/.mitmproxy/mitmproxy-ca.pem")
)
server = proxy.ProxyServer(config, 8080)
m = StickyMaster(server)
m.run()
