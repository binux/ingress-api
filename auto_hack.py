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
import ingress as _ingress
import database
import gen_path

import logging;logging.getLogger().setLevel(logging.INFO)
log.enable_pretty_logging()

COOLDOWN_MSG = {u'gameBasket': {u'deletedEntityGuids': [],
                  u'gameEntities': [],
                  u'inventory': []},
                  u'result': {u'addedGuids': []}}

_continue = True
_debug = True

_collect_xm = True
_hack = True
_pickup = False
_install_mod = False
_upgrade = False
_destroy = False
_deploy = False
_max_level = False
drop_item = ['EMITTER_A|2', 'EMITTER_A|3', 'EMP_BURSTER|1', 'EMP_BURSTER|2', 'EMP_BURSTER|3', ]

def report_location(self):
    for each in drop_item:
        item = self.bag.get_by_group(each)
        if item:
            self.drop(item)
            return
    return

if __name__ == '__main__':
    group = raw_input('portal group: ')
    _ingress.Ingress.report_location = report_location
    ingress = _ingress.Ingress()
    ingress.login()
    ingress.update_inventory()

    logging.info('query portals...')
    portals = ingress.session.query(database.Portal)\
            .filter(database.Portal.ignore == 0)\
            .filter(database.Portal.group == group).all()
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

    for portal in itertools.cycle(path):
        if not _continue:
            break
        try:
            # move
            need_time = ingress.goto(portal, wait=False)
            logging.info('goto %s need %ds' % (portal, need_time))
            ingress.target = portal
            need_time = ingress.goto(portal)

            # collect xm
            if _collect_xm and ingress.player_info['energyState'] != 'XM_OK'\
                    or ingress.player_info['energy'] < max(1500, ingress.max_energy - 3000):
                orig_energy = ingress.player_info['energy']
                #nearby = ingress.scan()
                xm = ingress.collect_xm()
                #for each in ingress.pickup(nearby):
                    #logging.info('pickup %r' % each)
                logging.warning('energy +%d' % (ingress.player_info['energy'] - orig_energy))

            # hack
            if _hack:
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

            if not isinstance(ingress.target, _ingress.Portal):
                ingress.scan()

            if not isinstance(ingress.target, _ingress.Portal):
                continue

            # install mod
            if _install_mod and ingress.target.controlling == ingress.player_team:
                for i, mod in enumerate(ingress.target.mods):
                    if mod is not None:
                        continue
                    item = ingress.bag.get_by_group('RES_SHIELD')
                    if not item:
                        continue
                    ret = ingress.add_mod(item, index=i)
                    if ret.get('error'):
                        logging.error(ret.get('error'))

            # upgrade
            if _upgrade and ingress.target.controlling == ingress.player_team:
                if not ingress.target.full:
                    continue
                res_limit = list(ingress.res_limit)
                for res in ingress.target.resonators:
                    if res and res['ownerGuid'] == ingress.player_id:
                        res_limit[res['level']] -= 1
                for i, res in enumerate(ingress.target.resonators):
                    if res['ownerGuid'] == ingress.player_id:
                        continue
                    if res['level'] >= ingress.player_level:
                        continue
                    for j in range(res['level']+1, ingress.player_level+1):
                        if res_limit[j] <= 0:
                            continue
                        item = ingress.bag.get_by_group('EMITTER_A', j)
                        if not item:
                            continue
                        ret = ingress.upgrade(item, slot=i)
                        if ret.get('error'):
                            logging.error(ret.get('error'))
                        else:
                            res_limit[j] -= 1
                        break

            # deploy
            if _deploy and ingress.target.controlling == 'NEUTRAL':
                ingress.goto(ingress.target.latlng.goto(0, 39))
                ingress.deploy_full(max_level=_max_level)
                if _install_mod:
                    for i, mod in enumerate(ingress.target.mods):
                        if mod is not None:
                            continue
                        item = ingress.bag.get_by_group('RES_SHIELD')
                        if not item:
                            continue
                        ret = ingress.add_mod(item, index=i)
                        if ret.get('error'):
                            logging.error(ret.get('error'))

            # destroy
            enemy = 'RESISTANCE' if ingress.player_team == 'ALIENS' else 'ALIENS'
            if _destroy and ingress.target.controlling == enemy:
                ingress.destroy()

                if _deploy:
                    ingress.deploy_full(max_level=_max_level)
                    if _install_mod:
                        for i, mod in enumerate(ingress.target.mods):
                            if mod is not None:
                                continue
                            item = ingress.bag.get_by_group('RES_SHIELD')
                            if not item:
                                continue
                            ret = ingress.add_mod(item, index=i)
                            if ret.get('error'):
                                logging.error(ret.get('error'))

        except Exception, e:
            logging.exception(e)
            if _debug:
                import IPython; IPython.embed()
            continue
        except KeyboardInterrupt:
            import IPython; IPython.embed()
            continue
