from alumn import *
import pandas as pd
import numpy as np




import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.cluster import KMeans
import sklearn.metrics as sm

import sklearn.ensemble as sk



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
    do_decision_tree(df)
    do_assoc_rules(df)


def do_clustering(data):

    #Convert CONV to INT before Kmeans, then recover first value
    d_conv = {}
    key = 1
    CONV_tmp = []
    for v_conv in data['CONV']:
        if not d_conv.has_key(key):
            if d_conv.has_key(key-1) and d_conv[key-1] == v_conv:
                CONV_tmp.append(key-1)
            else:
                d_conv[key] = v_conv
                CONV_tmp.append(key)
                key += 1

    data['CONV'] = CONV_tmp


    #KMEANS
    km = KMeans(2, init='k-means++', random_state=3425)  # initialize
    km.fit(data[['MITJA_EXP','MITJA_SEL','CONV']])
    data['RENOUNCE_PRED'] = km.predict(data[['MITJA_EXP','MITJA_SEL','CONV']])
    data.groupby(['RENOUNCE','RENOUNCE_PRED']).RENOUNCE.count()
    print pd.crosstab(data.RENOUNCE, data.RENOUNCE_PRED, rownames=['RENOUNCE'], colnames=['RENOUNCE_PRED'])


    #Trying to plot clustering
    fig, ax = plt.subplots()

    print "\n\n"
    dcolor = ['b','g']
    for i in range(0,2):
        color = dcolor[i]
        data[data.RENOUNCE == bool(i)].plot(kind='scatter', x='MITJA_EXP', y='MITJA_SEL', label=bool(i),
                                            ax = ax, color=color)

    handles, labels = ax.get_legend_handles_labels()

    _ = ax.legend(handles, labels, loc="upper left")
    #plt.show()


    #Recover the value of CONV
    data['CONV'] = [d_conv[k] for k in data['CONV']]



#Random forest
def do_decision_tree(data):

    clf = sk.RandomForestClassifier(n_estimators=100)
    clf = clf.fit(data, [2,3,4])

    print clf




    return



def do_assoc_rules(data):
    return







create_data_frame()
