import math

def sched_fcfs(system, available, jobs, pending):
    for jid in pending:
        job = jobs[jid]
        family = system.keys()[0]
        cpus = job["tasks"]
        nodes = job["tasks"]
        time = job["time"]

        if cpus > len(available[family]):
            break

        return [jid, family, int(cpus), int(nodes), time]

    return None

