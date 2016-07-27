import math

from collections import defaultdict

import scorsa

def allocate_nodes(config, free, family, num_nodes, node_size):
    reuse = config.getboolean("composition", "reuse")
    ff = free[family]
    num_cpus = num_nodes * node_size

    # 1. Reuse node if available
    if reuse and node_size in ff.keys() and len(ff[node_size]) >= num_nodes:
        nodes = ff[node_size][0:num_nodes]
        ff[node_size] = ff[node_size][num_nodes:]
        return False, nodes

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

    cpus = scorsa.list_cpus(ff[1][0:num_cpus])
    nodes = [cpus[i:i+node_size] for i in range(0, len(cpus), node_size)]
    ff[1] = ff[1][num_cpus:]
    return True, nodes

def free_nodes(free, family, nodes):
    for node in nodes:
        free[family][len(node)].append(node)

def sched_fcfs(config, curr, jobs, pending, free):
    period = config.getfloat("simulator", "period")
    digits = config.getint("simulator", "digits")
    compose = config.getfloat("composition", "time")
    backscale = config.getboolean("scheduler", "backscale")

    schedule = {}

    for jid in pending:
        job = jobs[jid]
        family = free.keys()[0]
        num_cpus = job["tasks"]
        num_nodes = 1 if job["scale"] == "up" else num_cpus
        node_size = num_cpus / num_nodes
        time = job["time"]
        backscaled = False

        alloc = allocate_nodes(config, free, family, num_nodes, node_size)
        if alloc == None and not backscale:
            break

        num_free = len(scorsa.list_free_cpus(free))
        if alloc == None and num_free == 0:
            break

        if alloc == None:
            num_cpus = num_free
            num_nodes = 1 if job["scale"] == "up" else num_cpus
            node_size = num_cpus / num_nodes
            time = time * (1 / (float(num_cpus) / job["tasks"]))
            alloc = allocate_nodes(config, free, family, num_nodes, node_size)
            backscaled = True

        recomposed, nodes = alloc
        if recomposed:
            time = time + compose

        schedule[jid] = {}
        schedule[jid]["family"] = family
        schedule[jid]["nodes"] = nodes
        schedule[jid]["start"] = curr
        schedule[jid]["end"] = curr + scorsa.step(time, period, digits)
        schedule[jid]["reused"] = not recomposed
        schedule[jid]["backscaled"] = backscaled

    for jid in schedule.keys():
        pending.remove(jid)

    return schedule
