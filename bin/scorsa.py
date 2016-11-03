from __future__ import division

import numpy as np
import math

from collections import defaultdict
from itertools import groupby, chain
from operator import itemgetter


# Convert standard time in float format to discrete time in "step" format.
def step(time, period, digits):
    s = time - (time % period)
    s = s + period if time % period != 0 else s
    return round(s, digits)


# Generate list of time steps between the specified interval. Similar to
# Python's range(), with float support.
def steps(start, stop, period, digits):
    r = start
    while r < stop:
        yield round(r, digits)
        r += period


def map_layout(data,layout_info):
    m = {}
    sled_id = 0
    draw_id = 0
    rack_id = 0
    sockets = 0

    for (x,y), value in np.ndenumerate(data):
        if y == 0:
            rack_id = 0

        if value == "|":
            rack_id += 1

        if value.startswith("--") and y == 0:
            draw_id += 1

        if value == "|" or value.startswith("-"):
            continue

        for sled in value.split("-"):
            for sid in sled.split("+"):
                sid = int(sid)
                m[sid] = {}
                m[sid]["x"] = x
                m[sid]["y"] = y
                m[sid]["sled_id"] = sled_id
                m[sid]["draw_id"] = draw_id
                m[sid]["rack_id"] = rack_id
                sockets += 1

        sled_id += 1

    layout_info["n_racks"] = rack_id+1
    layout_info["n_drawers"] = (draw_id+1)*layout_info["n_racks"]
    layout_info["sleds_drawer"] = (sled_id / layout_info["n_racks"])/(draw_id+1)
    layout_info["n_sleds"] = sled_id
    layout_info["n_sockets"] = sockets
    layout_info["sockets_sled"] = sockets / sled_id
    return m


def distance(layout, a, b):
    d = 0
    if a != b:
        d = 1
    if layout[a]["sled_id"] != layout[b]["sled_id"]:
        d = 10
    if layout[a]["draw_id"] != layout[b]["draw_id"]:
        d = 100
    if layout[a]["rack_id"] != layout[b]["rack_id"]:
        d = 1000
    return d


def fragmentation(layout, subset):
    f = 0.0
    by_rack = defaultdict(list)

    if len(subset) == 0:
        return f

    for sid in subset:
        by_rack[layout[sid]['rack_id']].append(sid)

    for _, sids in by_rack.iteritems():
        sids = sorted(sids)
        fragments = []
        for k, group in groupby(enumerate(sids), lambda (i, x): i - x):
            fragments.append(len(map(itemgetter(1), group)))
        f += 1 - max(fragments) / sum(fragments)

    return f / len(by_rack)


def system_fragmentation(layout, used, layout_info):
    racks_used = defaultdict(list)
    drawers_used = defaultdict(list)
    resources_drawer_used = defaultdict(list)
    blocks_drawer_used = defaultdict(list)
    blocks_rack_used = defaultdict(list)
    for sid in used:
        draw_id = layout[sid]["draw_id"]
        rack_id = layout[sid]["rack_id"]
        sled_id = layout[sid]["sled_id"]
        if rack_id not in racks_used:
            racks_used[rack_id] = []
            blocks_rack_used[rack_id] = 0
            drawers_used[rack_id] = defaultdict(list)

        if draw_id not in drawers_used[rack_id]:
            drawers_used[rack_id][draw_id] = []
            blocks_rack_used[rack_id] += 1
            blocks_drawer_used[draw_id] = defaultdict(list)
            resources_drawer_used[draw_id] = 0

        if sled_id not in blocks_drawer_used[draw_id]:
            blocks_drawer_used[draw_id][sled_id] = 0

        blocks_drawer_used[draw_id][sled_id] += 1
        resources_drawer_used[draw_id] += 1

    f_racks = 0
    for rid in racks_used:
        f_drawers = 0
        f_rack = 0
        resources_drawers_used = 0
        for draw_id in drawers_used[rid]:
            blocks_total = layout_info["sleds_drawer"]
            resources_total = blocks_total * layout_info["sockets_sled"]
            min_blocks = math.ceil((resources_drawer_used[draw_id] / resources_total)*blocks_total)
            if min_blocks == 1 and len(blocks_drawer_used[draw_id]) == blocks_total:
                f_drawers += 1
            else:
                f_drawers += (len(blocks_drawer_used[draw_id]) - min_blocks) / blocks_total

            for sled in blocks_drawer_used[draw_id]:
                resources_drawers_used += blocks_drawer_used[draw_id][sled]

        blocks_total = layout_info["n_drawers"] / layout_info["n_racks"]
        resources_total = blocks_total * layout_info["sleds_drawer"] * layout_info["sockets_sled"]
        min_blocks = math.ceil((resources_drawers_used / resources_total)*blocks_total)
        if min_blocks == 1 and len(drawers_used[rid]) == blocks_total:
            f_rack += 1
        else:
            f_rack += (len(drawers_used[rid]) - min_blocks) / blocks_total

        f_drawers /= blocks_total
        f_racks += (f_rack + f_drawers) / 2

    return f_racks / layout_info["n_racks"]


def system_fragmentation_lookahead(layout, used, layout_info):
    racks_used = defaultdict(list)
    drawers_used = defaultdict(list)
    resources_drawer_used = defaultdict(list)
    blocks_drawer_used = defaultdict(list)
    blocks_rack_used = defaultdict(list)
    for sid in used:
        draw_id = layout[sid]["draw_id"]
        rack_id = layout[sid]["rack_id"]
        sled_id = layout[sid]["sled_id"]
        if rack_id not in racks_used:
            racks_used[rack_id] = []
            blocks_rack_used[rack_id] = 0
            drawers_used[rack_id] = defaultdict(list)

        if draw_id not in drawers_used[rack_id]:
            drawers_used[rack_id][draw_id] = []
            blocks_rack_used[rack_id] += 1
            blocks_drawer_used[draw_id] = defaultdict(list)
            resources_drawer_used[draw_id] = 0

        if sled_id not in blocks_drawer_used[draw_id]:
            blocks_drawer_used[draw_id][sled_id] = 0

        blocks_drawer_used[draw_id][sled_id] += 1
        resources_drawer_used[draw_id] += 1

    f_racks = 0
    for rid in racks_used:
        f_drawers = 0
        f_rack = 0
        resources_drawers_used = 0
        for draw_id in drawers_used[rid]:
            blocks_total = layout_info["sleds_drawer"]
            resources_total = blocks_total * layout_info["sockets_sled"]
            min_blocks = math.ceil((resources_drawer_used[draw_id] / resources_total)*blocks_total)
            mgap = resources_drawer_used[draw_id] % resources_total
            ogap = (min_blocks - (resources_drawer_used[draw_id] / layout_info["sockets_sled"]))*layout_info["sockets_sled"]
            if mgap == ogap:
                f_drawers += 0
            else:
                f_drawers += 1 - (abs(mgap - ogap) / layout_info["sockets_sled"])

            for sled in blocks_drawer_used[draw_id]:
                resources_drawers_used += blocks_drawer_used[draw_id][sled]

        blocks_total = layout_info["n_drawers"] / layout_info["n_racks"]
        block_resources = layout_info["sleds_drawer"] * layout_info["sockets_sled"]
        resources_total = blocks_total * layout_info["sleds_drawer"] * layout_info["sockets_sled"]
        min_blocks = math.ceil((resources_drawers_used / resources_total)*blocks_total)
        mgap = resources_drawers_used % block_resources
        ogap = (min_blocks - (resources_drawers_used / block_resources))*block_resources
        if mgap == ogap:
            f_rack += 0
        else:
            f_rack += 1 - (abs(mgap - ogap) / block_resources)

        f_drawers /= blocks_total
        f_racks += (f_rack + f_drawers) / 2

    return f_racks / layout_info["n_racks"]


def list_sockets(nodes):
    return list(chain.from_iterable(nodes))


def list_free_sockets(free):
    nodes = []
    for f in free.values():
        for l, n in f.iteritems():
            nodes.append(n)
    return list(chain.from_iterable(chain.from_iterable(nodes)))


def list_used_sockets(free,layout):
    used = []
    for sid in layout:
        if sid not in free:
            used.append(sid)

    return used
