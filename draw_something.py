#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2013-01-27 23:28:19

import log
import utils
import ingress

import logging;logging.getLogger().setLevel(logging.INFO)
log.enable_pretty_logging()

something = """
.##.....##.########.##.......##........#######.....##......##..#######..########..##.......########.....####
.##.....##.##.......##.......##.......##.....##....##..##..##.##.....##.##.....##.##.......##.....##....####
.##.....##.##.......##.......##.......##.....##....##..##..##.##.....##.##.....##.##.......##.....##....####
.#########.######...##.......##.......##.....##....##..##..##.##.....##.########..##.......##.....##.....##.
.##.....##.##.......##.......##.......##.....##....##..##..##.##.....##.##...##...##.......##.....##........
.##.....##.##.......##.......##.......##.....##....##..##..##.##.....##.##....##..##.......##.....##....####
.##.....##.########.########.########..#######......###..###...#######..##.....##.########.########.....####
"""
start_at = utils.LatLng(39.9943428, 116.3864975)
i_meter = 2
j_meter = 2

ingress = ingress.Ingress()
ingress.login()

logging.info('get pen...')
pens = {}
ingress.update_inventory()
for guid, item in ingress.inventory.iteritems():
    name = '%s_%s' % (item.type, item.level) if item.level else item.type
    pens.setdefault(name, []).append(guid)
pens_cnt = {}
for pen_type, cnt in pens.iteritems():
    logging.info('%s x%d' % (pen_type, len(cnt)))
    pens_cnt[pen_type] = len(cnt)

logging.info('analyse something...')
chars = {}
for line in something.splitlines():
    if line == '':
        continue
    for each in line:
        chars.setdefault(each, 0)
        chars[each] += 1
for char, cnt in chars.iteritems():
    logging.info('%r x%d' % (char, cnt))

logging.info('chose pen...')
char_pen_map = {}
for char, cnt in chars.iteritems():
    while True:
        use_pen = raw_input('item for %r:' % char)
        if not use_pen:
            char_pen_map[char] = use_pen
            break
        if use_pen not in pens:
            logging.error('no such pen!')
            continue
        if pens_cnt[use_pen] < cnt:
            logging.error('no enough pen!')
            continue
        pens_cnt[use_pen] -= cnt
        char_pen_map[char] = use_pen
        break

logging.info('drawing...')
for i, line in enumerate(reversed(something.splitlines())):
    if i % 2:
        line = reversed(line)
    for _j, char in enumerate(line):
        if i % 2:
            j = len(line) - _j - 1
        pen = char_pen_map[char]
        if not pen:
            continue
        guid = pens[pen].pop()
        pos = start_at.goto(0, i*i_meter).goto(90, j*j_meter)
        ingress.goto(pos)
        ingress.drop(guid)
