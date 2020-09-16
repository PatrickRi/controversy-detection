import numpy as np
import pandas as pd

from measures.utils import get_logger

pd.set_option('display.max_colwidth', -1)
pd.set_option('display.max_columns', None)


def create():
    df_gc = pd.read_csv('new_merged_votes_and_postings.csv', sep=';', decimal=',')
    pd.set_option('float_format', '{:f}'.format)
    logger = get_logger('main')
    df_corr = pd.DataFrame(columns=['measure', 'doc_id', 'result_postings', 'result_votes'])

    i = 0
    for row in df_gc.iterrows():
        i = i + 1
        if i % 1000 == 0:
            logger.info(str(i))
        measure = row[1]['measure']
        experiment = row[1]['experiment']
        doc_id = row[1]['doc_id']
        result = row[1]['result']
        if experiment != 'postings_10000' and experiment != 'votes_10000':
            continue
        found_row = df_corr.loc[(df_corr['doc_id'] == doc_id) & (df_corr['measure'] == measure)]
        if found_row.empty:
            if experiment == 'postings_10000':
                df_corr.loc[len(df_corr)] = [measure, doc_id, result, np.NaN]
            else:
                df_corr.loc[len(df_corr)] = [measure, doc_id, np.NaN, result]
        else:
            if experiment == 'postings_10000':
                df_corr.at[found_row.index.values[0], 'result_postings'] = result
            else:
                df_corr.at[found_row.index.values[0], 'result_votes'] = result

    df_corr.to_csv('df_corr.csv', sep=';', decimal=',')


def calc_corr():
    df_gc = pd.read_csv('df_corr.csv', sep=';', decimal=',')
    df_gc = df_gc.dropna()
    print(df_gc.corr())
    #                 Unnamed: 0    doc_id  result_postings  result_votes
    # Unnamed: 0       1.000000    0.996090  0.028195         0.077944
    # doc_id           0.996090    1.000000  0.028652         0.079313
    # result_postings  0.028195    0.028652  1.000000         0.448838
    # result_votes     0.077944    0.079313  0.448838         1.000000
    df_gc[['measure', 'result_postings', 'result_votes']].groupby(['measure']).corr()
    #                            result_postings  result_votes
    # measure
    # BC         result_postings         1.000000      0.590386
    #            result_votes            0.590386      1.000000
    # EC         result_postings         1.000000      0.034328
    #            result_votes            0.034328      1.000000
    # ECU(corr)  result_postings         1.000000      0.143161
    #            result_votes            0.143161      1.000000
    # ECU(n30)   result_postings         1.000000      0.039604
    #            result_votes            0.039604      1.000000
    # MBLB       result_postings         1.000000      0.433537
    #            result_votes            0.433537      1.000000
    # Modularity result_postings         1.000000      0.670434
    #            result_votes            0.670434      1.000000
    # PI         result_postings         1.000000      0.636433
    #            result_votes            0.636433      1.000000
    # RWC        result_postings         1.000000      0.449498
    #            result_votes            0.449498      1.000000


if __name__ == '__main__':
    # create() # calculate dataframe and store it in csv
    calc_corr() # read created dataframe and print correlation
