from con_SQL import *

class Alumne:

    info_db = {}

    def __init__(self, id, db):
        self.id_alu = id
        info_db = db


    #Metodo para realizar las consultas

    #Perfil de selectivitat

    #Dades obtingudes del primer curs

    #Calcular si ha abandonat a segon any


    def set_perfil_selectivitat(self):
        id_prova = run_query("SELECT * FROM alumne WHERE id_alumne = %s" % self.id_alu)



    def toString(self):
        print "Alumne ID: %s" %self.id_alu