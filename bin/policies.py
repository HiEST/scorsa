import math

def sched_min_exec(system, available, jobs, pending):
    for jid in pending:
        job = jobs[jid]

        family = None
        cpus = None
        nodes = None
        time = None
        found = False

        for f in job["times"].keys():
            for cpn, t in job["times"][f].iteritems():
                if not time or t < time:
                    family = f
                    num_cpu = math.ceil(float(job["tasks"]) / system[f]["cores"])
                    num_mem = math.ceil(float(job["mem"]) / system[f]["mem"])
                    cpus = max(num_cpu, num_mem)
                    nodes = math.ceil(cpus / int(cpn))
                    time = t
                    found = True

        if not found:
            continue

        if cpus > len(available[family]):
            break

        return [jid, family, int(cpus), int(nodes), time]

    return None
