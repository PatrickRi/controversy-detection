import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import seaborn as sns

df = pd.read_csv('keyword_used_count.csv', names=['keyword', 'cnt'])
sns.lineplot(x="keyword", y="cnt",
             data=df)