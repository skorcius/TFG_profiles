# -*- coding: utf-8 -*-

import MySQLdb
import _mysql_exceptions


infoDB = {
    'user': 'joan',
    'passwd': '1234',
    'host': 'localhost',
    'db': 'profiles'
}

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
            print "ERROR: No se ha podido ejecutar la sentencia '%s' " % query



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


def execute_insert(insert=''):
    conn = MySQLdb.connect(**infoDB)  # Conectar a la base de datos
    cursor = conn.cursor()  # Crear un cursor
    cursor.execute(insert)  # Ejecutar una consulta

    conn.commit()  # Hacer efectiva la escritura de datos

    id = cursor.lastrowid

    cursor.close()  # Cerrar el cursor
    conn.close()  # Cerrar la conexión

    return id
