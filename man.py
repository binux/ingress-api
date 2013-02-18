#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2013-02-01 11:55:30

import ingress as _ingress
from utils import LatLng
import logging;logging.getLogger().setLevel(logging.INFO)

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

def contol(guid):
    portal = ingress.session.query(database.Portal).get(guid)
    if not portal:
        return None
    ingress.target = portal
    ingress.goto(ingress.target)
    ingress.scan()
    speed_limit = ingress.speed_limit
    ingress.speed_limit = 100
    ingress.destroy()
    ingress.goto(ingress.target.latlng.goto(0, 39.5))
    ingress.deploy_full(max_level=True)
    ingress.speed_limit = speed_limit
    return ingress.target.controlling == ingress.player_team

ingress = _ingress.Ingress()
ingress.login()
for i in range(10):
    try:
        ingress.update_inventory()
        break
    except ValueError:
        continue
import IPython; IPython.embed()
