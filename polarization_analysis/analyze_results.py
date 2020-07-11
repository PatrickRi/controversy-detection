import glob
import os

import pandas as pd

from measures.utils import get_logger

pd.set_option('display.max_colwidth', -1)
pd.set_option('display.max_columns', None)

logger = get_logger('main')
posting_dirs = glob.glob('./cache/postings*')
df_all = pd.DataFrame(
    columns=['measure', 'result', 'title', 'removed_edges', 'ratio_edges_removed', 'largest_cc', 'ratio_largest_cc',
             'experiment'])
for posting_dir in posting_dirs:
    articles = glob.glob(os.path.join('.', posting_dir, '*'))
    experiment = posting_dir.split(os.sep)[-1]
    for article in articles:
        doc_id = article.split(os.sep)[-1]
        # gml_path = glob.glob(os.path.join('.', article, '*.gml'))[0]
        # graph = nx.read_gml(gml_path, label='id')
        statistics_path = glob.glob(os.path.join('.', article, '*statistics.csv'))[0]
        df_statistics = pd.read_csv(statistics_path,
                                    names=['removed_edges', 'ratio_edges_removed', 'largest_cc', 'ratio_largest_cc'],
                                    header=0)
        scores_path = glob.glob(os.path.join('.', article, 'scores_*.csv'))[0]
        df_scores = pd.read_csv(scores_path,
                                names=['idx', 'measure', 'result'], header=0)
        df_scores = df_scores.drop(columns=['idx'])

        doc_title = glob.glob(os.path.join('.', article, '*.txt'))[0].split(os.sep)[-1].split('.txt')[0]
        df_scores['title'] = doc_title
        df_scores['removed_edges'] = df_statistics.iloc[0]['removed_edges']
        df_scores['ratio_edges_removed'] = df_statistics.iloc[0]['ratio_edges_removed']
        df_scores['largest_cc'] = df_statistics.iloc[0]['largest_cc']
        df_scores['ratio_largest_cc'] = df_statistics.iloc[0]['ratio_largest_cc']
        df_scores['experiment'] = experiment
        df_all = pd.concat([df_all, df_scores])
