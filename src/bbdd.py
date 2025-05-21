# -*- coding: utf-8 -*-
"""
Created on Fri May 29 13:55:27 2020
Modificat: 2025/04/27
@author: Natalia Pares Vives
"""

import io
import sqlite3 as sq3
import chess
import chess.pgn


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
    
        
    def llegeixPartidesDetallades(self):
        conn = self.con
        # Retornar com a diccionaris per facilitar l'accés per nom de columna
        conn.row_factory = sq3.Row 
        cursor = conn.cursor()
        partides_raw = []
        try:
            # Llegim totes les columnes que necessitarem per reconstruir
            cursor.execute("SELECT * FROM partides")
            partides_raw = cursor.fetchall() # Llista de sqlite3.Row (com diccionaris)
        except sq3.Error as e:
            print(f"Error llegint partides de SQLite: {e}")
        finally:
            conn.close()

        return partides_raw
   
    # llegeix partides i les retornes com chess.geme[]
    def llegeixPartidesAsGames(self):
        # llegeix totes les partides i les transforma en objectes chess.pgn.Game
        partides = self.llegeixPartidesDetallades()
        llista_partides = []
        for partida in partides:
            game = self.transformaPartida(partida)
            llista_partides.append(game)
        return llista_partides

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


    # transforma una partida en un objecte de la llibreria chess
    # retorna un objecte chess.pgn.Game
    # @staticmethod
    def transformaPartida(self, partida_tupla): 
        # Canvio el nom de 'partida' a 'partida_tupla' per claredat
        
        # 1. Construir una cadena PGN completa a partir de les dades
        pgn_string_list = []

        # Afegir capçaleres a la llista de strings
        # (Has d'assegurar-te que els índexs de partida_tupla[] siguin correctes)
        headers_map = {
            # id: partida_tupla[0],
            "White": partida_tupla[1], 
            "WhiteElo": partida_tupla[2],
            "WhiteTitle": partida_tupla[3], 
            "WhiteFideId": partida_tupla[4],
            "Black": partida_tupla[5], 
            "BlackElo": partida_tupla[6], 
            "BlackTitle": partida_tupla[7],
            "BlackFideId": partida_tupla[8], 
            "Event": partida_tupla[9], 
            "Site": partida_tupla[10], 
            "Round": partida_tupla[11],
            "Date": partida_tupla[12], 
            "Result": partida_tupla[13], 
            "ECO": partida_tupla[14],
            "FEN": partida_tupla[15], 
            "Variant": partida_tupla[16], 
            "TimeControl": partida_tupla[17],
            "Opening": partida_tupla[18], 
            "Variation": partida_tupla[19], 
            "Study": partida_tupla[20],
            "Chapter": partida_tupla[21], 
            "Commentator": partida_tupla[22], 
            "NumGame": partida_tupla[23]
            # Afegeix "WhiteTeam", "BlackTeam" si els tens
        }

        for key, value in headers_map.items():
            if value is not None and str(value).strip() != "": # Només afegir si té valor
                # Assegura't que els valors que puguin contenir " es gestionen correctament
                # tot i que python-chess normalment ho fa bé en el parseig.
                pgn_string_list.append(f'[{key} "{str(value)}"]')
        
        pgn_string_list.append("") # Línia buida entre capçaleres i moviments

        # Afegir la cadena de jugades PGN raw
        jugades_pgn_raw = partida_tupla[24]
        pgn_string_list.append(jugades_pgn_raw)

        pgn_completa_string = "\n".join(pgn_string_list)
        
        # print("\nPGN Reconstruït per parsejar:")
        # print(pgn_completa_string) # Útil per depurar

        # 2. Parsejar la cadena PGN completa
        try:
            pgn_file_like_object = io.StringIO(pgn_completa_string)
            game = chess.pgn.read_game(pgn_file_like_object)
            if game is None:
                # Això pot passar si les jugades són completament invàlides
                # o si només hi ha capçaleres sense cap moviment.
                print(f"ADVERTÈNCIA: No s'ha pogut parsejar la partida PGN reconstruïda. PGN:\n{pgn_completa_string[:200]}...")
                # Retornar un objecte Game buit o gestionar l'error 
                game = chess.pgn.Game() # O retornar None i filtrar-ho després
                # Omplir les capçaleres manualment en aquest cas per conservar-les
                for key, value in headers_map.items():
                    if value is not None and str(value).strip() != "":
                        game.headers[key] = str(value)
            return game
        except Exception as e:
            print(f"ERROR parsejant PGN reconstruït: {e}")
            print(f"PGN que va causar l'error:\n{pgn_completa_string[:300]}...")
            # Gestionar aquest error: podem retornar None,
            # un Game buit, o llançar l'excepció més amunt.
            # Per ara, retornem un Game buit amb capçaleres si és possible.
            game_error = chess.pgn.Game()
            for key, value in headers_map.items():
                 if value is not None and str(value).strip() != "":
                     game_error.headers[key] = str(value)
            return game_error

          

####################      M A I N     ############################
#                                                                #
# per a poder fer TESTING d'aquest modul                         #
##################################################################
if __name__=='__main__':
    bd = Bbdd()
    llista_partides = []
    # es un test
    # bd per defecte


    llista_partides = bd.llegeixPartidesAsGames()
    print(llista_partides[0])
    print("Partides llegides: " + str(len(llista_partides)))
    print ("proces acabat amb exit")
