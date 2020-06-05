import pandas as pd
import os
import numpy as np
pd.set_option('display.max_colwidth', -1)
pd.set_option('display.max_columns', None)


txtfile = open("results_postings_min_2_weight.txt")
lines = txtfile.readlines()
data = []
for line in lines:
    line = line.strip()
    elements = line.split("  ")
    if len(elements) > 3:
        data.append(elements)

df = pd.DataFrame(data=data, columns=['docid', 'mean', 'measure', 'result'])
df["result"] = pd.to_numeric(df["result"])
print(df[['measure', 'result']].groupby(['measure']).describe())

