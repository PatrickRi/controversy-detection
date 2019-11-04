import networkx as nx
from typing import Dict
from operator import itemgetter


# first take the nodes with the highest degree, then take the top $k$
def get_nodes_with_highest_degree(g: nx.Graph, k: int, partition: Dict[int, int]):
    random_nodes = {}
    dict_degrees = {}
    for node in g.nodes():
        dict_degrees[node] = g.degree[node]
    sorted_dict = sorted(dict_degrees.items(), key=itemgetter(1), reverse=True)  # sorts nodes by degrees
    count = 0
    for i in sorted_dict:
        if count > k:
            break
        if i[0] not in partition:
            continue
        random_nodes[i[0]] = i[1]
        count += 1
    return random_nodes
