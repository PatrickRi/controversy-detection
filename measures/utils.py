from typing import Tuple, Dict
import yaml

import networkx as nx


# Nodes have arbitrary names, which might be difficult later on, 0:n is much simpler, but dictionary might be needed
def normalize_graph(G: nx.Graph) -> Tuple[nx.Graph, Dict]:
    dict = {}
    G_new = nx.to_networkx_graph(nx.adjacency_matrix(G).todense())
    for i, node in enumerate(G.nodes()):
        dict[i] = node
    return G_new, dict


def adjacency_matrix(G: nx.Graph):
    return nx.adjacency_matrix(G).todense()


def get_config(config_path: str, overwrites: str = None) -> Dict[str, any]:
    with open(config_path, 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

    if overwrites is not None and overwrites != "":
        over_parts = [yaml.load(x) for x in overwrites.split(",")]

        for d in over_parts:
            for key, value in d.items():
                cfg[key] = value

    return cfg
