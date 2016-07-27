from con_SQL import *
from alumn import *
import numpy
import pandas as pd



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


create_data_frame()