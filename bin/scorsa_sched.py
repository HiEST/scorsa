#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# scorsa-sched -- Simulate the execution of a workload
#
# Given a system configuration and layout, and a workload description,
# simulate the execution of all the jobs in the workload generating a schedule
# that includes when and where the jobs are executed, along with additional
# stats such as fragmentation.
#
# Copyright © 2016 Jordà Polo <jorda.polo@bsc.es>


import logging
import argparse
import configparser
import json
import numpy as np

from collections import defaultdict

import scorsa
import policies


def free_nodes(free, family, nodes):
    for node in nodes:
        free[family][len(node)].append(node)


def main(args):

    logging.basicConfig(format="%(message)s", level=logging.ERROR)
    config = configparser.ConfigParser(delimiters=("="))
    config.read(args.c)

    length = config.getfloat("simulator", "length")
    period = config.getfloat("simulator", "period")
    digits = config.getint("simulator", "digits")
    families = json.loads(config.get("system", "families"))

    layout = scorsa.map_layout(np.genfromtxt(
        args.l, delimiter=',', dtype=str, encoding=None))
    max_dist = scorsa.distance(layout, 0, len(layout) - 1)

    with open(args.w) as w:
        workload = json.load(w)

    jobs = {job["id"]: job for job in workload}

    arrivals = defaultdict(list)  # job IDs indexed by arrival time
    completions = defaultdict(list)  # job IDs indexed by completion time

    schedule = {}  # scheduling decisions indexed by job ID
    stats = []
    internal_stats = []

    running = []  # current job IDs being executed
    pending = []  # current submitted job IDs that haven't been scheduled yet
    free = {}  # current available resources indexed by family

    for f in families:
        r = json.loads(config.get("system.%s" % f, "range"))
        free[f] = defaultdict(list)
        free[f][1] = [[n] for n in range(r[0], r[1])]

    for jid, job in jobs.items():
        i = scorsa.step(float(job["arrival"]), period, digits)
        arrivals[i].append(jid)

    for i in scorsa.steps(0.0, length, period, digits):
        if i in completions:
            #  release resources for jobs that complete in this step
            for jid in completions[i]:
                family = schedule[jid]["family"]
                nodes = schedule[jid]["nodes"]
                free_nodes(free, family, nodes)
                running.remove(jid)

        if i in arrivals:
            pending = pending + arrivals[i]

        new = policies.schedule(config, i, jobs, pending, free)

        for jid, sched in new.items():
            running.append(jid)
            completions[sched["end"]].append(jid)

        schedule.update(new)

        # measure fragmentation of free slots, and for each running job,
        # normalized by number of sockets
        sockets = scorsa.list_free_sockets(free)
        f = scorsa.fragmentation(layout, sockets) * len(sockets) / len(layout)
        r = d = b = 0.0
        for jid in running:
            sockets = scorsa.list_sockets(schedule[jid]["nodes"])
            job_dist = scorsa.distance(layout, min(sockets), max(sockets))
            min_dist = scorsa.distance(layout, 0, len(sockets) - 1)
            ratio = len(sockets) / len(layout)
            f += scorsa.fragmentation(layout, sockets) * \
                len(sockets) / len(layout)
            d += job_dist - min_dist
            r += ratio if schedule[jid]["reused"] else 0.0
            b += ratio if schedule[jid]["backscaled"] else 0.0
        d = d / len(running) / max_dist if len(running) > 0 else d

        stats.append({"time": i, "frag": f, "dist": d,
                      "reuse": r, "backscale": b})
        internal_stats.append([f, d])

    metrics = {}
    x = 0  #  fragmentation
    metrics = {
        "fragmentation": {
            "mean": np.mean(internal_stats, axis=0)[x],
            "stdev": np.std(internal_stats, axis=0)[x],
            "max": np.max(internal_stats, axis=0)[x],
            "90th": np.percentile(internal_stats, axis=0, q=90)[x],
            "95th": np.percentile(internal_stats, axis=0, q=95)[x],
            "99th": np.percentile(internal_stats, axis=0, q=99)[x],
            "#records": len(internal_stats),
            "totaltime": stats[len(stats)-1]["time"]
        }
    }
    x = 1  #  distance
    metrics.update({
        "distance": {
            "mean": np.mean(internal_stats, axis=0)[x],
            "stdev": np.std(internal_stats, axis=0)[x],
            "max": np.max(internal_stats, axis=0)[x],
            "90th": np.percentile(internal_stats, axis=0, q=90)[x],
            "95th": np.percentile(internal_stats, axis=0, q=95)[x],
            "99th": np.percentile(internal_stats, axis=0, q=99)[x],
            "#records": len(internal_stats),
            "totaltime": stats[len(stats)-1]["time"]
        }
    })
    print(json.dumps(metrics, indent=4, sort_keys=True))

    with open("metrics.json", "w") as out:
        json.dump(metrics, out)

    with open("schedule.json", "w") as out:
        json.dump(schedule, out)

    with open("stats.json", "w") as out:
        json.dump(stats, out)

    print("Files 'metrics.json', schedule.json' and 'stats.json' generated.")

    print(
        "\nRemember to submit the file 'metrics.json' to "
        "http://bscdc-login.bsc.es:7777 before the end "
        "of the lecture! Multiple submissions are accepted.\n"
    )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--config", dest="c", required=True,
                    help="System configuration file")
    ap.add_argument("-l", "--layout", dest="l", required=True,
                    help="System layout file")
    ap.add_argument("-w", "--workload", dest="w", required=True,
                    help="JSON workload file")
    args = ap.parse_args()
    main(args)
