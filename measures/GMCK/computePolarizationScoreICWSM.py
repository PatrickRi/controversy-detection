# script to compute the polarization score proposed in http://homepages.dcc.ufmg.br/~pcalais/papers/icwsm13-pcalais.pdf
# ICWSM 2013

# first run metis to compute the cut.

import sys
import networkx as nx
import numpy as np

#filename = sys.argv[1]
#file2 = sys.argv[2]
file2 = "polblogs"

#G = nx.read_weighted_edgelist(filename, delimiter=",")
G = nx.read_gml("../../polblogs.gml", label='id')

f1 = open("../../polblogs_left.txt")
# f1 = open("../communities_follow_networks/community1_" + file2 + ".txt")
lines1 = f1.readlines()
dict_left = {}

for line in lines1:
    line = int(line.strip())
    dict_left[line] = 1

f2 = open("../../polblogs_right.txt")
# f2 = open("../communities_follow_networks/community2_" + file2 + ".txt")
lines2 = f2.readlines()
dict_right = {}

for line in lines2:
    line = int(line.strip())
    dict_right[line] = 1

cut_nodes1 = {}
cut_nodes = {}

for i in range(len(lines1)):
    name1 = int(lines1[i].strip())
    for j in range(len(lines2)):
        name2 = int(lines2[j].strip())
        if G.has_edge(name1, name2):
            cut_nodes1[name1] = 1
            cut_nodes1[name2] = 1

dict_across = {}  # num. edges across the cut
dict_internal = {}  # num. edges internal to the cut


def satisfyCondition2(node1):  # A node v \in G_i has at least one edge connecting to a member of G_i which is not connected to G_j.
    neighbors = G.neighbors(node1)
    for n in neighbors:
        if node1 in dict_left and n in dict_right:  # only consider neighbors belonging to G_i
            continue
        if node1 in dict_right and n in dict_left:  # only consider neighbors belonging to G_i
            continue
        if n not in cut_nodes1:
            return True
    return False


# remove nodes from the cut that dont satisfy condition 2 - check for condition2 in the paper http://homepages.dcc.ufmg.br/~pcalais/papers/icwsm13-pcalais.pdf page 5,
for keys in list(cut_nodes1.keys()):
    if satisfyCondition2(keys):
        cut_nodes[keys] = 1

for edge in G.edges():
    #	print edge
    node1 = edge[0]
    node2 = edge[1]
    if node1 not in cut_nodes and (node2 not in cut_nodes):  # only consider edges involved in the cut
        continue
    if (node1 in cut_nodes and node2 in cut_nodes):  # if both nodes are on the cut and both are on the same side, ignore
        if node1 in dict_left and node2 in dict_left:
            continue
        if (node1 in dict_right and node2 in dict_right):
            continue
    if node1 in cut_nodes:
        if node1 in dict_left:
            if (node2 in dict_left and node2 not in cut_nodes1):
                if node1 in dict_internal:
                    dict_internal[node1] += 1
                else:
                    dict_internal[node1] = 1
            elif (node2 in dict_right and node2 in cut_nodes):
                if node1 in dict_across:
                    dict_across[node1] += 1
                else:
                    dict_across[node1] = 1
        elif node1 in dict_right:
            if (node2 in dict_left and node2 in cut_nodes):
                if node1 in dict_across:
                    dict_across[node1] += 1
                else:
                    dict_across[node1] = 1
            elif (node2 in dict_right and node2 not in cut_nodes1):
                if node1 in dict_internal:
                    dict_internal[node1] += 1
                else:
                    dict_internal[node1] = 1
    if node2 in cut_nodes:
        if node2 in dict_left:
            if (node1 in dict_left and node1 not in cut_nodes1):
                if node2 in dict_internal:
                    dict_internal[node2] += 1
                else:
                    dict_internal[node2] = 1
            elif (node1 in dict_right and node1 in cut_nodes):
                if node2 in dict_across:
                    dict_across[node2] += 1
                else:
                    dict_across[node2] = 1
        elif node2 in dict_right:
            if (node1 in dict_left and node1 in cut_nodes):
                if node2 in dict_across:
                    dict_across[node2] += 1
                else:
                    dict_across[node2] = 1
            elif (node1 in dict_right and node1 not in cut_nodes1):
                if node2 in dict_internal:
                    dict_internal[node2] += 1
                else:
                    dict_internal[node2] = 1

            # print dict_internal
# print dict_across

polarization_score = 0.0
lis1 = []
for keys in list(cut_nodes.keys()):
    if (keys not in dict_internal or (keys not in dict_across)):  # for singleton nodes from the cut
        continue
    if (dict_across[keys] == 0 and dict_internal[keys] == 0):  # theres some problem
        print("wtf")
    #	print dict_internal[keys],dict_across[keys],(dict_internal[keys]*1.0/(dict_internal[keys] + dict_across[keys]) - 0.5),G.degree(keys)
    polarization_score += (dict_internal[keys] * 1.0 / (dict_internal[keys] + dict_across[keys]) - 0.5)
#	if(polarization_score==0.0):
#		continue
#	lis1.append(polarization_score)

polarization_score = polarization_score / len(list(cut_nodes.keys()))
print(("********************" + file2 + "*********************"))
print((polarization_score, "\n"))
# print np.mean(np.asarray(lis1)), np.median(np.asarray(lis1))
