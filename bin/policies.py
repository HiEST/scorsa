import math
import random

from collections import defaultdict

import scorsa

def resource_selection_composition_and_placement(config, free: dict, family: str, num_nodes:int , node_size: int):
    reuse = config.getboolean("composition", "reuse")
    ff = free[family]
    num_sockets = num_nodes * node_size

    # 1. Reuse pre-composed node if available
    if reuse and node_size in list(ff.keys()) and len(ff[node_size]) >= num_nodes:
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

    # 2a. Not enough sockets
    if num_sockets > num_free:
        return None

    # 2b. Decompose and compose new node
    freed = len(ff[1])
    for l, node in decomposable:
        if freed >= num_sockets:
            break
        ff[l].remove(node)
        ff[1] += [[n] for n in node]
        freed += l

    sockets = scorsa.list_sockets(ff[1][0:num_sockets])
    nodes = [sockets[i:i+node_size] for i in range(0, len(sockets), node_size)]
    ff[1] = ff[1][num_sockets:]
    return True, nodes



#inputs:
#   config: simulator configuration, can be ignored
#   curr: current simulation step 
#   jobs: dictionary of ALL job descriptions as listed in the workload file (by ID)
#   pending: dictionary of job IDs that haven't been scheduled yet. Sorted by Arrival Time
#   free: dictionary of currently available resources indexed by processor family


#output:
#    schedule: proposed job schedule and placement

def schedule(config, curr, jobs, pending, free):
    period = config.getfloat("simulator", "period")
    digits = config.getint("simulator", "digits")
    compose = config.getfloat("composition", "time")
    downscale = config.getboolean("scheduler", "backscale")

    schedule = {}

######################
# START EDITING HERE
######################


# visiting_jobs [[u'1387', 8], [u'1373', 16]]
# visiting_jids [u'1387', u'1373']

    visiting_jobs = [] # array of jobid,num_requested_sockets
    visiting_jids = [] # array of jobid only

    if len(pending) == 0:
        return schedule


    #VISITNG NODES IN RANDOM ORDER
    random.seed(12345)
    visiting_indexes = random.sample(range(len(pending)), len(pending))

    for index in visiting_indexes:
        visiting_jobs.append([pending[index],jobs[pending[index]]["tasks"]])

    for job in visiting_jobs:
        visiting_jids.append(job[0])

    #print 'pending',pending
    #print 'visiting_jobs',visiting_jobs
    #print 'visiting_jids',visiting_jids

    for jid in visiting_jids:
        job = jobs[jid]
        family = list(free.keys())[0]
        num_sockets = job["tasks"]
        num_nodes = 1 if job["scale"] == "up" else num_sockets
        node_size = int(num_sockets / num_nodes)
        assert num_sockets % num_nodes == 0, "This was not expected! nodesize=%s".format(node_size)
        time = job["time"]
        downscaled = False

        ## 1. TRY TO PLACE ALL TASKS
        alloc = resource_selection_composition_and_placement(config, free, family, num_nodes, node_size)
        if alloc == None and not downscale:
            break

        ## IF NOT ALL TASKS CAN BE PLACED,
        ## 2. TRY TO PLACE AT LEAST AS MANY TASKS AS POSSIBLE (DOWNSCALE THE JOB) IF THE JOB
        ## is scaleout (expected to scale across nodes, as opposed to scale up - SMP designed)
        if alloc == None:
            num_free = len(scorsa.list_free_sockets(free))
            if num_free == 0:
                break
            num_sockets = num_free
            num_nodes = 1 if job["scale"] == "up" else num_sockets
            node_size = int(num_sockets / num_nodes)
            assert num_sockets % num_nodes == 0, "This was not expected! nodesize=%s".format(node_size)
            time = time * (1 / (float(num_sockets) / job["tasks"]))
            alloc = resource_selection_composition_and_placement(config, free, family, num_nodes, node_size)
            downscaled = True

        recomposed, nodes = alloc
        if recomposed:
            time = time + compose


######################
# If the job can't be placed, you should break before this point
######################

        schedule[jid] = {}
        schedule[jid]["family"] = family
        schedule[jid]["nodes"] = nodes
        schedule[jid]["start"] = curr
        schedule[jid]["end"] = curr + scorsa.step(time, period, digits)
        schedule[jid]["reused"] = not recomposed
        schedule[jid]["backscaled"] = downscaled

    for jid in list(schedule.keys()):
        pending.remove(jid)

    return schedule
