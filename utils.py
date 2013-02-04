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

    def __eq__(self, other):
        return self.lat == other.lat and self.lng == other.lng

    def to_pixel(self, zoom):
        'zoom 11 to 18'
        siny = cmath.sin(to_rad(self.lat))
        y = cmath.log((1 + siny) / (1 - siny));
        lat = (128 << zoom) * (1 - y / (2 * PI));

        lng = (self.lng + 180.0) * (256 << zoom) / 360.0
        return lat.real, lng

    def from_pixel(self, lat, lng, zoom):
        lat = 2 * PI * (1 - lat / (128 << zoom))
        lat = cmath.exp(lat)
        lat = (lat - 1) / (lat + 1)
        self.lat = (cmath.asin(lat) * 180 / PI).real
        self.lng = lng * 360.0 / (256 << zoom) - 180.0
        return self

    def cellid(self):
        lat = self.lat
        lng = self.lng
        d3 = cmath.cos(lat)
        d4 = d3 * cmath.cos(lng).real
        d5 = d3 * cmath.sin(lng).real
        d6 = cmath.sin(lat).real
        d7 = abs(lat)
        d8 = abs(d5)
        d9 = abs(d6)
        i = 3
        d10 = -d5 / d6
        d11 = -d4 / d6

        a = [0, ]*1024
        b = [0, ]*1024

        def b_a_init(p1, p2, p3, p4, p5, p6):
            if p1 == 4:
                i3 = p3 + p2 << 4
                a[p4+(i3<<2)] = p6 + (p5 << 2)
                b[p4+(p5<<2)] = p6 + (i3 << 2)
            while True:
                i = p1 + 1
                j = p2 << 1
                k = p3 << 1
                m = p5 << 2
                for n in range(0, 4):
                    i1 = f_a(p6, n)
                    i2 = f_a(n)
                    a(i, j + (i1 >> 1))
        def b_a(double):
            return int(max(0, min(1073741823, round(536870911.5 + 536870912.0 * double))))
        def aa_b(double):
            return 1.273239544735163 * cmath.atan(double).real

        l = 0
        while True:
            j = b_a(aa_b(d10))
            k = b_a(aa_b(d11))
            l = i << 60
            m = i & 0x1
            for n in range(7, -1, -1):
                i1 = m + ((0xF & j >> n * 4) << 6) + ((0xF & k >> n * 4) << 2)
                print i1
                i2 = a[i1]
                l |= i2 >> 2 << 4 * (n * 2)
                m = i2 & 0x3
        return 1L + (l << 1);

if __name__ == '__main__':
    #assert int(LatLng(40, 116).distance_to(LatLng(35, 147))) == 2775934
    #assert int(LatLng(40, 116) - LatLng(35, 147)) == 2775934
    #assert int(LatLng(40, 116).bearing_to(LatLng(35, 147))) == 91
    #assert LatLng(40, 116).goto(LatLng(35, 147), 2775934) - LatLng(35, 147) < 1000
    #assert LatLng(0, 0).from_pixel(*LatLng(40, 116).to_pixel(zoom=18), zoom=18)# == LatLng(40, 16)
    print LatLng(40, 116).cellid()
