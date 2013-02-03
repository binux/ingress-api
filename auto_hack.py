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
_hack_log = True
_auto_drop = True
_pickup = False
_install_mod = False
_upgrade = False
_destroy = False
_deploy = False
_max_level = False
drop_item = {
        'RES_SHIELD|10': 2000,
        'RES_SHIELD|8': 1000,
        'RES_SHIELD|6': 500,
        'EMITTER_A|1': 1000,
        'EMITTER_A|2': 0,
        'EMITTER_A|3': 0,
        'EMITTER_A|4': 800,
        'EMITTER_A|5': 500,
        'EMITTER_A|6': 500,
        'EMITTER_A|7': 1000,
        'EMITTER_A|8': 2000,
        'EMP_BURSTER|1': 100,
        'EMP_BURSTER|2': 50,
        'EMP_BURSTER|3': 50,
        'EMP_BURSTER|4': 100,
        'EMP_BURSTER|5': 500,
        'EMP_BURSTER|6': 800,
        'EMP_BURSTER|7': 1000,
        'EMP_BURSTER|8': 2000,
        }

auto_drop_cnt = 0

def report_location(self):
    pass
#_ingress.Ingress._report_location = _ingress.Ingress.report_location
#_ingress.Ingress.report_location = report_location

if __name__ == '__main__':
    group = raw_input('portal group: ')
    ingress = _ingress.Ingress()
    ingress.login()
    ingress.update_inventory()
    log_session = database.LogSession()

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
                        auto_drop_cnt += 1

            if not isinstance(ingress.target, _ingress.Portal):
                ingress.scan()

            if not isinstance(ingress.target, _ingress.Portal):
                continue

            # hack log
            if _hack_log and not hack.get('error') and isinstance(ingress.target, _ingress.Portal):
                hacklog = database.HackLog()
                hacklog.guid = ingress.target.guid
                hacklog.enemy = 0 if ingress.target.controlling == 'NEUTRAL' else 1 if ingress.enemy == ingress.target.controlling else -1
                hacklog.resonators = ''.join([str(x['level']) if x else '0' for x in ingress.target.resonators])
                hacklog.mods = ''.join([str(x['stats']['MITIGATION'])[0] if x else '0' for x in ingress.target.mods])
                hacklog.level = ingress.target.level

                hacklog.damage = sum([int(x['damageAmount']) for x in hack.get('gameBasket', {}).get('playerDamages', [])])
                for each in hack['result']['addedGuids']:
                    item = ingress.bag.get(each)
                    if item.type == ingress.bag.EMITTER_A:
                        setattr(hacklog, 'res%s' % item.level, (getattr(hacklog, 'res%s' % item.level) or 0)+1)
                    elif item.type == ingress.bag.EMP_BURSTER:
                        setattr(hacklog, 'buster%s' % item.level, (getattr(hacklog, 'buster%s' % item.level) or 0)+1)
                    elif item.type == ingress.bag.RES_SHIELD:
                        setattr(hacklog, 'shield%s' % item.mitigation, (getattr(hacklog, 'shield%s' % item.mitigation) or 0)+1)
                    elif item.type == ingress.bag.PORTAL_LINK_KEY:
                        setattr(hacklog, 'key', (getattr(hacklog, 'key') or 0)+1)
                log_session.add(hacklog)
                log_session.commit()

            # auto drop
            if _auto_drop and auto_drop_cnt > 1000:
                auto_drop_cnt = 0
                for group, limit in drop_item.iteritems():
                    if len(ingress.bag.group.get(group, [])) > limit:
                        for guid in ingress.bag.group[group][limit:]:
                            ingress.drop(guid)

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
