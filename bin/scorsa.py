import numpy as np

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

def map_layout(layout):
    m = {}
    rack_id = 0
    drawer_id = 0

    for (x,y), value in np.ndenumerate(layout):
        if y == 0:
            rack_id = 0

        if value == "|":
            rack_id += 1

        if value == "--" and y == 0:
            drawer_id += 1

        if value in ["--", "|", "-1"]:
            continue

        cpu_id = int(value)
        m[cpu_id] = {}
        m[cpu_id]["x"] = x
        m[cpu_id]["y"] = y
        m[cpu_id]["rid"] = rack_id
        m[cpu_id]["did"] = drawer_id

    return m

def distance(procs, a, b):
    d = 0
    if a != b:
	d += 1
    if procs[a]["did"] != procs[b]["did"]:
        d += 10
    if procs[a]["rid"] != procs[b]["rid"]:
        d += 100
    return d
