import math

import scorsa

def sched_fcfs(config, system, jobs, curr, available, pending):
    step = config.getfloat("simulator", "step")
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

        pending.remove(jid)
        cpus = available[family][0:num_cpus]
        available[family] = available[family][num_cpus:]

        end = curr + scorsa.f2step(time, step, digits)

        schedule[jid] = {}
        schedule[jid]["family"] = family
        schedule[jid]["cpus"] = cpus
        schedule[jid]["nodes"] = num_nodes
        schedule[jid]["start"] = curr
        schedule[jid]["end"] = end

    return schedule
