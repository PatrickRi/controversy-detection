# script to generate the dataset required to run the code for the venezuela polarization score, present at ./external_datasets/Twitter_data_venezuela/OpinionModel.py
# this script gets the top k% users with highest degree (influential seed users) on both sides. this is required to run the polarization score code above.

# output will be a gml file, where each node will have an id (integer), label (twitter screename), ideo (ideology score, -1 for top community2, 1 for top community1, and 0 otherwise).

import networkx as nx
import random, numpy, sys
from operator import itemgetter

#filename = sys.argv[1]
#file2 = sys.argv[2]


def convertIntoDirected(G):
    for edge in G.edges():
        node1 = edge[0]
        node2 = edge[1]
        G.add_edge(node2, node1)
    return G

G = nx.read_gml("../../polblogs.gml", label='id')
#G = nx.read_weighted_edgelist(filename, delimiter=',', create_using=nx.DiGraph())

G = convertIntoDirected(G)
seed_nodes_num = int(len(G.nodes()) * 0.05)  # seed nodes percenatage = 5 percent
# seed_nodes_num = 1
print("selecting ", seed_nodes_num, " seed nodes from each side")

f1 = open("../../polblogs_left.txt")
# f1 = open("communities_follower_network/community1_" + file2 + ".txt")
lines1 = f1.readlines()
left = []
dict_left = {}

for line in lines1:
    line = int(line.strip())
    left.append(line)
    dict_left[line] = 1

f2 = open("../../polblogs_right.txt")
# f2 = open("communities_follower_network/community2_" + file2 + ".txt")
lines2 = f2.readlines()
right = []
dict_right = {}

for line in lines2:
    line = int(line.strip())
    right.append(line)
    dict_right[line] = 1


def getNodesFromLabelsWithHighestDegree(G, k, flag):  # first take the nodes with the highest degree according to the "flag" and then take the top $k$
    random_nodes = {}
    dict_degrees = {}
    for node in G.nodes():
        dict_degrees[node] = G.degree(node)
    sorted_dict = sorted(list(dict_degrees.items()), key=itemgetter(1), reverse=True)  # sorts nodes by degrees
    #	sorted_dict = sorted_dict[:k]
    if flag == "left":
        count = 0
        for i in sorted_dict:
            if count > k:
                break
            if i[0] not in dict_left:
                continue
            random_nodes[i[0]] = i[1]
            count += 1
    elif flag == "right":
        count = 0
        for i in sorted_dict:
            if count > k:
                break
            if i[0] not in dict_right:
                continue
            random_nodes[i[0]] = i[1]
            count += 1
    else:
        count = 0
        for i in sorted_dict:
            if count > k / 2:
                break
            if i[0] not in dict_left:
                continue
            random_nodes[i[0]] = i[1]
            count += 1
        count = 0
        for i in sorted_dict:
            if count > k / 2:
                break
            if i[0] not in dict_right:
                continue
            random_nodes[i[0]] = i[1]
            count += 1

    return random_nodes


left_seed_nodes = getNodesFromLabelsWithHighestDegree(G, seed_nodes_num, 'left')
right_seed_nodes = getNodesFromLabelsWithHighestDegree(G, seed_nodes_num, 'right')

dict_ids = {}
dict_ideos = {}

count = 0
for node in G.nodes():
    dict_ids[node] = count
    count += 1
    if node in left_seed_nodes:
        dict_ideos[node] = 1
    elif node in right_seed_nodes:
        dict_ideos[node] = -1
    else:
        dict_ideos[node] = 0

for node in G.nodes():
    node_id = dict_ids[node]
    node_ideo = dict_ideos[node]
    G.add_node(node, ideo=node_ideo)

nx.write_gml(G, 'polblogs.gml')
# nx.write_gml(G,'gml_files/follower_network/' + file2 + '.gml')
