import glob

import pandas as pd

df_merged = pd.DataFrame(columns=['idx', 'dataset', 'measure', 'result', 'duration'])
for file in glob.glob('output*.csv'):
    df = pd.read_csv(file, sep=',')
    df_merged = df_merged.append(df)
df_merged = df_merged[['dataset', 'measure', 'result', 'duration']]
df_merged.index.name = 'idx'
df_merged.to_csv('merged_results_umap.csv')
