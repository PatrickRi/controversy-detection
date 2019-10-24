from .partition import Partition
from .metis import MetisPartitioner


def get_partitioner(method: str) -> Partition:
    if method == "metis":
        return MetisPartitioner()
    else:
        raise Exception("Method " + method + " not supported yet")
