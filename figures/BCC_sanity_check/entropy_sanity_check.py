import numpy as np
from numpy import asarray
from scipy.stats import entropy
from scipy.special import rel_entr
from sklearn.neighbors import KernelDensity
import math

def entropy_clone(pk, qk):
    pk = asarray(pk)
    pk = 1.0 * pk / np.sum(pk, axis=0)
    qk = asarray(qk)
    if len(qk) != len(pk):
        raise ValueError("qk and pk must have same length.")
    qk = 1.0 * qk / np.sum(qk, axis=0)
    vec = rel_entr(pk, qk)
    S = np.sum(vec, axis=0)
    return S

def entropy_woscaling(pk, qk):
    pk = asarray(pk)
    qk = asarray(qk)
    if len(qk) != len(pk):
        raise ValueError("qk and pk must have same length.")
    vec = rel_entr(pk, qk)
    S = np.sum(vec, axis=0)
    return S

def kl_divergence(p, q):
    return sum(p[i] * math.log(p[i]/q[i]) for i in range(len(p)))

def replace_with_small(arr):
    result = []
    for x in arr:
        if x < 0.000000001:
            result.append(0.000000001)
        else:
            result.append(x)
    return result

def score(entr):
    return 1 - np.exp(-1.0 * entr)

def ff(n):
    return '{:.8f}'.format(n)

def sample_from_kde(values: np.ndarray):
    kde_fitted = KernelDensity(bandwidth=0.0000001).fit(values.reshape(-1, 1))
    return kde_fitted.sample(10000)

def flat_arr(arr):
    res = []
    for i in arr:
        res.append(i[0])
    return np.array(res)

def experiment(name1, name2, kde=False):
    print(name1, ("KDE" if kde else ""))
    eb_list_all = np.loadtxt(name1, dtype=float)
    eb_list = np.loadtxt(name2, dtype=float)

    entr_arr = np.zeros(100)
    entr_clone_arr = np.zeros(100)
    entr_woscal_arr = np.zeros(100)
    kl_div_arr = np.zeros(100)
    for i in range(100):
        if kde:
            rd_list = np.array(replace_with_small(flat_arr(sample_from_kde(np.array(eb_list)))))
            rd_list_all = np.array(replace_with_small(flat_arr(sample_from_kde(np.array(eb_list_all)))))
        else:
            rd_list = replace_with_small(eb_list[np.random.choice(len(eb_list), size=10000, replace=True)])
            rd_list_all = replace_with_small(eb_list_all[np.random.choice(len(eb_list_all), size=10000, replace=True)])
        entr_arr[i] = entropy(rd_list_all, rd_list)
        entr_clone_arr[i] = entropy_clone(rd_list_all, rd_list)
        entr_woscal_arr[i] = entropy_woscaling(rd_list_all, rd_list)
        kl_div_arr[i] = kl_divergence(rd_list_all, rd_list)
    print("all mean|std:   ", ff(np.mean(eb_list_all)), ":", ff(np.std(eb_list_all)))
    print("rd-all mean|std:", ff(np.mean(rd_list_all)), ":", ff(np.std(rd_list_all)))
    print("cut mean|std:   ", ff(np.mean(eb_list)), ":", ff(np.std(eb_list)))
    print("rd-cut mean|std:", ff(np.mean(rd_list)), ":", ff(np.std(rd_list)))
    print("ent em|es|sm|ss: ", ff(np.mean(entr_arr)), ":", ff(np.std(entr_arr)), ":", ff(np.mean([score(x) for x in entr_arr])), ":", ff(np.std([score(x) for x in entr_arr])))
    # print(np.mean(entr_clone_arr), ":", np.std(entr_clone_arr), ":", score(entr_clone_arr[0])) < same as scipy.entropy
    # print(np.mean(entr_woscal_arr), ":", np.std(entr_woscal_arr), ":", score(entr_woscal_arr[0])) < same as kl_div
    ###print(ff(np.mean(kl_div_arr)), ":", ff(np.std(kl_div_arr)), ":", ff(np.mean([score(x) for x in kl_div_arr])), ":", ff(np.std([score(x) for x in kl_div_arr])))
    print("")

#experiment('s_eb_list_all.txt', 's_eb_list.txt')
#experiment('s_eb_list_all.txt', 's_eb_list.txt', True)
experiment('brazsoc_eb_list_all.txt', 'brazsoc_eb_list.txt')
experiment('brazsoc_eb_list_all.txt', 'brazsoc_eb_list.txt', True)
experiment('cc_eb_list_all.txt', 'cc_eb_list.txt')
experiment('cc_eb_list_all.txt', 'cc_eb_list.txt', True)
experiment('karate_eb_list_all.txt', 'karate_eb_list.txt')
experiment('karate_eb_list_all.txt', 'karate_eb_list.txt', True)