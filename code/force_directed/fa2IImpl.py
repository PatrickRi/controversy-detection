#! /usr/bin/python

import networkx as nx

from scipy.sparse import spdiags, coo_matrix
import scipy as sp
import numpy as np

import matplotlib.pyplot as plt
import sys
import networkx as nx
from fa2l import force_atlas2_layout
import matplotlib.pyplot as plt


if __name__ == "__main__":
    ## Read a food web with > 100 nodes
    #    FW = nx.read_edgelist('web.edges', create_using=nx.DiGraph())
    filename = "../../polblogs.gml"
    file2 = "polblogs"
    G2 = nx.read_gml("../../polblogs.gml", label='id')
    FW = nx.Graph(G2)
    #FW = nx.read_weighted_edgelist(filename, create_using=nx.Graph(), delimiter=",")
    positions = force_atlas2_layout(FW,
                                    iterations=100,
                                    pos_list=None,
                                    node_masses=None,
                                    outbound_attraction_distribution=False,
                                    lin_log_mode=False,
                                    prevent_overlapping=False,
                                    edge_weight_influence=1.0,

                                    jitter_tolerance=1.0,
                                    barnes_hut_optimize=True,
                                    barnes_hut_theta=0.5,

                                    scaling_ratio=2.0,
                                    strong_gravity_mode=False,
                                    gravity=1.0)

    #positions = forceatlas2_layout(FW, linlog=False, nohubs=False, iterations=1000)
    #	out = open(file2 + "_positions.txt","w");
    out = open(file2 + "_positions_fai.txt", "w")
    #    print positions
    for keys in positions.keys():
        out.write(str(keys) + "\t" + str(positions[keys][0]) + "," + str(positions[keys][1]) + "\n")
#    nx.draw(FW, positions)
#    plt.show()
