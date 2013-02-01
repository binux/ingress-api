#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2013-02-01 11:55:30

import ingress
from utils import LatLng

def goto(lat, lng):
    ingress.goto(LatLng(lat, lng))

def keys(guid):
    cnt = 0
    for each in ingress.bag.group[ingress.bag.PORTAL_KEY]:
        if ingress.bag.inventory[each].portal_guid == guid:
            cnt += 1
    return cnt

def link(orig, dest):
    global ret
    ret = ingress.link(orig, dest)

if __name__ == '__main__':
    _ingress = ingress
    ingress = ingress.Ingress()
    ingress.login()
