import pytest
import networkx as nx
from measures.utils import normalize_graph
from numpy.testing import assert_array_equal


def test_normalize():
    g = nx.Graph()
    g.add_edge("1", 2)
    g.add_edge("4", "5")
    g.add_edge("1", "3")
    g.add_edge(2, "5")
    g.add_edge("3", "4")
    new_graph, node_mapping = normalize_graph(g)
    assert_array_equal(nx.adjacency_matrix(g).todense(), nx.adjacency_matrix(new_graph).todense())
    assert node_mapping == {0: "1", 1: 2, 2: "4", 3: "5", 4: "3"}
