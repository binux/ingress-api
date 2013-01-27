#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2013-01-26 13:27:42

import time
import logging
import itertools

import log
import utils
import ingress
import database
import gen_path

import logging;logging.getLogger().setLevel(logging.INFO)
log.enable_pretty_logging()

COOLDOWN_MSG = {u'gameBasket': {u'deletedEntityGuids': [],
                  u'gameEntities': [],
                  u'inventory': []},
                  u'result': {u'addedGuids': []}}

if __name__ == '__main__':
    ingress = ingress.Ingress()
    ingress.login()
    logging.info('query portals...')
    portals = ingress.session.query(database.Portal).filter(database.Portal.ignore == 0).all()
    logging.info('gen path...')
    path = gen_path.find_path(portals)

    max_portal = max(path, key=lambda x: x.guid)
    max_index = path.index(max_portal)
    path = path[max_index:]+path[:max_index]

    pre = utils.LatLng(path[-1].latE6*1e-6, path[-1].lngE6*1e-6)
    total_len = 0
    for each in path:
        cur = utils.LatLng(each.latE6*1e-6, each.lngE6*1e-6)
        total_len += cur - pre
        pre = cur
    logging.info('path total length: %fkm, need %fh' % (total_len/1000, total_len / ingress.speed_limit / 60 / 60))

    _continue = True
    _debug = False
    for portal in itertools.cycle(path):
        if not _continue:
            break
        try:
            need_time = ingress.goto(portal.latE6*1e-6, portal.lngE6*1e-6, wait=False)
            logging.info('goto %s need %ds' % (portal, need_time))
            need_time = ingress.goto(portal.latE6*1e-6, portal.lngE6*1e-6)

            hack = ingress.hack(portal)
            if hack == COOLDOWN_MSG:
                start_time = time.time()
                while hack == COOLDOWN_MSG:
                    logging.error('cooldown +%ds' % (time.time()-start_time+30))
                    time.sleep(30)
                    hack = ingress.hack(portal)

            if _debug and hack.get('gameBasket'):
                if hack['gameBasket'].get('apGains'):
                    import IPython; IPython.embed()
                elif hack['gameBasket'].get('playerDamages'):
                    import IPython; IPython.embed()

            if hack.get('error'):
                logging.error(hack.get('error'))
            else:
                game_basket = hack.get('gameBasket', {})
                for each in game_basket.get('apGains', []):
                    logging.info('%s +%saps' % (each['apTrigger'], each['apGainAmount']))
                for each in game_basket.get('playerDamages', []):
                    logging.warning('%s -%sxms' % (each['weaponSerializationTag'], each['damageAmount']))
                for each in hack['result']['addedGuids']:
                    logging.info(ingress.inventory[each])

            if ingress.player_info['energyState'] != 'XM_OK'\
                    or ingress.player_info['energy'] < max(ingress.max_energy * 0.5, 500):
                orig_energy = ingress.player_info['energy']
                xm = ingress.collect_xm()
                logging.warning('energy +%d' % (ingress.player_info['energy'] - orig_energy))
        except Exception, e:
            logging.exception(e)
            if _debug:
                import IPython; IPython.embed()
            continue
        except KeyboardInterrupt:
            import IPython; IPython.embed()
            continue
