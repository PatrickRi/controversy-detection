from typing import Dict, List

import networkx as nx
import umap


def umap_ec(g: nx.Graph, s, n_neighbors, metric) -> Dict[int, List[float]]:
    reducer = umap.UMAP(n_neighbors=n_neighbors, metric=metric)
    # using the partitioning vector as target, leads to extreme results (information leak)
    #embedding = reducer.fit_transform(nx.to_numpy_array(g), s)
    embedding = reducer.fit_transform(nx.to_numpy_array(g))
    del reducer
    return dict(zip(g.nodes(), embedding))
