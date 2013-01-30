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
    ingress.update_inventory()
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
    _debug = True
    for portal in itertools.cycle(path):
        if not _continue:
            break
        try:
            # move
            need_time = ingress.goto(portal.latlng, wait=False)
            logging.info('goto %s need %ds' % (portal, need_time))
            need_time = ingress.goto(portal.latlng)

            # hack
            hack = ingress.hack(portal)
            if hack == COOLDOWN_MSG:
                start_time = time.time()
                while hack == COOLDOWN_MSG:
                    logging.error('cooldown +%ds' % (time.time()-start_time+30))
                    time.sleep(30)
                    hack = ingress.hack(portal)
            if hack.get('error'):
                logging.error(hack.get('error'))
            else:
                for each in hack['result']['addedGuids']:
                    logging.info('hacked %s' % ingress.bag.get(each))

            # auto pick and upgrade
            nearby = ingress.scan()
            for each in nearby:
                if isinstance(each, ingress.Item)\
                        and each.type in ('PORTAL_LINK_KEY', 'RES_SHIELD', ):
                    for each in self.pickup(each):
                        logging.info('pickup %s' % each)
                elif isinstance(each, ingress.Portal)\
                        and each.guid == portal.guid:
                    ingress.target = each
                    # install mod
                    for i, mod in enumerate(ingress.target.mods):
                        if mod is None:
                            item = ingress.bag.get_by_group('RES_SHIELD')
                            if item:
                                ingress.add_mod(item, index=i)

                    # upgrade
                    if ingress.target.full:
                        res_limit = list(ingress.res_limit)
                        for res in portal.resonators:
                            if res['ownerGuid'] == ingress.player_id:
                                res_limit[res['level']] -= 1
                        for i, res in enumerate(portal.Resonators):
                            if res['ownerGuid'] == ingress.player_id:
                                continue
                            if res['level'] >= ingress.player_level:
                                continue
                            for j in range(res['level']+1, ingress.player_level+1):
                                if res_limit[j] <= 0:
                                    continue
                                item = ingress.bag.get_by_group('EMP_BURSTER', j)
                                if item:
                                    ingress.upgrade(item, slot=i)
                                    res_limit[j] -= 1
                                    break

            if ingress.player_info['energyState'] != 'XM_OK'\
                    or ingress.player_info['energy'] < max(ingress.max_energy * 0.5, 500):
                orig_energy = ingress.player_info['energy']
                #nearby = ingress.scan()
                xm = ingress.collect_xm()
                #for each in ingress.pickup(nearby):
                    #logging.info('pickup %r' % each)
                logging.warning('energy +%d' % (ingress.player_info['energy'] - orig_energy))
        except Exception, e:
            logging.exception(e)
            if _debug:
                import IPython; IPython.embed()
            continue
        except KeyboardInterrupt:
            import IPython; IPython.embed()
            continue
