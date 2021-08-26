import aiofiles
import aiofiles.os
import aiohttp
from oppai import *

from singletons.config import Config


async def download_map(beatmap_id):
    path = '%s/%s.osu' % (Config()['oppai']['map_dir'], beatmap_id)

    async with aiohttp.ClientSession() as session:
        async with session.get('https://osu.ppy.sh/osu/%s' % beatmap_id) as resp:
            if resp.status == 200:
                f = await aiofiles.open(path, mode='wb')
                await f.write(await resp.read())
                await f.close()


async def ensure_map_exists(beatmap_id):
    path = '%s/%s.osu' % (Config()['oppai']['map_dir'], beatmap_id)

    try:
        stat = await aiofiles.os.stat(path)
    except FileNotFoundError:
        return await download_map(beatmap_id)
    if stat.st_size == 0:
        return await download_map(beatmap_id)


async def get_pp_spread(beatmap_id, enabled_mods, combo=None):
    # get spread (95, 98, 99, 100 acc pps)
    await ensure_map_exists(beatmap_id)
    ez = ezpp_new()
    ezpp_set_autocalc(ez, 1)
    ezpp_dup(ez, '%s/%s.osu' % (Config()['oppai']['map_dir'], beatmap_id))

    if enabled_mods & 4:
        ezpp_set_mods(ez, enabled_mods ^ 64)
    ezpp_set_mods(ez, enabled_mods)

    if combo:
        ezpp_set_combo(ez, combo)

    ezpp_set_accuracy_percent(ez, 95)
    pp95 = ezpp_pp(ez)
    ezpp_set_accuracy_percent(ez, 98)
    pp98 = ezpp_pp(ez)
    ezpp_set_accuracy_percent(ez, 99)
    pp99 = ezpp_pp(ez)
    ezpp_set_accuracy_percent(ez, 100)
    pp100 = ezpp_pp(ez)
    stars = ezpp_stars(ez)
    ar = ezpp_ar(ez)
    od = ezpp_od(ez)
    ezpp_free(ez)
    return pp95, pp98, pp99, pp100, stars, ar, od


async def get_pp(beatmap_id, enabled_mods, accuracy, combo=None):
    # returns total_pp for a specific accuracy
    await ensure_map_exists(beatmap_id)
    ez = ezpp_new()
    ezpp_set_autocalc(ez, 1)
    ezpp_dup(ez, '%s/%s.osu' % (Config()['oppai']['map_dir'], beatmap_id))

    if enabled_mods & 4:
        ezpp_set_mods(ez, enabled_mods ^ 64)
    ezpp_set_mods(ez, enabled_mods)

    if combo:
        ezpp_set_combo(ez, combo)

    ezpp_set_accuracy_percent(ez, accuracy)
    pp = ezpp_pp(ez)
    stars = ezpp_stars(ez)
    ar = ezpp_ar(ez)
    od = ezpp_od(ez)
    ezpp_free(ez)
    return pp, stars, ar, od


async def get_pps(beatmap_id, enabled_mods, maxcombo, countmiss, count50, count100):
    # returns total_pp, aim_pp, speed_pp, acc_pp
    await ensure_map_exists(beatmap_id)
    ez = ezpp_new()
    ezpp_set_mods(ez, enabled_mods)

    if maxcombo:
        ezpp_set_combo(ez, maxcombo)
    if countmiss:
        ezpp_set_nmiss(ez, countmiss)
    if count100 and count50:
        ezpp_set_accuracy(ez, count100, count50)

    ezpp(ez, '%s/%s.osu' % (Config()['oppai']['map_dir'], beatmap_id))
    ret = (ezpp_pp(ez), ezpp_aim_pp(ez), ezpp_speed_pp(ez), ezpp_acc_pp(ez))
    ezpp_free(ez)
    return ret
