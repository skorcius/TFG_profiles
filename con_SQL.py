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
            conn = MySQLdb.connect(**infoDB)    #Connect to DB
            cursor = conn.cursor()              #Create a cursor
            cursor.execute(query)               #Make the query

            if query.upper().startswith('SELECT'):
                data = cursor.fetchall()        #Bring results from select
            else:
                conn.commit()                   #Commit the query if it's not a select
                data = None

            cursor.close()                      #Close the cursor
            conn.close()                        #Close the connection

            return data
        except _mysql_exceptions.DataError:
            print "ERROR: No se ha podido ejecutar la sentencia '%s' " % query



def exist_in_db(query=''):
    conn = MySQLdb.connect(**infoDB)
    cursor = conn.cursor()
    cursor.execute(query)

    if query.upper().startswith('SELECT'):
        data = cursor.fetchall()
    else:
        data = None

    cursor.close()
    conn.close()

    if len(data) == 0:
        return False
    else:
        return True


def execute_insert(insert=''):
    conn = MySQLdb.connect(**infoDB)
    cursor = conn.cursor()
    cursor.execute(insert)

    conn.commit()

    id = cursor.lastrowid   #Get ID from the last insert

    cursor.close()
    conn.close()

    return id
