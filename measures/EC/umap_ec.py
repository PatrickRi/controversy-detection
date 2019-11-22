from typing import Dict, List

import networkx as nx
import umap


def umap_ec(g: nx.Graph, s) -> Dict[int, List[float]]:
    reducer = umap.UMAP()
    embedding = reducer.fit_transform(nx.to_numpy_array(g), s)
    return dict(zip(g.nodes(), embedding))
