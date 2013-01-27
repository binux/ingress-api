#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2013-01-25 23:13:54

import time
#import numpy
import cmath
import random
import logging
#import Pycluster

import utils
import database
TOTAL_GROUP = 7
LAT_FIX = (utils.LatLng(40, 116) - utils.LatLng(39, 116)) / 1000
LNG_FIX = (utils.LatLng(40, 116) - utils.LatLng(40, 117)) / 1000

def draw_group(portals, tofile='group.kml'):
    import simplekml
    styles = [
            'http://s.binux.me/ingress/icons/smallSQGreenIcons/blank.PNG',
            'http://s.binux.me/ingress/icons/smallSQGreenIcons/marker1.png',
            'http://s.binux.me/ingress/icons/smallSQGreenIcons/marker2.png',
            'http://s.binux.me/ingress/icons/smallSQGreenIcons/marker3.png',
            'http://s.binux.me/ingress/icons/smallSQGreenIcons/marker4.png',
            'http://s.binux.me/ingress/icons/smallSQGreenIcons/marker5.png',
            'http://s.binux.me/ingress/icons/smallSQGreenIcons/marker6.png',
            'http://s.binux.me/ingress/icons/smallSQGreenIcons/marker7.png',
            'http://s.binux.me/ingress/icons/smallSQGreenIcons/marker8.png',
            'http://s.binux.me/ingress/icons/smallSQGreenIcons/marker9.png',
            'http://s.binux.me/ingress/icons/smallSQGreenIcons/marker10.png',
            'http://s.binux.me/ingress/icons/smallSQGreenIcons/marker11.png',
            ]
    for key, value in enumerate(list(styles)):
        tmp = simplekml.Style()
        tmp.iconstyle.icon.href = value
        styles[key] = tmp

    kml = simplekml.Kml()
    for portal in portals:
        pnt = kml.newpoint(name=portal.guid,
                coords = [(portal.lngE6*1e-6, portal.latE6*1e-6),])
        pnt.style = styles[portal.group]
    kml.save(tofile)

def draw_path(portals, tofile='path.kml'):
    import simplekml
    kml = simplekml.Kml()
    pre = None
    for portal in portals:
        pnt = kml.newpoint(name=portal.guid,
                coords = [(portal.lngE6*1e-6, portal.latE6*1e-6),])
        if pre is not None:
            lin = kml.newlinestring(name='path', coords=[pre, (portal.lngE6*1e-6, portal.latE6*1e-6)])
        pre = (portal.lngE6*1e-6, portal.latE6*1e-6)
    kml.save(tofile)

class find_path(object):
    INIT_TEMPERATURE = 290
    DROP_TEMPERATURE = 0.92

    def __call__(self, portals):
        random.shuffle(portals)
        self.current = list(portals)
        self.current_len = sum((self.distance(p1, p2) for p1, p2 in zip(portals, portals[1:])))\
                                + self.distance(portals[0], portals[-1])
        self.best = list(self.current)
        self.best_len = self.current_len

        temperature = self.INIT_TEMPERATURE
        not_changed_cnt = 0
        i = 0

        while True:
            i += 1
            changed = False
            for _ in xrange(100*len(portals)):
                next_status, next_len = self.select_neighbor_status()
                
                if next_len < self.best_len:
                    self.best = list(next_status)
                    self.best_len = next_len

                if next_len < self.current_len:
                    if abs(next_len - self.current_len) > 1:
                        changed = True
                    self.current = next_status
                    self.current_len = next_len
                else:
                    pt = cmath.exp( -(next_len - self.current_len) / temperature )
                    if pt.real > random.random():
                        if abs(next_len - self.current_len) > 1:
                            changed = True
                        self.current = next_status
                        self.current_len = next_len

            if not changed:
                if not_changed_cnt > 2:
                    break
                else:
                    not_changed_cnt += 1
            else:
                not_changed_cnt = 0

            temperature = self.DROP_TEMPERATURE*temperature
            logging.debug('%s %s' % (i, self.best_len))

        return self.best


    def distance(self, p1, p2):
        return ((abs(p1.latE6 - p2.latE6)*LAT_FIX) ** 2 + (abs(p1.lngE6 - p2.lngE6)*LNG_FIX) ** 2) ** 0.5

    def select_neighbor_status(self):
        if len(self.current) <= 2:
            return self.current, self.current_len
        status = list(self.current)
        nlen = self.current_len
        i, j = sorted(random.sample(xrange(len(self.current)), 2))
        status = self.current[:i]+list(reversed(self.current[i:j]))+self.current[j:]
        nlen = self.current_len\
                - self.distance(self.current[i-1], self.current[i])\
                - self.distance(self.current[j-1], self.current[j])\
                + self.distance(self.current[i-1], self.current[j-1])\
                + self.distance(self.current[j], self.current[i])
        #_nlen = sum((self.distance(p1, p2) for p1, p2 in zip(status, status[1:])))
        #assert abs(nlen - _nlen) < 1, (i, j, nlen, _nlen, nlen-_nlen)
        return status, nlen

find_path = find_path()

if __name__ == '__main__':
    session = database.Session()
    portals = session.query(database.Portal).filter(database.Portal.ignore == 0).all()
    start_time = time.time()
    path = find_path(portals)
    print time.time() - start_time
    draw_path(path)

    #points = numpy.vstack([(x.latE6*LAT_FIX, x.lngE6*LNG_FIX) for x in portals])
    #labels, error, nfound = Pycluster.kcluster(points, TOTAL_GROUP)
    #groups = {}
    #for group, portal in zip(labels, portals):
        #portal.group = group
        #groups.setdefault(group, []).append(portal)

    #path = []
    #for group, portals in groups.items():
        #path.extend(find_path(portals))
    #draw_path(path)
