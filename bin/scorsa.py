from __future__ import division

import numpy as np

from collections import defaultdict
from itertools import groupby, chain
from operator import itemgetter

def f2step(f, step, digits):
    s = f - (f % step)
    s = s + step if f % step != 0 else s
    return round(s, digits)

# range with float support
def rangef(start, stop, step, digits):
    r = start
    while r < stop:
        yield round(r, digits)
        r += step

def map_layout(data):
    m = {}
    rack_id = 0
    drawer_id = 0

    for (x,y), value in np.ndenumerate(data):
        if y == 0:
            rack_id = 0

        if value == "|":
            rack_id += 1

        if value == "--" and y == 0:
            drawer_id += 1

        if value in ["--", "|", "-1"]:
            continue

        cid = int(value)
        m[cid] = {}
        m[cid]["x"] = x
        m[cid]["y"] = y
        m[cid]["rid"] = rack_id
        m[cid]["did"] = drawer_id

    return m

def distance(layout, a, b):
    d = 0
    if a != b:
	d += 1
    if layout[a]["did"] != layout[b]["did"]:
        d += 10
    if layout[a]["rid"] != layout[b]["rid"]:
        d += 100
    return d

def fragmentation(layout, subset):
    f = 0.0
    by_rack = defaultdict(list)

    if len(subset) == 0:
        return f

    for cid in subset:
        by_rack[layout[cid]['rid']].append(cid)

    for rid, cids in by_rack.iteritems():
        cids = sorted(cids)
        fragments = []
        for k, group in groupby(enumerate(cids), lambda (i, x): i - x):
            fragments.append(len(map(itemgetter(1), group)))
        f += 1 - max(fragments) / sum(fragments)

    return f / len(by_rack)

def list_free_cpus(free):
    nodes = []
    for f in free.values():
        for l, n in f.iteritems():
            nodes.append(n)
    return list(chain.from_iterable(chain.from_iterable(nodes)))
