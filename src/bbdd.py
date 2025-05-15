# -*- coding: utf-8 -*-
"""
Created on Fri May 29 13:55:27 2020
Modificat: 2025/04/27
@author: Natalia Pares Vives
"""


import sqlite3 as sq3


class Bbdd():

    def __init__(self, bbdd = None):

        self.bd_defecte = "../assets/bd/twic_1589.db"

        if bbdd is None:
            self.bd = self.bd_defecte
            # print("BBDD: " + self.bd)
        else:
            self.bd = bbdd

        # connecta
        # print("Connectant a la BBDD: " + self.bd)
        self.con = sq3.connect(self.bd)
        self.cur = self.con.cursor()
        self.reg = 1


    def tancaBBDD(self):
        self.cur.close()
        self.con.close()
        

    def fes_commit(self, con = None):
        if con is None:
            print("Error al fer commit, no hi ha connexio")
        else:
            con.commit()
        


    # llegeix tot d'una coleccio de partides i retorna tots els registres
    def llegeixPartides(self):
        self.cur.execute('SELECT * FROM partides')
        return self.cur.fetchall()
    

   
    # llegeix partidess amb filtre i retorna registres filtrats
    def llegeixBBDDFiltre(self, filtre):
        self.cur.execute('SELECT * FROM partides WHERE ' + filtre + ' ORDER BY blanc || "ZZZ" ASC, negre || "Z" ASC')
        return self.cur.fetchall()
    
   

    # inserta nou registre a Partides (retorna true o False)
    def insertaNou(self, white, elow, t_w, fideW, black, elob, t_b, fideB, event, site, round, date, result, ECO, FEN, var, ritmo, opening,
                    variation, study, chapter, commentator, num_game, moves):
        # inserta un registre a la taula partides
        cur = self.con.cursor()
        cur.execute("""INSERT INTO partides
            (blanc, elo_blanques, titol_blanc, fide_id_blanc, negre, elo_negres, titol_negre,
                fide_id_negre, torneig, lloc, ronda, data, resultat, eco, fen, variant, ritme,
                obertura, variacio, estudi, capitol, comentarista, num_partida, jugades)
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (white, elow, t_w, fideW, black, elob, t_b, fideB, event, site, round, date, result, ECO, FEN, var, ritmo,
                 opening, variation, study, chapter, commentator, num_game, moves))
        self.con.commit()

        if cur.rowcount <1:
            print("Cagada pastoret fent l'alta del registre")
            return False
        else:
            return True

   

          

####################      M A I N     ############################
#                                                                #
# per a poder fer TESTING d'aquest modul                         #
##################################################################
if __name__=='__main__':
    bd = Bbdd()
    llista_partides = []
    # es un test
    # bd per defecte


    llista_partides = bd.llegeixPartides()
    print(llista_partides)
    bd.tancaBBDD()
    print ("proces acabat amb exit")
