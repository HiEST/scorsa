import math

import scorsa

def sched_fcfs(config, system, jobs, curr, available, pending):
    step = config.getfloat("simulator", "step")
    reshape = config.getfloat("simulator", "reshape")
    digits = config.getint("simulator", "digits")

    schedule = {}

    for jid in pending:
        job = jobs[jid]
        family = system.keys()[0]
        num_cpus = job["tasks"]
        num_nodes = job["tasks"]
        time = job["time"]

        if num_cpus > len(available[family]):
            break

        cpus = available[family][0:num_cpus]
        available[family] = available[family][num_cpus:]

        end = curr + scorsa.f2step(reshape + time, step, digits)

        schedule[jid] = {}
        schedule[jid]["family"] = family
        schedule[jid]["cpus"] = cpus
        schedule[jid]["nodes"] = num_nodes
        schedule[jid]["start"] = curr
        schedule[jid]["end"] = end

    for jid in schedule.keys():
        pending.remove(jid)

    return schedule
