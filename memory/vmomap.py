#!/usr/bin/env python
#
# Copyright 2017 The Fuchsia Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Visualizes the VMO/process graph from Magenta's "memgraph" tool.

Run "vmomap.py --help" for a list of arguments.

For usage, see magenta/docs/memory.md
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import sys


class DirectedEdge(object):
    """A generic directed edge in a directed graph."""

    def __init__(self, head, tail):
        """Creates a directed edge from the head to the tail.

        Args:
            head: the DagNode at the head (origin) of the edge
            tail: the DagNode at the tail (destination) of the edge
        """
        self.head = head
        self.tail = tail


class DirectedNode(object):
    """A generic node in a directed graph."""

    def __init__(self, name, area=0):
        """Creates a named node.

        Args:
            name: human-readable name of the node
            area: a numeric size for the node; typically maps to memory size
        """
        #xxx unique id? or our parent container has it as a key?
        #DirectedGraph.AddNode(id, name, area)
        self.name = name
        self.area = area
        self.edges_in = []  #xxx set?
        self.edges_out = []  #xxx set?
        self.labels = set() # strings


def build_vmo_proc_graph(dataset):
    for record in dataset:
        record_type = record['type']
        if record_type != 'p':
            continue


def main():
    dataset = json.load(sys.stdin)
    # we only care about vmos and processes, but jobs help group
    # can label each node with the spheres it's in (job-job-process)
    # no nodes for jobs per se, unless we want the name
    # ignore jobs at first

    # start with clusters of vmos that have the same set of processes
    # pointing to them.
    # Ignore handle vs. mapping at first, though could add that to
    # the process label on the vmo

    # process node, vmo node
    # edge labels on vmos; backlinks on processes
    #  edges have via (mapping, handle+rights)

    # also have clone tree
    #  parent/child edges
    # ignore this at first, too


if __name__ == '__main__':
    main()
