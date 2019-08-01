

import numpy as np

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


def map_layout(data):
    m = {}
    sled_id = 0
    draw_id = 0
    rack_id = 0

    for (x, y), value in np.ndenumerate(data):
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

    for _, sids in by_rack.items():
        sids = sorted(sids)
        fragments = []
        for k, group in groupby(enumerate(sids), lambda i_x: i_x[0] - i_x[1]):
            fragments.append(len(list(map(itemgetter(1), group))))
        f += 1 - max(fragments) / sum(fragments)

    return f / len(by_rack)


def list_sockets(nodes):
    return list(chain.from_iterable(nodes))


def list_free_sockets(free):
    nodes = []
    for f in list(free.values()):
        for l, n in f.items():
            nodes.append(n)
    return list(chain.from_iterable(chain.from_iterable(nodes)))
