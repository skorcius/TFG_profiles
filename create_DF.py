from alumn import *
import pandas as pd


import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.cluster import KMeans
import sklearn.metrics as sm



def get_alums(alumns):

    data = run_query("SELECT id_alumne FROM alumne")
    for alumn in data:
        alumns.append(Alumn(alumn))


def create_data_frame():
    alumns=[]

    get_alums(alumns)

    data=[]
    for alumn in alumns:
        data.append([alumn.id_alu[0], alumn.renounce, alumn.p_alumn['mitja_exp'], alumn.p_pacces['mitja'],
                     alumn.p_pacces['conv'], alumn.p_alumn['centre']])



    df = pd.DataFrame(data=data, columns=['ALUMN', 'RENOUNCE', 'MITJA_EXP', 'MITJA_SEL', 'CONV', 'CENTRE'])
    print df
    print "\n\n------------------------------------------------------------\n\n"

    do_clustering(df)


# 2 clusters (0 abandonen, 1 continuen) o al reves!!
def do_clustering(data):

    km = KMeans(2, init='k-means++', random_state=3425)  # initialize
    km.fit(data[['MITJA_EXP','MITJA_SEL']])
    data['RENOUNCE_PRED'] = km.predict(data[['MITJA_EXP','MITJA_SEL']])
    data.groupby(['RENOUNCE','RENOUNCE_PRED']).RENOUNCE.count()
    print pd.crosstab(data.RENOUNCE, data.RENOUNCE_PRED, rownames=['RENOUNCE'], colnames=['RENOUNCE_PRED'])

    print data
    return



def do_decision_tree(data):
    return



def do_assoc_rules(data):
    return






def test_clustering():


    return





create_data_frame()
