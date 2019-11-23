from typing import Dict, List

import networkx as nx
import umap


def umap_ec(g: nx.Graph, s) -> Dict[int, List[float]]:
    reducer = umap.UMAP()
    # using the partitioning vector as target, leads to extreme results (information leak)
    #embedding = reducer.fit_transform(nx.to_numpy_array(g), s)
    embedding = reducer.fit_transform(nx.to_numpy_array(g))
    return dict(zip(g.nodes(), embedding))
