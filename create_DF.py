# -*- coding: utf-8 -*-

from alumn import *
import pandas as pd
import numpy as np
from heapq import merge
from sklearn_pandas import DataFrameMapper
import lib.apriori

import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.cluster import KMeans
import sklearn.metrics as sm

import sklearn.ensemble as sk



def get_alums(alumns):
    data = run_query("SELECT id_alumne FROM alumne")
    for alumn in data:
        alumns.append(Alumn(alumn))


def create_data_frame(alumns):
    data=[]
    for alumn in alumns:
        data.append([alumn.id_alu[0], alumn.renounce, alumn.p_alumn['mitja_exp'], alumn.p_pacces['mitja'],
                     alumn.p_pacces['conv'], alumn.p_alumn['centre']])



    df = pd.DataFrame(data=data, columns=['ALUMN', 'RENOUNCE', 'MITJA_EXP', 'MITJA_SEL', 'CONV', 'CENTRE'])

    print df
    print "\n\n------------------------------------------------------------\n\n"


    #do_clustering(df)
    #do_decision_tree(df)
    #do_assoc_rules(df)


def do_clustering(data_o):

    data = pd.DataFrame.copy(data_o)
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


    #Plot clustering
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

    return data



#Random forest
def do_decision_tree(data_o):

    #Dividir conjunt de dades en 5 parts
    data = (pd.DataFrame.copy(data_o))


    parts = 4
    lng = len(data_o) / parts
    lng_last = 0
    if len(data_o) % parts == 0:
        lng_last = lng
    else:
        lng_last = lng + (len(data_o) % parts)

    data_parts = []

    data_parts[0] = data[0:lng]
    data_parts[1] = data[lng:lng*2]
    data_parts[2] = data[lng*2:lng*3]
    data_parts[3] = data[lng*3:lng*4]
    data_parts[4] = data[lng*4:lng_last]

    it = parts
    while it > 0:

        df_test = data_parts[it-1]
        #Unir ses altres parts
        #df_train =

        dfm = DataFrameMapper(data)

        print '----- !! -----'
        print dfm

        clf = sk.RandomForestClassifier(n_estimators=100)

        #print clf

        #1. Crear dataframes x 'train' i x 'test'

        #DF train
        features = dfm.features
        y = pd.factorize(data['RENOUNCE'])[0]

        clf.fit(data[features], y)

        #DF test, Comprovar els resultats
        #clf.predict(test[features])

        it = it-1

    return



def do_assoc_rules(data):
    return



# ---------------- Clust, RF, Assoc_Rules with notes ----------

def create_data_frame_ext(alumns):

    # IN: List(k, v)
    # OUT: List(k, -1)
    def get_new_sig_list(list):
        n_list = dict()
        for item in list.items():
            n_list.update({item[0]: '-1'})
        return n_list

    #Crear dataframe de les notes x cada alumne,
    l_assig = dict()
    data = run_query('SELECT codi,nom FROM assig_sel')
    for assig in data:
        l_assig.update({str(assig[0]) : assig[1]})

    data=[]
    for alumn in alumns:
        n_asig = get_new_sig_list(l_assig)

        i=0
        while i < len(alumn.ca_pacces):
            n_asig.update({alumn.ca_pacces[i] : str(alumn.n_pacces[i])})
            i = i+1

        data.append([alumn.id_alu[0], alumn.renounce, alumn.p_alumn['mitja_exp'], alumn.p_pacces['mitja'],
                     alumn.p_pacces['conv'], alumn.p_alumn['centre']] + n_asig.values())


    cols = list(['ALUMN', 'RENOUNCE', 'MITJA_EXP', 'MITJA_SEL', 'CONV', 'CENTRE'] + l_assig.keys())
    df_alum_assig = pd.DataFrame(data=data, columns=cols )

    do_ext_clustering(df_alum_assig)

    return

# --------------- CLUSTERING WITH EXTENDED DATAFRAME ----------------------------
def do_ext_clustering(data_o, l_assig=dict()):
    data = pd.DataFrame.copy(data_o)
    # Convert CONV to INT before Kmeans, then recover first value
    d_conv = {}
    key = 1
    CONV_tmp = []
    for v_conv in data['CONV']:
        if not d_conv.has_key(key):
            if d_conv.has_key(key - 1) and d_conv[key - 1] == v_conv:
                CONV_tmp.append(key - 1)
            else:
                d_conv[key] = v_conv
                CONV_tmp.append(key)
                key += 1

    data['CONV'] = CONV_tmp

    # KMEANS
    km = KMeans(2, init='k-means++', random_state=3425)  # initialize
    cols = ['MITJA_EXP', 'MITJA_SEL', 'CONV'] + l_assig.keys()
    km.fit(data[cols])

    data['RENOUNCE_PRED'] = km.predict(data[cols])
    data.groupby(['RENOUNCE', 'RENOUNCE_PRED']).RENOUNCE.count()

    print pd.crosstab(data.RENOUNCE, data.RENOUNCE_PRED, rownames=['RENOUNCE'], colnames=['RENOUNCE_PRED'])

    # Plot clustering
    fig, ax = plt.subplots()


    #CAN USE PLOT IN THIS EXPERIMENT? I THINK THEY HAD TOO MANY VARIABLES
    print "\n\n"
    dcolor = ['b', 'g']
    for i in range(0, 2):
        color = dcolor[i]
        data[data.RENOUNCE == bool(i)].plot(kind='scatter', x='MITJA_EXP', y='MITJA_SEL', label=bool(i),
                                            ax=ax, color=color)

    handles, labels = ax.get_legend_handles_labels()

    _ = ax.legend(handles, labels, loc="upper left")
    #plt.show()


    # Recover the value of CONV
    data['CONV'] = [d_conv[k] for k in data['CONV']]

    return data


def do_ext_random_forest(data_o):
    # Dividir conjunt de dades en 5 parts
    data = (pd.DataFrame.copy(data_o))

    parts = 4
    lng = len(data_o) / parts
    lng_last = 0
    if len(data_o) % parts == 0:
        lng_last = lng
    else:
        lng_last = lng + (len(data_o) % parts)

    data_parts = []

    data_parts[0] = data[0:lng]
    data_parts[1] = data[lng:lng * 2]
    data_parts[2] = data[lng * 2:lng * 3]
    data_parts[3] = data[lng * 3:lng * 4]
    data_parts[4] = data[lng * 4:lng_last]

    it = parts
    while it > 0:
        df_test = data_parts[it - 1]
        # Unir ses altres parts
        # df_train =

        dfm = DataFrameMapper(data)

        print '----- !! -----'
        print dfm

        clf = sk.RandomForestClassifier(n_estimators=100)

        # print clf

        # 1. Crear dataframes x 'train' i x 'test'

        # DF train
        features = dfm.features
        y = pd.factorize(data['RENOUNCE'])[0]

        clf.fit(data[features], y)

        # DF test, Comprovar els resultats
        # clf.predict(test[features])

        it = it - 1


def do_ext_assoc_rules(data_o):
    return


# ----------------------- MAIN program ------------------------------
def main():

    alumns = []
    get_alums(alumns)

    #create_data_frame(alumns)
    create_data_frame_ext(alumns)

main()