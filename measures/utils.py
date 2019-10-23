from typing import Tuple, Dict

import networkx as nx

# Nodes have arbitrary names, which might be difficult later on, 0:n is much simpler, but dictionary might be needed
def normalize_graph(G: nx.Graph) -> Tuple[nx.Graph, Dict] :
    dict = {}
    G_new = nx.to_networkx_graph(nx.adjacency_matrix(G).todense())
    for i, node in enumerate(G.nodes()):
        dict[i] = node
    return G_new, dict


def adjacency_matrix(G: nx.Graph):
    return nx.adjacency_matrix(G).todense()
