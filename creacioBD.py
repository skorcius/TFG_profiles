# -*- coding: utf-8 -*-

from _codecs import utf_8_decode

import MySQLdb
import csv

import _mysql_exceptions
from cvxopt import info
from xml.dom import minidom

## GLobal data
	#Predefined info about MySQL
infoDB = {
    'user': 'joan',
    'passwd': '1234',
    'host': 'localhost',
    'db': 'profiles'
}

## ----------------------------

def run_query(query=''):
    conn = MySQLdb.connect(**infoDB)  # Conectar a la base de datos
    cursor = conn.cursor()  # Crear un cursor
    cursor.execute(query)  # Ejecutar una consulta

    if query.upper().startswith('SELECT'):
        data = cursor.fetchall()  # Traer los resultados de un select
    else:
        conn.commit()  # Hacer efectiva la escritura de datos
        data = None

    cursor.close()  # Cerrar el cursor
    conn.close()  # Cerrar la conexión

    return data


def convert_csv_to_xml(path='', xmlDataFiles={}):

    tmp = path.split('/')
    filename = tmp[len(tmp)-1]

    xml=filename[0:len(filename)-3]+"xml"
    csvfile = open(path, 'rt')
    xmlfile = open(xml, 'w')

    xmlfile.write('<?xml version="1.0"?>' + "\n")
    xmlfile.write('<csv_data>' + '\n')

    try:
        reader = csv.reader(csvfile, delimiter=",")

        rowNum = 0
        for row in reader:
            if rowNum == 0:
                tags = row
                for i in range(len(tags)):
                    tags[i] = tags[i].replace(' ', '_')
            else:
                xmlfile.write('<row>' + '\n')
                for i in range(len(tags)):
                    xmlfile.write('     '+'<'+tags[i] + '>'+ row[i] + '</' + tags[i] + '>' + '\n')
                xmlfile.write('</row>'+'\n')
            rowNum += 1

        #cargar datos para el header obtenido
        xmlfile.write('</csv_data>')

        header=""
        for data in tags:
            header = header + data + ','
        header = header[0:len(header) - 1]


        if header == "ID_ALU,PLA,NOM,CODI_RUCT,ANY_PROVA,CONV_PROVA,FASE,CODI_MATERIA,NOM_MATERIA,PRESENTAT,NOTA":
            xmlDataFiles['a_sel'] = xml
        elif header == "ID_ALU,PLA,NOM,CODI_RUCT,ANY_INICI_ESTUDIS,ORDRE_PREFERENCIA_PREINSCRIPCIO," \
                "NOTA_ACCES_PREINSCRIPCIO,TIPUS_ACCES,NOM_TIPUS,SUBACCES,NOM_SUBACCES,ANY_ACCES,CONV_ACCES," \
                "UNIVERSITAT_PROVA,NOTA_PROVA,ANY_BATXILLER,CONV_BATXILLER,CENTRE_BATXILLER,MITJA_EXPEDIENT":
            xmlDataFiles['d_acces'] = xml
        elif header == "ID_ALU,PLA,NOM,CODI_RUCT,ANY,CRED_MAT_TOTAL,CRED_1_MAT,CRED_2_MAT,CRED_3_MAT," \
                        "CRED_SUPERATS,CRED_NO_SUPERAT,CRED_RECONEGUTS,CRED_PRESENTAT,CRED_NOPRESENTAT":
            xmlDataFiles['d_matricula']=xml
        elif header == "ID_ALU,PLA,NOM,CODI_RUCT,ASSIG,CURS,TIPUS,CREDITS,NUM_MATRIC,ANY,CONVOCATORIA," \
                       "PRESENTAT,MHONOR,NOTA,QUALIFICACIO":
            xmlDataFiles['l_acta'] = xml

    finally:
        csvfile.close()
        xmlfile.close()



def create_DB(nameDB="profiles"):
    infoDB['db'] = nameDB
    conn = MySQLdb.connect(user=infoDB['user'], passwd=infoDB['passwd'], host=infoDB['host'])
    loadInfo = False
    try:
        cursor=conn.cursor()
        sql="CREATE DATABASE %s" % nameDB
        cursor.execute(sql)

        create_Tables()

        insert_t_valorsInfo("FEB JUN SET GEN ESP FBA OBL OPT TFG")

        loadInfo=True                     #La BD no existe, debemos cargar la info en la BD
    except _mysql_exceptions.DatabaseError:
        loadInfo=False                    #La BD ya existe, no cargar info en la BD
    finally:
        conn.close()

    return loadInfo


def create_Tables():
    conn = MySQLdb.connect(user=infoDB['user'], passwd=infoDB['passwd'], host=infoDB['host'], db=infoDB['db'])

    try:
        cursor = conn.cursor()

        #Taules per guardar informació repetitiva (FEB JUN, SET, GEN, ESP, FBA, OBL, OPT, TFG)
        c_query = "CREATE TABLE t_valors (id int auto_increment primary key, valor varchar(10) not null)"
        cursor.execute(c_query)

        #Taules per guardar l'informació de selectivitat
        c_query =   """CREATE TABLE p_acces (
	                nota float not null, #nota mitja de selectivitat
	                any1 int not null,
	                any2 int not null,
	                id int auto_increment primary key,
	                conv int not null,
	                universitat varchar(50),
	                foreign key (conv) references t_valors(id) )"""
        cursor.execute(c_query)

        c_query =   """CREATE TABLE assig_sel (
	                codi int primary key,
	                nom varchar(70) not null )"""
        cursor.execute(c_query)

        c_query =   """CREATE TABLE assig_prova (
	                id_prova int,
	                id_assig int,
	                nota float not null,
	                presentat boolean not null default false,
	                fase int not null,
	                primary key (id_prova, id_assig),
	                foreign key (id_prova) references p_acces(id),
	                foreign key (id_assig) references assig_sel(codi),
	                foreign key (fase) references t_valors(id) )"""
        cursor.execute(c_query)

        #Taule Alumne
        c_query=    """CREATE TABLE alumne (
	                id_alumne int auto_increment primary key,
                	mitja_exp float not null,
	                centre varchar(150),
	                id_prova int,
                	conv_batx int not null,
	                foreign key (id_prova) references p_acces(id),
	                foreign key (conv_batx) references t_valors(id) )"""
        cursor.execute(c_query)

        #Taules per l'informació del grau
        c_query =   """CREATE TABLE matricula (
	                id int auto_increment primary key,
	                any1 int not null,
	                any2 int not null,
                	ordre_preferencia int not null,
	                cred_1 int not null default 0,
	                cred_2 int not null default 0,
	                cred_3 int not null default 0,
	                cred_sup int not null default 0,
	                cred_rec int not null default 0,
	                cred_pres int not null default 0,
	                cred_no_pres int not null default 0,
	                alumne int not null,
	                foreign key (alumne) references alumne(id_alumne) )"""
        cursor.execute(c_query)

        c_query =   """CREATE TABLE grau (
	                id_grau int primary key,
	                nom varchar(70) not null,
	                pla varchar(30) not null )"""
        cursor.execute(c_query)

        c_query =   """CREATE TABLE assig (
                    id_assig int primary key )"""
        cursor.execute(c_query)

        c_query =   """CREATE TABLE assig_grau (
	                id_grau int,
            	    id_assig int,
	                curs int not null,
            	    tipus int not null,
	                credits int not null,
	                primary key (id_grau, id_assig),
	                foreign key (tipus) references t_valors(id),
	                foreign key (id_grau) references grau(id_grau),
	                foreign key (id_assig) references assig(id_assig) )"""
        cursor.execute(c_query)

        c_query =   """CREATE TABLE alumne_assig (
	                id_alumne int,
	                id_assig int,
	                any1 int not null,
                	any2 int not null,
                	conv int,
	                nota float not null default 0,
	                m_honor boolean default false,
	                presentat boolean not null default false,
	                primary key (id_alumne, id_assig) ,
	                foreign key (id_alumne) references alumne(id_alumne),
	                foreign key (id_assig) references assig(id_assig),
	                foreign key (conv) references t_valors(id) )"""
        cursor.execute(c_query)

    finally:
        conn.close()


def insert_t_valorsInfo(valors=""):
    i_query="INSERT INTO t_valors (valor) VALUES "

    primer = True
    for valor in valors.split():
        if primer:
           primer = False
           i_query = i_query + "('%s')" % valor
        else:
            i_query = i_query + ",('%s')" % valor

    run_query(i_query)

def insert_xml_to_bd(xmlDataFiles={}):
    print





def main():
    xmlDataFiles = {'d_acces' : 'dades_acces.xml', 'd_matricula' : 'dades_matricula.xml',
                    'l_acta' : 'linies_acta.xml', 'a_sel' : 'assig_sel.xml'}

    path = "/home/joan/Documents/"

    load_info = create_DB()

    if load_info:
        convert_csv_to_xml(path+"assig_sel.csv", xmlDataFiles)
        convert_csv_to_xml(path + "dades_acces.csv", xmlDataFiles)
        convert_csv_to_xml(path + "dades_matricula.csv", xmlDataFiles)
        convert_csv_to_xml(path + "linies_acta.csv", xmlDataFiles)

        insert_xml_to_bd(xmlDataFiles)
    else:
        print "No s'ha de crear la BD"



main()
