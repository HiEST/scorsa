#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# gen-layout -- Generate a layout file
#
# Given a number of sockets, racks, drawers per rack, and sockets per sled,
# generate a layout of a Rack Scale system to use as part of scorsa's
# simulator. A layout file is basically a CSV file containing the location of
# sockets in the system. Each socket is identified by a unique integer ID.
# Sleds can be denoted as a set of sockets separated by «+». Drawers are
# denoted by rows containing «--», while racks are columns separated by «|».
# This generator is limited in that it doesn't generate multi-line drawers.
#
# Copyright © 2016 Jordà Polo <jorda.polo@bsc.es>

import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-n", dest="n", required=True, help="Number of sockets")
ap.add_argument("-r", dest="r", required=True, help="Number of racks")
ap.add_argument("-d", dest="d", required=True, help="Number of drawers/rack")
ap.add_argument("-s", dest="s", required=True, help="Number of sockets/sled")
args = ap.parse_args()

n = int(args.n)
r = int(args.r)
dpr = int(args.d)     # drawers per rack
sps = int(args.s)     # sockets per sled
npr = n / r           # nodes per rack
spd = npr / dpr / sps # sleds per drawer

# Ensure socket ID length is at least 2, so as to support empty slots, which
# are marked as "-1".
id_len = max(len(str(n)), 2)
separator = "-" * (id_len * sps + sps - 1)

for i in range(dpr):
    row = ""
    for j in range(r):
        sleds = []
        for k in range(spd):
            base = (i * spd * sps) + (j * npr) + (k * sps)
            sled = [str(sid).zfill(id_len) for sid in range(base, base + sps)]
            sleds.append("+".join(sled))
        row += ",".join(sleds)
        if j + 1 < r:
            row += ",|,"

    print(row)

    if i + 1 == dpr:
        break

    row = ""
    for j in range(r):
        row += ",".join([separator for k in range(spd)])
        if j + 1 < r:
            row += ",|,"

    print(row)
