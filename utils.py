#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2013-01-24 20:04:52

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
