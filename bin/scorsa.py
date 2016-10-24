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

    for (x,y), value in np.ndenumerate(data):
        if y == 0:
            rack_id = 0

        if value == "|":
            rack_id += 1

        if value.startswith("--") and y == 0:
            draw_id += 1

        if value == "|" or value.startswith("-"):
            continue

        for sid in value.split("-"):
            sid = int(sid)
            m[sid] = {}
            m[sid]["x"] = x
            m[sid]["y"] = y
            m[sid]["sled_id"] = sled_id
            m[sid]["draw_id"] = draw_id
            m[sid]["rack_id"] = rack_id

        sled_id += 1

    layout_info["n_racks"] = rack_id+1
    layout_info["n_drawers"] = (draw_id+1)*layout_info["n_racks"]
    layout_info["sleds_drawer"] = (sled_id / layout_info["n_racks"])/(draw_id+1)

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
    blocks_total = math.ceil(layout_info["n_drawers"]/layout_info["n_racks"])
    blocks_resources = layout_info["sleds_drawer"]
    resources_total = blocks_total * blocks_resources
    resources_used = defaultdict(list)
    blocks_seen = defaultdict(list)

    #Determine which sids are used
    for sid in used:
        if layout[sid]["rack_id"] not in resources_used:
            resources_used[layout[sid]["rack_id"]] = 1
            blocks_seen[layout[sid]["rack_id"]] = []
        else:
            resources_used[layout[sid]["rack_id"]] += 1

        if layout[sid]['draw_id'] not in blocks_seen[layout[sid]["rack_id"]]:
            blocks_seen[layout[sid]["rack_id"]].append(layout[sid]['draw_id'])

    sum_f = 0
    for rf in resources_used:
        f = 0
        blocks_used = len(blocks_seen[rf])
        min_blocks = math.ceil((resources_used[rf] / resources_total)*blocks_total)

        if min_blocks == 1 and blocks_used == blocks_total:
            f = 1
        elif min_blocks == 0:
            f = 0
        elif blocks_used == min_blocks:
            f = 0
        else:
            f = (blocks_used - min_blocks) / blocks_total

        sum_f += f

    if sum_f == 0:
        return 0
    else:
        return sum_f / layout_info["n_racks"]


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
