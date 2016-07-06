import math

from collections import defaultdict
from itertools import chain

import scorsa

def allocate_cpus(config, free, family, num_cpus):
    reuse = config.getboolean("composition", "reuse")
    ff = free[family]

    # 1. Reuse node if available
    if reuse and num_cpus in ff.keys() and len(ff[num_cpus]) > 0:
        cpus = ff[num_cpus].pop(0)
        return False, cpus

    # 2. Try to compose node from other nodes
    num_free = len(ff[1])
    decomposable = []
    for l, nodes in sorted(ff.items()):
        if l > 1:
            decomposable += [(l, node) for node in nodes]
            num_free += len(nodes) * l

    # 2a. Not enough CPUs
    if num_cpus > num_free:
        return None

    # 2b. Decompose and compose new node
    freed = len(ff[1])
    for l, node in decomposable:
        if freed >= num_cpus:
            break
        ff[l].remove(node)
        ff[1] += [[n] for n in node]
        freed += l

    cpus = ff[1][0:num_cpus]
    ff[1] = ff[1][num_cpus:]
    return True, list(chain.from_iterable(cpus))

def free_cpus(free, family, cpus):
    free[family][len(cpus)].append(cpus)

def sched_fcfs(config, curr, jobs, pending, free):
    step = config.getfloat("simulator", "step")
    digits = config.getint("simulator", "digits")
    compose = config.getfloat("composition", "compose")

    schedule = {}

    for jid in pending:
        job = jobs[jid]
        family = free.keys()[0]
        num_cpus = job["tasks"]
        num_nodes = job["tasks"]
        time = job["time"]

        alloc = allocate_cpus(config, free, family, num_cpus)
        if alloc == None:
            break

        recomposed, cpus = alloc
        if recomposed:
            time = time + compose

        end = curr + scorsa.f2step(time, step, digits)

        schedule[jid] = {}
        schedule[jid]["family"] = family
        schedule[jid]["cpus"] = cpus
        schedule[jid]["nodes"] = num_nodes
        schedule[jid]["start"] = curr
        schedule[jid]["end"] = end
        schedule[jid]["reused"] = not recomposed

    for jid in schedule.keys():
        pending.remove(jid)

    return schedule
