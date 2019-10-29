from fa2 import ForceAtlas2
import networkx as nx
from typing import Dict, List


# maybe play around with some parameters (defaults yield results similar to Gephi)
def force_atlas_fa2(g: nx.Graph, iterations: int) -> Dict[int, List[float]]:
    forceatlas2 = ForceAtlas2(
        # Behavior alternatives
        outboundAttractionDistribution=True,  # Dissuade hubs
        linLogMode=False,  # NOT IMPLEMENTED
        adjustSizes=False,  # Prevent overlap (NOT IMPLEMENTED)
        edgeWeightInfluence=1.0,

        # Performance
        jitterTolerance=1.0,  # Tolerance
        barnesHutOptimize=True,
        barnesHutTheta=1.2,
        multiThreaded=False,  # NOT IMPLEMENTED

        # Tuning
        scalingRatio=2.0,
        strongGravityMode=False,
        gravity=1.0,

        # Log
        verbose=True)

    return forceatlas2.forceatlas2_networkx_layout(g, pos=None, iterations=iterations)
