import numpy as np
from numpy import diag
import numpy.random as rand
from numpy.linalg import norm, inv

from numpy.linalg import norm
def preprocessArgs(s, max_rounds):
    '''Argument processing common for most models.
    Returns:
        N, z, max_rounds
    '''

    N = np.size(s)
    max_rounds = int(max_rounds) + 1  # Round 0 contains the initial opinions
    z = s.copy()

    return N, z, max_rounds

def friedkinJohnsen(A, s, max_rounds, eps=1e-6, plot=False, conv_stop=True,
                    save=False):
    '''Simulates the Friedkin-Johnsen (Kleinberg) Model.
    Runs a maximum of max_rounds rounds of the Friedkin-Jonsen model. If the
    model converges sooner, the function returns. The stubborness matrix of
    the model is extracted from the diagonal of matrix A.
    Args:
        A (NxN numpy array): Adjacency matrix (its diagonal is the stubborness)
        s (1xN numpy array): Initial opinions (intrinsic beliefs) vector
        max_rounds (int): Maximum number of rounds to simulate
        eps (double): Maximum difference between rounds before we assume that
        the model has converged (default: 1e-6)
        plot (bool): Plot preference (default: False)
        conv_stop (bool): Stop the simulation if the model has converged
        (default: True)
        save (bool): Save the simulation data into text files
    Returns:
        A txN vector of the opinions of the nodes over time
    '''

    N, z, max_rounds = preprocessArgs(s, max_rounds)

    B = np.diag(np.diag(A))  # Stubborness matrix of the model
    A_model = A - B  # Adjacency matrix of the model

    opinions = np.zeros((max_rounds, N))
    opinions[0, :] = z

    for t in range(1, max_rounds):
        z = np.dot(A_model, z) + np.dot(B, s)
        z = np.array(z[0, :])[0]
        opinions[t, :] = z
        if conv_stop and \
           norm(opinions[t - 1, :] - opinions[t, :], np.inf) < eps:
            print('Friedkin-Johnsen converged after {t} rounds'.format(t=t))
            break

    return opinions[0:t+1, :]


import networkx as nx
g = nx.Graph()
g.add_edge(1, 2)
g.add_edge(1, 5)
g.add_edge(1, 12)
g.add_edge(1, 9)
g.add_edge(1, 8)
g.add_edge(1, 4)
g.add_edge(1, 6)
g.add_edge(2, 3)
g.add_edge(2, 8)
g.add_edge(2, 7)
g.add_edge(2, 9)
g.add_edge(2, 10)
g.add_edge(3, 4)
g.add_edge(3, 5)
g.add_edge(3, 6)
g.add_edge(3, 7)
g.add_edge(3, 8)
g.add_edge(3, 9)
g.add_edge(3, 10)
g.add_edge(3, 11)
g.add_edge(4, 6)
g.add_edge(4, 7)
g.add_edge(4, 8)
g.add_edge(4, 9)
g.add_edge(4, 10)
g.add_edge(6, 8)
g.add_edge(6, 10)
g.add_edge(6, 14)
g.add_edge(7, 8)
g.add_edge(7, 10)
g.add_edge(8, 9)
g.add_edge(8, 16)
g.add_edge(9, 10)
g.add_edge(10, 13)

g.add_edge(11, 12)
g.add_edge(11, 13)
g.add_edge(11, 16)
g.add_edge(11, 17)
g.add_edge(11, 18)
g.add_edge(11, 19)
g.add_edge(11, 20)
g.add_edge(12, 14)
g.add_edge(12, 16)
g.add_edge(12, 18)
g.add_edge(13, 14)
g.add_edge(13, 16)
g.add_edge(13, 17)
g.add_edge(13, 18)
g.add_edge(13, 19)
g.add_edge(13, 20)
g.add_edge(14, 17)
g.add_edge(14, 18)
g.add_edge(14, 20)
g.add_edge(15, 17)
g.add_edge(15, 18)
g.add_edge(15, 19)
g.add_edge(15, 20)
g.add_edge(16, 17)
g.add_edge(16, 18)
g.add_edge(16, 19)
g.add_edge(16, 20)
g.add_edge(17, 18)
g.add_edge(18, 19)
g.add_edge(19, 20)


s = np.zeros(20)
for i in range(20):
  if i < 10:
    s[i] = -1
  else:
    s[i] = 1
A = nx.adjacency_matrix(g).todense()
opinion_vector = np.copy(s)
adj_dict_cache = {}
for its in range(100):
    prev_opinion_vector = opinion_vector
    for v in range(1, 21):
        sum_on = 0
        for n in g.neighbors(v):
            sum_on = sum_on + prev_opinion_vector[n-1]
        opinion_vector[v-1] = (s[v-1] + sum_on)/(1+len(list(g.neighbors(v))))

print((np.linalg.norm(opinion_vector) ** 2) / 20)