# -*- coding: utf-8 -*-

import MySQLdb
import csv

import _mysql_exceptions
from enum import Enum


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
    try:
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
    except _mysql_exceptions.DataError:
        print "ERROR: No se ha podido ejecutar la sentencia '%s' " %query


def execute_insert(insert=''):
    conn = MySQLdb.connect(**infoDB)  # Conectar a la base de datos
    cursor = conn.cursor()  # Crear un cursor
    cursor.execute(insert)  # Ejecutar una consulta

    conn.commit()  # Hacer efectiva la escritura de datos

    id = cursor.lastrowid

    cursor.close()  # Cerrar el cursor
    conn.close()  # Cerrar la conexión

    return id


def exist_in_db(query=''):
    conn = MySQLdb.connect(**infoDB)  # Conectar a la base de datos
    cursor = conn.cursor()  # Crear un cursor
    cursor.execute(query)  # Ejecutar una consulta

    if query.upper().startswith('SELECT'):
        data = cursor.fetchall()  # Traer los resultados de un select
    else:
        data = None

    cursor.close()  # Cerrar el cursor
    conn.close()  # Cerrar la conexión

    if len(data) == 0:
        return False
    else:
        return True


def prepare_info_for_db(path="", files=[]):

    for file in files:
        filename=path+file

        csvFile = csv.reader(open(filename, 'r'), delimiter=",")

        try:
            rowNum=0
            header=""
            for row in csvFile:
                for item in row:
                    header = header + item + ','
                break
            header = header[0:len(header)-1]

            if header == "ID_ALU,PLA,NOM,CODI_RUCT,ANY_PROVA,CONV_PROVA,FASE,CODI_MATERIA,NOM_MATERIA,PRESENTAT,NOTA":
                inserts_assig_sel(csvFile)
            elif header == "ID_ALU,PLA,NOM,CODI_RUCT,ANY_INICI_ESTUDIS,ORDRE_PREFERENCIA_PREINSCRIPCIO," \
                           "NOTA_ACCES_PREINSCRIPCIO,TIPUS_ACCES,NOM_TIPUS,SUBACCES,NOM_SUBACCES,ANY_ACCES,CONV_ACCES," \
                           "UNIVERSITAT_PROVA,NOTA_PROVA,ANY_BATXILLER,CONV_BATXILLER,CENTRE_BATXILLER,MITJA_EXPEDIENT":
                inserts_dades_acces(csvFile)
            elif header == "ID_ALU,PLA,NOM,CODI_RUCT,ANY,CRED_MAT_TOTAL,CRED_1_MAT,CRED_2_MAT,CRED_3_MAT," \
                           "CRED_SUPERATS,CRED_NO_SUPERAT,CRED_RECONEGUTS,CRED_PRESENTAT,CRED_NOPRESENTAT":
                inserts_dades_matricula(csvFile)
            elif header == "ID_ALU,PLA,NOM,CODI_RUCT,ASSIG,CURS,TIPUS,CREDITS,NUM_MATRIC,ANY,CONVOCATORIA," \
                           "PRESENTAT,MHONOR,NOTA,QUALIFICACIO":
                inserts_lines_acta(csvFile)

        except IOError:
            print "ERROR: Fichero no encontrado"


def enum(**enums):
    return type('Enum', (), enums)


def get_dates(date=""):
    dates = date.split('-')
    if len(dates) == 2:
        dates[1] = dates[0][0:len(dates[0])-len(dates[1])] + dates[1]
        return dates
    return None



def inserts_dades_acces(reader=[]):
    CNT = enum(ID=0, PLA=1, NOM=2, C_PLA=3, ANY_I_EST = 4, ORDRE_PREF = 5, NOTA_A_PREINS=6, TIPUS_ACCES=7,
                 NOM_TIPUS=8, SUBACCES=9, NOM_SUBACCES=10, ANY_ACCES=11, CONV_ACCES=12, UNI=13, NOTA_PROVA=14,
                 ANY_BATX = 15, CONV_BATX=16, CENTRE_BATX=17, MITJA_EXP=18)
    VALORS = dict()

    data = run_query("SELECT id, valor FROM t_valors")
    for row in data:
        VALORS.update({row[1] : row[0]})


    for row in reader:

        #Tratamiento de valores nulos
        for i in range(len(row)):
            if row[i] == '':
                row[i] = 'null'

        #Insertar el grau si no existeix
        if not exist_in_db("SELECT * FROM grau where id_grau = %s" %row[CNT.C_PLA]):
            insert = "INSERT INTO grau (id_grau, nom, pla) VALUES  (%s, \"%s\", \"%s\")" \
                     %(row[CNT.C_PLA], row[CNT.NOM], row[CNT.PLA])
            run_query(insert)

        #Comprobar si l'usuari existeix
        if not exist_in_db("SELECT id_alumne, id_prova FROM alumne WHERE id_alumne = %s" %row[CNT.ID]):

            #Insertar prova d'acces y usuari
            if row[CNT.TIPUS_ACCES] == '1':
                dates = get_dates(row[CNT.ANY_ACCES])

                insert = "INSERT INTO p_acces (universitat, sub_acces, nom_subacces, nota, any1, any2, conv) VALUES " \
                     "(\"%s\", %s,\"%s\",%s, %s, %s, %s)" %(row[CNT.UNI], row[CNT.SUBACCES], row[CNT.NOM_SUBACCES],
                                            row[CNT.NOTA_PROVA], dates[0], dates[1], VALORS.get(row[CNT.CONV_ACCES]))
                id_prova = execute_insert(insert)
                dates = get_dates(row[CNT.ANY_BATX])

                insert = "INSERT INTO alumne (id_alumne, centre, mitja_exp, nota_acces_preinscripcio, id_prova, " \
                         "conv_batx, anyBat1, anyBat2, ordre_pref) VALUES (%s, \"%s\", %s, %s, %s, %s, %s, %s, %s)" %(row[CNT.ID],
                         row[CNT.CENTRE_BATX], row[CNT.MITJA_EXP], row[CNT.NOTA_A_PREINS], id_prova,
                         VALORS.get(row[CNT.CONV_BATX]), dates[0], dates[1], row[CNT.ORDRE_PREF])
                execute_insert(insert)



def inserts_assig_sel(reader):
    CNT = enum(ID_ALU=0,PLA=1,NOM=2,C_PLA=3,ANY_PROVA=4,CONV_PROVA=5,FASE=6,C_MATERIA=7,
               NOM_MATERIA=8,PRESENTAT=9,NOTA=10)
    VALORS = dict()

    data = run_query("SELECT id, valor FROM t_valors")
    for row in data:
        VALORS.update({row[1]: row[0]})

    for row in reader:
        #Tratamiento de valores nulos
        for i in range(len(row)):
            if row[i] == '':
                row[i] = 'null'

        # Insertar el grado si no existe
        if not exist_in_db("SELECT * FROM grau where id_grau = %s" % row[CNT.C_PLA]):
            insert = "INSERT INTO grau (id_grau, nom, pla) VALUES  (%s, \"%s\", \"%s\")" \
               % (row[CNT.C_PLA], row[CNT.NOM], row[CNT.PLA])
            run_query(insert)

        #Insertar la asignatura si no existe
        if not exist_in_db("SELECT * FROM assig_sel WHERE codi = %s" % row[CNT.C_MATERIA]):
            insert = "INSERT INTO assig_sel (codi, nom) VALUES (%s, \"%s\")" %(row[CNT.C_MATERIA], row[CNT.NOM_MATERIA])
            run_query(insert)

        if exist_in_db("SELECT id_prova FROM alumne WHERE id_alumne = %s" %row[CNT.ID_ALU]):
            data=run_query("SELECT id_prova FROM alumne WHERE id_alumne = %s" %row[CNT.ID_ALU])
            id_prova = data[0][0]

            pres = 0
            if row[CNT.PRESENTAT] == 's' or row[CNT.PRESENTAT] == 'S':
                pres = 1

            insert = "INSERT INTO assig_prova (id_prova, id_assig, nota, presentat, fase) VALUES (%s, %s, %s, %s, %s)" \
                %(id_prova, row[CNT.C_MATERIA], row[CNT.NOTA], pres, VALORS.get(row[CNT.FASE]) )
            run_query(insert)


def inserts_dades_matricula(reader):
    CNT = enum(ID_ALU=0,PLA=1,NOM=2,C_PLA=3,ANY=4,CRED_MAT_TOTAL=5,CRED_1_MAT=6,CRED_2_MAT=7,CRED_3_MAT=8,
                           CRED_SUPERATS=9,CRED_NO_SUPERAT=10,CRED_RECONEGUTS=11,CRED_PRESENTAT=12,CRED_NOPRESENTAT=13)

    VALORS = dict()

    data = run_query("SELECT id, valor FROM t_valors")
    for row in data:
        VALORS.update({row[1]: row[0]})

    for row in reader:
        # Tratamiento de valores nulos
        for i in range(len(row)):
            if row[i] == '':
                row[i] = 'null'

            # Insertar el grado si no existe
            if not exist_in_db("SELECT * FROM grau where id_grau = %s" % row[CNT.C_PLA]):
                insert = "INSERT INTO grau (id_grau, nom, pla) VALUES  (%s, \"%s\", \"%s\")" \
                         % (row[CNT.C_PLA], row[CNT.NOM], row[CNT.PLA])
                run_query(insert)

            dates=get_dates(row[CNT.ANY])

            #Si el usuario existe introducimos la matricula
            if exist_in_db("SELECT * FROM alumne WHERE id_alumne = %s" %row[CNT.ID_ALU]):
                insert="INSERT INTO matricula (any1, any2, cred_1, cred_2, cred_3, cred_sup, cred_no_sup, cred_rec, " \
                   "cred_pres, cred_no_pres, alumne, id_grau) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" \
                      %(dates[0], dates[1], row[CNT.CRED_1_MAT], row[CNT.CRED_2_MAT], row[CNT.CRED_3_MAT],
                      row[CNT.CRED_SUPERATS], row[CNT.CRED_NO_SUPERAT], row[CNT.CRED_RECONEGUTS],
                      row[CNT.CRED_PRESENTAT], row[CNT.CRED_NOPRESENTAT], row[CNT.ID_ALU], row[CNT.C_PLA])
                run_query(insert)



def inserts_lines_acta(reader):
    CNT = enum(ID_ALU=0,PLA=1,NOM=2,C_PLA=3,ASSIG=4,CURS=5,TIPUS=6,CREDITS=7,NUM_MATRIC=8,ANY=9,
               CONVOCATORIA=10,PRESENTAT=11,MHONOR=12,NOTA=13,QUALIFICACIO=14)

    VALORS = dict()

    data = run_query("SELECT id, valor FROM t_valors")
    for row in data:
        VALORS.update({row[1]: row[0]})

    for row in reader:
        # Tratamiento de valores nulos
        for i in range(len(row)):
            if row[i] == '':
                row[i] = 'null'

        # Insertar el grado si no existe
        if not exist_in_db("SELECT * FROM grau where id_grau = %s" % row[CNT.C_PLA]):
            insert = "INSERT INTO grau (id_grau, nom, pla) VALUES  (%s, \"%s\", \"%s\")" \
                        % (row[CNT.C_PLA], row[CNT.NOM], row[CNT.PLA])
            run_query(insert)

        #Insertar assignatura si no existe
        if not exist_in_db("SELECT * FROM assig WHERE id_assig = %s" %row[CNT.ASSIG]):
            insert = "INSERT INTO assig (id_assig) VALUES (%s)" %row[CNT.ASSIG]
            run_query(insert)

        if not exist_in_db("SELECT * FROM assig_grau WHERE id_grau = %s and id_assig = %s" %(row[CNT.C_PLA], row[CNT.ASSIG])):
            insert="INSERT INTO assig_grau (id_grau, id_assig, curs, tipus, credits) VALUES (%s,%s,%s,%s,%s)" \
               %(row[CNT.C_PLA], row[CNT.ASSIG], row[CNT.CURS], VALORS.get(row[CNT.TIPUS]), row[CNT.CREDITS] )
            run_query(insert)

        if exist_in_db("SELECT * FROM alumne WHERE id_alumne = %s" %row[CNT.ID_ALU]):

            dates=get_dates(row[CNT.ANY])
            presentat=0
            if row[CNT.PRESENTAT] == 'S' or row[CNT.PRESENTAT] == 's':
                presentat = 1
            else:
                row[CNT.NOTA] = '0'

            m_honor = 0
            if row[CNT.MHONOR] == 'S' or row[CNT.MHONOR] == 's':
                m_honor=1

            insert="INSERT INTO alumne_assig (id_alumne, id_assig, num_matricula, any1, any2, conv, nota, presentat, m_honor) VALUES " \
                   "(%s, %s, %s, %s,%s, %s, %s, %s, %s)" %(row[CNT.ID_ALU], row[CNT.ASSIG], row[CNT.NUM_MATRIC],dates[0], dates[1],
                                                VALORS.get(row[CNT.CONVOCATORIA]), row[CNT.NOTA], presentat, m_honor)
            run_query(insert)


def create_DB(nameDB="profiles"):
    infoDB['db'] = nameDB
    conn = MySQLdb.connect(user=infoDB['user'], passwd=infoDB['passwd'], host=infoDB['host'])
    dbExist = False
    try:
        cursor=conn.cursor()
        sql="CREATE DATABASE %s" % nameDB
        cursor.execute(sql)
        cursor.close()

        create_Tables()

        insert_t_valorsInfo("FEB JUN JUL SET GEN ESP FBA OBL OPT TFG")

        dbExist=False                     #La BD no existe, debemos cargar la info en la BD
    except _mysql_exceptions.DatabaseError:
        dbExist=True                    #La BD ya existe, no cargar info en la BD
    finally:
        conn.close()

    return dbExist


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
	                sub_acces int,
	                nom_subacces varchar(200),
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
	                nota_acces_preinscripcio float,
	                id_prova int,
                	conv_batx int not null,
                	anyBat1 int,
                	anyBat2 int,
                	ordre_pref int,
	                foreign key (id_prova) references p_acces(id),
	                foreign key (conv_batx) references t_valors(id) )"""
        cursor.execute(c_query)

        c_query = """CREATE TABLE grau (
        	                id_grau int primary key,
        	                nom varchar(70) not null,
        	                pla varchar(30) not null )"""
        cursor.execute(c_query)

        #Taules per l'informació del grau
        c_query =   """CREATE TABLE matricula (
	                id int auto_increment primary key,
	                any1 int not null,
	                any2 int not null,
	                cred_1 int not null default 0,
	                cred_2 int not null default 0,
	                cred_3 int not null default 0,
	                cred_sup int not null default 0,
	                cred_no_sup int not null default 0,
	                cred_rec int not null default 0,
	                cred_pres int not null default 0,
	                cred_no_pres int not null default 0,
	                alumne int not null,
	                id_grau int not null,
	                foreign key (alumne) references alumne(id_alumne),
	                foreign key (id_grau) references grau(id_grau) )"""
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
                    id int auto_increment primary key,
	                id_alumne int,
	                id_assig int,
	                any1 int not null,
                	any2 int not null,
                	conv int,
                	num_matricula int,
	                nota float not null default 0,
	                m_honor boolean default false,
	                presentat boolean not null default false,
	                foreign key (id_alumne) references alumne(id_alumne),
	                foreign key (id_assig) references assig(id_assig),
	                foreign key (conv) references t_valors(id),
	                unique c_intent (id_alumne, id_assig, conv, num_matricula, any1, any2))"""
        cursor.execute(c_query)
        cursor.close()
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

def main():
    files = ['dades_acces.csv','assig_sel.csv', 'dades_matricula.csv', 'linies_acta.csv']

    path = ""

    dbExist = create_DB()
    dbExist = False
    if not dbExist:
        prepare_info_for_db(path, files)


main()
