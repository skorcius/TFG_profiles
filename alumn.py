# -*- coding: utf-8 -*-

from con_SQL import *

class Alumn:

    def __init__(self, id):
        self.id_alu = id

        self.p_alumn = {'mitja_exp':'', 'centre':'', 'nota_ac_pre':'', 'conv_batx':'', 'anyBatx1':'',
                         'anyBatx2':'', 'ordre_pref':''}
        self.set_alumn_profile()

        #Information about selectivity
        self.n_pacces = []
        self.a_pacces = []
        self.ca_pacces = []
        self.f_pacces = []

        self.p_pacces = {'mitja':'', 'any1':'', 'any2':'', 'conv':'', 'subacc':'', 'nom_subacc':'', 'uni':''}
        self.set_selectivity_profile()

        #Information about the degree
        self.p_subject_1 = {}
        self.first_year = 0
        self.set_degree_profile()

        self.renounce = False
        self.set_renounce()



    def set_alumn_profile(self):
        data = run_query("SELECT mitja_exp, centre, nota_acces_preinscripcio, t_valors.valor,anyBat1,anyBat2, " \
                         "ordre_pref, id_prova FROM alumne JOIN t_valors " \
                         "ON alumne.conv_batx = t_valors.id WHERE alumne.id_alumne = %s" %self.id_alu)

        if len(data) == 1:
            self.p_alumn['mitja_exp'] = data[0][0]
            self.p_alumn['centre']  = str(data[0][1])
            if data[0][2] == None:
                self.p_alumn['nota_ac_pre'] = 0
            else:
                self.p_alumn['nota_ac_pre'] = data[0][2]
            self.p_alumn['conv_batx'] = data[0][3]
            self.p_alumn['anyBatx1'] = data[0][4]
            self.p_alumn['anyBatx2'] = data[0][5]
            if data[0][6] == None:
                self.p_alumn['ordre_pref'] = 0
            else:
                self.p_alumn['ordre_pref'] = data[0][6]
            self.id_test = data[0][7]


    def set_selectivity_profile(self):
        if self.id_test != None:
            data = run_query("SELECT nota,any1,any2,t_valors.valor,sub_acces,nom_subacces,universitat" \
            " FROM p_acces JOIN t_valors ON p_acces.conv = t_valors.id WHERE p_acces.id = %s" %self.id_test)

            if len(data) == 1:
                self.p_pacces['mitja'] = data[0][0]
                self.p_pacces['any1'] = data[0][1]
                self.p_pacces['any2'] = data[0][2]
                self.p_pacces['conv'] = data[0][3]
                self.p_pacces['subacc'] = data[0][4]
                self.p_pacces['nom_subacc'] = data[0][5]
                self.p_pacces['uni'] = data[0][6]

            data = run_query("select nota, assig_sel.nom, t_valors.valor, assig_sel.codi from assig_prova join assig_sel "\
                             "on assig_prova.id_assig = assig_sel.codi join t_valors on t_valors.id = assig_prova.fase"\
                             " where assig_prova.id_prova = %s" %self.id_test)

            for row in data:
                self.n_pacces.append(str(row[0]))
                self.a_pacces.append(str(row[1]))
                self.f_pacces.append(str(row[2]))
                self.ca_pacces.append(str(row[3]))


    def set_degree_profile(self):
        data = run_query("select id_assig, any1, any2, t_valors.valor, num_matricula, presentat, nota  " \
                         "from alumne_assig join t_valors on t_valors.id = conv " \
                         "where id_alumne = %s order by any1" %self.id_alu)

        self.first_year=0
        notes = []
        bef_sub = 0


        for row in data:
            if self.first_year == 0:
                self.first_year = row[1]

            if row[1] == self.first_year: #First year subject {id_assig -> [nota1(FEB o JUN), nota2(JUL o SET)]}

               if bef_sub == 0:
                    bef_sub = row[0]
                    notes.append(row[6])

               elif bef_sub == row[0]:
                    notes.append(row[6])
                    self.p_subject_1[row[0]] = notes
                    bef_sub = 0
                    notes = []


    def set_renounce(self):
        data = run_query("SELECT * FROM alumne_assig WHERE id_alumne = %s and any1 = %s" \
                         % (self.id_alu[0], self.first_year+1))

        if len(data) > 1:
            self.renounce = False
        else:

            data = run_query("SELECT * FROM alumne_assig WHERE id_alumne = %s and any1 = %s" \
                             % (self.id_alu[0], self.first_year + 2))
            if len(data) < 1:
                self.renounce = True


    def toString(self):
        str = "Alumne ID: %s \n\n" %self.id_alu
        str += "\tInformació selectivitat: \n"
        str += "\t\t "
        for k, v in self.p_pacces.items():
            str += "{0}:{1}, ".format(k,v)
        str += "\n"
        str += "\t\t Assignatures Selectivitat: \n"
        for i in range(len(self.n_pacces)):
            str += "\t\t\t Assignatura: {0}, Nota: {1}\n".format(self.a_pacces[i],self.n_pacces[i])
        str += "\n\n"

        str += "\tInformació grau: \n"
        str += "\t\t Assignatures primer curs ({0}-{1}): \n".format(self.first_year, self.first_year+1)
        for k,v in self.p_subject_1.items():
            str += "\t\t\tAssignatura: {0}".format(k)
            for value in v:
                str += ", Nota: {0}".format(value)
            str += "\n"

        if self.renounce:
            str += "\n \t\t L'alumne ha abandonat el grau"
        else:
            str += "\n \t\t L'alumne continua amb el grau"

        str += "\n\n"
        return str


