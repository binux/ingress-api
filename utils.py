#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2013-01-24 20:04:52

import cmath
import string
digs = string.digits + string.lowercase

def int2base(x, base):
    assert isinstance(x, int)
    if x < 0:
        sign = -1
    elif x==0:
        return '0'
    else:
        sign = 1

    digits = []
    while x:
        digits.append(digs[x%base])
        x /= base
    if sign < 0:
        digits.append('-')
    digits.reverse()
    return ''.join(digits)

PI = 3.1415
def to_rad(a):
    return a * PI / 180

def to_deg(a):
    return a * 180 / PI

class LatLng(object):
    R = 6371*1000

    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

    def distance_to(self, point):
        lat1 = to_rad(self.lat)
        lng1 = to_rad(self.lng)
        lat2 = to_rad(point.lat)
        lng2 = to_rad(point.lng)
        dLat = lat2 - lat1
        dlng = lng2 - lng1

        a = cmath.sin(dLat/2.0) * cmath.sin(dLat/2.0) \
                + cmath.cos(lat1) * cmath.cos(lat2) \
                * cmath.sin(dlng/2) * cmath.sin(dlng/2)
        c = 2 * cmath.atan(cmath.sqrt(a) / cmath.sqrt(1-a));
        d = self.R * c;
        return d.real

    def bearing_to(self, point):
        lat1 = to_rad(self.lat)
        lat2 = to_rad(point.lat)
        dLng = to_rad(point.lng - self.lng)

        y = cmath.sin(dLng) * cmath.cos(lat2);
        x = cmath.cos(lat1) * cmath.sin(lat2) \
                - cmath.sin(lat1) * cmath.cos(lat2) * cmath.cos(dLng)
        brng = cmath.atan(y / x)
        return (to_deg(brng.real)+180) % 360

    def goto(self, brng, dist):
        if isinstance(brng, LatLng):
            brng = self.bearing_to(brng)
        brng = to_rad(brng)
        dist = float(dist) / self.R

        lat1 = to_rad(self.lat)
        lng1 = to_rad(self.lng)

        lat2 = cmath.asin(cmath.sin(lat1) * cmath.cos(dist) + 
                          cmath.cos(lat1) * cmath.sin(dist) * cmath.cos(brng))
        lng2 = lng1 + cmath.atan((cmath.sin(brng) * cmath.sin(dist) * cmath.cos(lat1)) \
                                / (cmath.cos(dist) - cmath.sin(lat1) * cmath.sin(lat2)))
        lng2 = (lng2+3*PI) % (2*PI) - PI

        return LatLng(to_deg(lat2.real), to_deg(lng2.real))

    def __repr__(self):
        return '<LatLng %f,%f>' % (self.lat, self.lng)

    def __sub__(self, other):
        return self.distance_to(other)

if __name__ == '__main__':
    assert int(LatLng(40, 116).distance_to(LatLng(35, 147))) == 2775934
    assert int(LatLng(40, 116) - LatLng(35, 147)) == 2775934
    assert int(LatLng(40, 116).bearing_to(LatLng(35, 147))) == 91
    assert LatLng(40, 116).goto(LatLng(35, 147), 2775934) - LatLng(35, 147) < 1000
