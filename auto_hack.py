#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2013-01-26 13:27:42

import time
import logging

import ingress
import database
import gen_path

import logging;logging.getLogger().setLevel(logging.INFO)


COOLDOWN_MSG = {u'gameBasket': {u'deletedEntityGuids': [],
                  u'gameEntities': [],
                  u'inventory': []},
                  u'result': {u'addedGuids': []}}

if __name__ == '__main__':
    ingress = ingress.Ingress()
    ingress.login()
    portals = ingress.session.query(database.Portal).filter(database.Portal.ignore == 0).all()
    path = gen_path.find_path(portals)

    _continue = False
    for portal in path:
        try:
            need_time = ingress.goto(portal.latE6*1e-6, portal.lngE6*1e-6, wait=False)
            logging.info('goto %s need %ds' % (portal, need_time))
            need_time = ingress.goto(portal.latE6*1e-6, portal.lngE6*1e-6)

            hack = ingress.hack(portal)
            if hack == COOLDOWN_MSG:
                start_time = time.time()
                while hack == COOLDOWN_MSG:
                    time.sleep(30)
                    logging.error('cooldown +%ds' % (time.time()-start_time))
                    hack = ingress.hack(portal)

            if hack.get('error'):
                logging.error(hack.get('error'))
            else:
                for each in hack['result']['addedGuids']:
                    logging.info(ingress.inventory[each])

            if ingress.player_info['energyState'] != 'XM_OK'\
                    or ingress.player_info['energy'] < ingress.max_energy * 0.5:
                orig_energy = ingress.player_info['energy']
                xm = ingress.collect_xm()
                logging.warning('energy +%d' % (ingress.player_info['energy'] - orig_energy))
        except Exception, e:
            print e
            import IPython; IPython.embed()
            continue
        except KeyboardInterrupt:
            import IPython; IPython.embed()
            continue
