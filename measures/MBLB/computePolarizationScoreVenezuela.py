# script to compute polarization score using the one by the paper from Twitter polarization in Venezuela.
# FIRST RUN generateDataForVenezuelaPolarizationScore.py to GENERATE SEED SETS

import networkx as networkx
import numpy as np
import scipy.sparse as sp
import time, pickle, sys

#file2 = sys.argv[1]


def Model(G, corenode, tol=10 ** -5, save_xi=True):
    # G: Graph to calculate opinions. The nodes have an attribute "ideo" with their ideology, set to 0 for all listeners, 1 and -1 for the elite.
    # corenode: Nodes that belong to the seed (Identifiers from the Graph G)
    # tol is the threshold for convergence. It will evaluate the difference between opinions at time t and t+1
    # save_xi: boolean to save results

    N = len(G.nodes())

    # Build the adjacency matrix
    Aij = sp.lil_matrix((N, N))
    print("Adjacency matrix shape: " + str(Aij.shape))
    for o, d in G.edges():
        Aij[o-1, d-1] = 1
        Aij[d-1, o-1] = 1
    new_corenodes = [x-1 for x in corenode] # needed because indexes start with 0 (for A e.g.), but nodes have ids with 1
    # Build the vectors with users opinions
    v_current = []
    v_new = []
    #dict_nodes = {} # for what are labels needed???
    all_nodes = G.nodes()
    all_nodes.sort()
    for nodo in all_nodes:
        #dict_nodes[G.node[nodo]['label']] = G.node[nodo]['ideo']
        v_current.append(G.node[nodo]['ideo'])
        v_new.append(0.0)

    v_current = 1. * np.array(v_current)
    v_new = 1. * np.array(v_new)
    notconverged = len(v_current)
    times = 0

    # Do as many times as required for convergence
    while notconverged > 0:
        times = times + 1
        print(times)
        t = time.time()

        # for all nodes apart from corenode, calculate opinion as average of neighbors
        for j in np.setdiff1d(list(range(len(v_current))), new_corenodes):
            nodosin = Aij.getrow(j).nonzero()[1]
            if len(nodosin) > 0:
                v_new[j] = np.mean(v_current[nodosin])
            else:
                v_new[j] = v_current[j]
        #            nodos_changed[j]=nodos_changed[j] or (v_new[j]!=v_current[j])

        # update opinion
        for j in new_corenodes:
            v_new[j] = v_current[j]

        diff = np.abs(v_current - v_new)
        notconverged = len(diff[diff > tol])
        v_current = v_new.copy()
    return v_current


def GetPolarizationIndex(ideos):
    # Input: Vector with individuals Xi
    # Output: Polarization index, Area Difference, Normalized Pole Distance
    D = []  # POLE DISTANCE
    AP = []  # POSSITIVE AREA
    AN = []  # NEGATIVE AREA
    cgp = []  # POSSITIVE GRAVITY CENTER
    cgn = []  # NEGATIVE GRAVITY CENTER

    ideos.sort()
    hist, edg = np.histogram(ideos, np.linspace(-1, 1.1, 50))
    edg = edg[:len(edg) - 1]
    AP = sum(hist[edg > 0])
    AN = sum(hist[edg < 0])
    AP0 = 1. * AP / (AP + AN)
    AN0 = 1. * AN / (AP + AN)
    cgp = sum(hist[edg > 0] * edg[edg > 0]) / sum(hist[edg > 0])
    cgn = sum(hist[edg < 0] * edg[edg < 0]) / sum(hist[edg < 0])
    D = cgp - cgn
    p1 = 0.5 * D * (1. - 1. * abs(AP0 - AN0))  # polarization index
    DA = 1. * abs(AP0 - AN0) / (AP0 + AN0)  # Areas Difference
    D = 0.5 * D  # Normalized Pole Distance
    return p1, DA, D, (1-DA)*D, abs((AP-AN)/(AP+AN)), (1-abs((AP-AN)/(AP+AN)))*D


# G = networkx.read_gml("external_datasets/Twitter_data_venezuela/data_files_gml/r_chavez_4.gml")
# G = networkx.read_gml("gml_files/" + file2 + ".gml")
#G = networkx.read_gml("gml_files/follower_network/" + file2 + ".gml")
G = networkx.read_gml("karate.gml")

ideos = networkx.get_node_attributes(G, 'ideo')

corenode = []

for key in list(ideos.keys()):
    if (ideos[key] == 1 or ideos[key] == -1):
        corenode.append(key)

v_current = Model(G, corenode)

# v_current = pickle.load(open("results_name", "rb"))
print(GetPolarizationIndex(v_current))
