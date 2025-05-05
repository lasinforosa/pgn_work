# src/main.py

import sys
import io
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidget, QHeaderView, QTableWidgetItem
from PySide6.QtCore import Qt, QDate
from PySide6.QtUiTools import QUiLoader   
# from ui_mainwindow import Ui_MainWindow
import chess
import chess.pgn
import sqlite3 as sq

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()

        # Llista per guardar els objectes chess.pgn.Game carregats
        self.loaded_games = []
        
        # OPCIO 1:
        # ui convertit a python
        # pyside6-uic main.ui > ui_mainwindow.py
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)

        # OPCIO 2:
        # ui carregat com XML
        self.ui = QUiLoader().load("../ui/main.ui")
        self.setCentralWidget(self.ui)

        # modifica el table WIdget de les partides
        # self.ui.tb_llistaPartides
        self.tableWidget_Partides = self.ui.tw_LlistaPartides
        # Defineix les columnes que vols mostrar al resum
        self.table_headers = ["Blanc", "Elo B", "t_B", "Negre", "Elo N", "t_N", "Torneig", "Lloc", "Ronda", "Data", "Resultat", "ECO"]
        self.tableWidget_Partides.setColumnCount(len(self.table_headers))
        self.tableWidget_Partides.setHorizontalHeaderLabels(self.table_headers)
        self.tableWidget_Partides.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableWidget_Partides.setSelectionMode(QTableWidget.SingleSelection)
        self.tableWidget_Partides.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget_Partides.verticalHeader().setVisible(False) # Oculta números de fila
        # Ajusta l'amplada de les columnes (exemple: estirar l'última, ajustar les altres)
        header = self.tableWidget_Partides.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(len(self.table_headers) -1, QHeaderView.Stretch) # Estira l'última
        self.tableWidget_Partides.itemSelectionChanged.connect(self.on_game_selected) # <-- Connexió clau

        # Accions dels botons panell dret
        self.ui.bt_nouPGN.clicked.connect(self.crea_PGN)
        self.ui.bt_llegirPGN.clicked.connect(self.llegirPGN)
        self.ui.bt_editaPartida.clicked.connect(self.pendent)
        self.ui.bt_EsborraPartida.clicked.connect(self.pendent)
        self.ui.bt_salvaPGN.clicked.connect(self.save_as_PGN)
        self.ui.bt_salvaSQ3.clicked.connect(self.save_as_sqlite)
        self.ui.bt_Filtres.clicked.connect(self.pendent)
        self.ui.bt_Sortir.clicked.connect(self.close)

        # Accions dels botons panell esquerra
        self.ui.bt_B.clicked.connect(self.cercarJugBlanc)
        self.ui.bt_N.clicked.connect(self.cercarJufNegre)

        self.ui.bt_substituir.clicked.connect(self.pendent)
        self.ui.bt_SalvaNova.clicked.connect(self.pendent)
        self.ui.bt_Neteja.clicked.connect(self.netejaCamps)

    def pendent(self):
        pass

    def netejaCamps(self):
        self.ui.le_Blanc.clear()
        self.ui.cb_titBlanc.setCurrentIndex(0)
        self.ui.le_Negre.clear()
        self.ui.cb_titNegre.setCurrentIndex(0)
        self.ui.le_EloB.clear()
        self.ui.le_EloN.clear()
        self.ui.le_FIDEB.clear()
        self.ui.le_FIDEN.clear()
        self.ui.le_Torneig.clear()
        self.ui.le_Lloc.clear()
        self.ui.de_Data.clear()
        self.ui.le_Ronda.clear()
        self.ui.cb_Resultat.setCurrentIndex(0)  
        self.ui.le_FEN.clear() 
        self.ui.cb_Variant.setCurrentIndex(0)  
        self.ui.le_Ritme.clear()
        self.ui.le_ECO.clear()
        self.ui.le_Obertura.clear()
        self.ui.le_Variacio.clear()
        self.ui.le_Estudi.clear()
        self.ui.le_Capitol.clear()
        self.ui.le_Comentarista.clear()
        self.ui.le_numPartida.clear()

    # cercar jugador a la BBDD
    # i carregar les dades al formulari
    def cercarJugBlanc(self):
        self.cercarJugador("blanc")
    def cercarJufNegre(self):
        self.cercarJugador("negre")
    def cercarJugador(self, color):
        pass

    # llegir un fitxer PGN
    def llegirPGN(self):
        """Obre diàleg per seleccionar PGN, llegeix totes les partides i pobla la taula."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Obre Fitxer PGN", "", "Fitxers PGN (*.pgn);;Tots els fitxers (*)")
        if not file_path:
            return # L'usuari ha cancel·lat

        self.loaded_games = [] # Buida la llista de partides anteriors
        self.tableWidget_Partides.setRowCount(0) # Buida la taula
        self.ui.te_PGN.clear() # Buida el visor de jugades
        self.netejaCamps() # Buida els camps de detall

        try:
            # Important especificar encoding, utf-8 és comú, però pot variar.
            # errors='ignore' o 'replace' pot ajudar amb caràcters invàlids.
            with open(file_path, 'r', encoding='utf-8', errors='replace') as pgn_file:
                while True:
                    # Llegeix la següent partida. Pot aixecar excepcions si el PGN té errors greus.
                    game = chess.pgn.read_game(pgn_file)
                    # print(f"Llegint partida: {game}") # Missatge a consola o status bar
                    if game is None:
                        break # Fi del fitxer

                    self.loaded_games.append(game) # Guarda l'objecte sencer

                    # Afegeix fila a la taula amb les capçaleres seleccionades
                    row_position = self.tableWidget_Partides.rowCount()
                    self.tableWidget_Partides.insertRow(row_position)

                    self.headers = game.headers
                    # Accedeix a les capçaleres de forma segura amb .get()
                    data_row = [
                        self.headers.get("White", "?"),
                        self.headers.get("WhiteElo", "-"),
                        self.headers.get("WhiteTitle", "?"), 
                        self.headers.get("Black", "?"),
                        self.headers.get("BlackElo", "-"),
                        self.headers.get("BlackTitle", "?"),
                        self.headers.get("Event", "?"),
                        self.headers.get("Site", "?"),
                        self.headers.get("Round", "?"),
                        self.headers.get("Date", "????.??.??").replace('.', '/'), # Formata data si cal
                        self.headers.get("Result", "*"),
                        self.headers.get("ECO", "-")
                    ]

                    for col, data in enumerate(data_row):
                         item = QTableWidgetItem(str(data)) # Assegura't que sigui string
                         self.tableWidget_Partides.setItem(row_position, col, item)

            # Ajusta l'amplada de les columnes al contingut després de carregar
            # self.tableWidget_Partides.resizeColumnsToContents()
            print(f"Carregades {len(self.loaded_games)} partides.") # Missatge a consola o status bar

        except Exception as e:
            # Mostra un error a l'usuari (millor amb QMessageBox)
            print(f"Error llegint el fitxer PGN: {e}")
            self.ui.te_PGN.setPlainText(f"Error llegint el fitxer PGN:\n{e}")


    def on_game_selected(self):
        """Slot cridat quan la selecció a la taula canvia."""
        selected_rows = self.tableWidget_Partides.selectionModel().selectedRows()
        if not selected_rows:
            # No hi ha cap fila seleccionada (p.ex., després de buidar la taula)
            self.ui.te_PGN.clear()
            self.netejaCamps()
            return

        selected_row_index = selected_rows[0].row() # Obtenir l'índex de la fila

        if 0 <= selected_row_index < len(self.loaded_games):
            # Obtenir la partida corresponent de la nostra llista
            selected_game = self.loaded_games[selected_row_index]

            # 1. Mostrar les jugades al QTextEdit (zona verda)
            self.mostra_jugades_partida(selected_game)

            # 2. Poblar els camps de detall (zona taronja)
            self.pobla_camps_detall(selected_game.headers)
        else:
             print(f"Índex de fila seleccionat ({selected_row_index}) fora de rang.")


    def obtenir_jugades_txt(self, game):
        """
        Obté només el text de les jugades (i resultat) usant StringExporter
        sense capçaleres.
        """
        # Crear un exportador que NO inclogui capçaleres
        # Pots afegir comments=False, variations=False si tampoc els vols
        exporter = chess.pgn.StringExporter(headers=False, comments=True, variations=True)

        # Aplicar l'exportador al joc
        moves_string = game.accept(exporter)

        # L'exportador pot deixar salts de línia. Els normalitzem a espais.
        # " ".join(moves_string.split()) és un bon truc per normalitzar espais en blanc
        moves_string_net = " ".join(moves_string.split())

        return moves_string_net.strip() # Assegurem que no hi hagi espais al principi/final
    

    def mostra_jugades_partida(self, game):
        """Formata i mostra les jugades de la partida donada al QTextEdit."""
        if not game:
            self.ui.te_PGN.clear()
            return

        board = game.board() # Tauler inicial (pot tenir FEN)
        moves_text = ""
        move_number = board.fullmove_number if board.turn == chess.WHITE else board.fullmove_number
        first_move = True

        # Iterem sobre els nodes per poder gestionar variacions si calgués en el futur
        # Per ara, només la línia principal game.mainline_moves()
        # Nota: game.mainline() retorna nodes, game.mainline_moves() retorna moviments
        for i, move in enumerate(game.mainline_moves()):
            san_move = ""
            try:
                 # És crucial tenir el tauler en l'estat correcte *abans* de demanar el SAN
                 san_move = board.san(move)
            except ValueError:
                 # Pot passar si la partida PGN té moviments il·legals.
                 # Usem la notació UCI com a fallback.
                 san_move = board.uci(move) + "?" # Indiquem que és UCI
            except Exception as e:
                 print(f"Error obtenint SAN per {move.uci()}: {e}")
                 san_move = move.uci() + "!" # Indiquem error

            move_str = ""
            if board.turn == chess.WHITE:
                # Afegir número de jugada per les blanques
                 move_str = f"{move_number}. {san_move}"
            else:
                # Afegir només moviment per les negres (després de les blanques)
                # Si la partida comença amb negres (cas rar), el número va amb '...'
                if first_move and game.board().turn == chess.BLACK:
                    move_str = f"{move_number}... {san_move}"
                else:
                    move_str = san_move
                move_number += 1 # Incrementa número després de jugada negra

            moves_text += move_str + " " # Afegir espai entre jugades
            first_move = False

            # Important: Aplicar el moviment DESPRÉS d'obtenir el SAN
            board.push(move)

        # Afegir el resultat al final
        result = game.headers.get("Result", "*")
        moves_text = moves_text.strip() # Treure espais sobrants
        moves_text += f" {result}"

        self.ui.te_PGN.setPlainText(moves_text)

    def pobla_camps_detall(self, headers):
        """Omple els QLineEdit i altres widgets de la zona taronja amb les capçaleres."""
        self.ui.le_Blanc.setText(headers.get("White", ""))
        self.ui.le_Negre.setText(headers.get("Black", ""))
        self.ui.le_EloB.setText(headers.get("WhiteElo", ""))
        self.ui.le_EloN.setText(headers.get("BlackElo", ""))
        self.ui.cb_titBlanc.setCurrentText(headers.get("WhiteTitle", "*")) 
        self.ui.cb_titNegre.setCurrentText(headers.get("BlackTitle", "*"))
        self.ui.le_FIDEB.setText(headers.get("WhiteFideId", ""))
        self.ui.le_FIDEN.setText(headers.get("BlackFideId", ""))
        self.ui.le_Torneig.setText(headers.get("Event", ""))
        self.ui.le_Lloc.setText(headers.get("Site", ""))

        # Tractament especial per la data
        date_str = headers.get("Date", "????.??.??").replace('.', '-') # Posa format YYYY-MM-DD si és possible
        try:
            # Intenta convertir a QDate (necessita format yyyy-MM-dd)
            # Si la data PGN és només YYYY, o YYYY.MM, això fallarà
            # Hauries de parsejar manualment si els formats són inconsistents
            # Exemple simple: agafar els primers 10 caràcters
             qdate = QDate.fromString(date_str[:10], "yyyy-MM-dd")
             if qdate.isValid():
                 self.ui.de_Data.setDate(qdate)
             else:
                  self.ui.de_Data.setDate(QDate(2000,1,1)) # Data per defecte si falla
                  print(f"Data no reconeguda: {date_str}")
        except Exception:
             self.ui.de_Data.setDate(QDate(2000,1,1)) # Data per defecte

        self.ui.le_Ronda.setText(headers.get("Round", ""))
        # Per ComboBox de Resultat:
        self.ui.cb_Resultat.setCurrentText(headers.get("Result", "*")) # "1-0", "0-1", "1/2-1/2", "*"
        self.ui.le_FEN.setText(headers.get("FEN", "")) # Pot ser buit si és posició inicial estàndard
        self.ui.cb_Variant.setCurrentText(headers.get("Variant", ""))
        self.ui.le_Ritme.setText(headers.get("TimeControl", ""))
        self.ui.le_ECO.setText(headers.get("ECO", ""))
        self.ui.le_Obertura.setText(headers.get("Opening", ""))
        self.ui.le_Variacio.setText(headers.get("Variation", ""))
        self.ui.le_Comentarista.setText(headers.get("Annotator", ""))
        self.ui.le_Estudi.setText(headers.get("StudyName", ""))
        self.ui.le_Capitol.setText(headers.get("ChapterName", ""))
        self.ui.le_numPartida.setText(headers.get("SetUp", ""))


    def save_as_PGN(self):
        """Obre diàleg per guardar un fitxer PGN amb les partides carregades."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Desa Fitxer PGN", "", "Fitxers PGN (*.pgn);;Tots els fitxers (*)")
        if not file_path:
            return
        if not file_path.endswith(".pgn"):
            file_path += ".pgn"
        try:
            with open(file_path, 'w', encoding='utf-8') as pgn_file:
                for game in self.loaded_games:
                    # Escriu la partida al fitxer
                    pgn_file.write(str(game) + "\n\n") # Afegir dues línies per separar partides
            print(f"Partides desades a {file_path}")
        except Exception as e:
            print(f"Error desant el fitxer PGN: {e}")
            self.ui.te_PGN.setPlainText(f"Error desant el fitxer PGN:\n{e}")


    def crea_PGN(self):
        """Crea un nou fitxer PGN."""
        """Obre diàleg per guardar un fitxer PGN amb les partides carregades."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Crea Fitxer PGN", "", "Fitxers PGN (*.pgn);;Tots els fitxers (*)")
        if not file_path:
            return
        if not file_path.endswith(".pgn"):
            file_path += ".pgn"
        try:
            with open(file_path, 'w', encoding='utf-8') as pgn_file:
                pgn_file.write("")
        except Exception as e:
            print(f"Error creant el fitxer PGN: {e}")
            self.ui.te_PGN.setPlainText(f"Error creant el fitxer PGN:\n{e}")  


    def save_as_sqlite(self):
        """Obre diàleg per guardar un fitxer SQLite amb les partides carregades."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Desa Fitxer SQLite", "", "Fitxers SQLite (*.db);;Tots els fitxers (*)")
        if not file_path:
            return
        if not file_path.endswith(".db"):
            file_path += ".db"
        try:
            # Connexió a la base de dades SQLite
            conn = sq.connect(file_path)
            cursor = conn.cursor()

            # Crea la taula si no existeix
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS partides (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    blanc TEXT,
                    elo_blanques TEXT,
                    titol_blanc TEXT,
                    fide_id_blanc TEXT,
                    negre TEXT,
                    elo_negres TEXT,
                    titol_negre TEXT,
                    fide_id_negre TEXT,
                    torneig TEXT,
                    lloc TEXT,
                    ronda TEXT,
                    data TEXT,
                    resultat TEXT,
                    eco TEXT,
                    fen TEXT,
                    variant TEXT,
                    ritme TEXT,
                    obertura TEXT,
                    variacio TEXT,
                    estudi TEXT,
                    capitol TEXT,
                    comentarista TEXT,
                    num_partida TEXT,
                    jugades TEXT
                )
            ''')

            # Insereix les partides carregades
            for game in self.loaded_games:
                headers = game.headers
                pgn_game = self.obtenir_jugades_txt(game)
                cursor.execute('''
                    INSERT INTO partides (blanc, elo_blanques, titol_blanc, fide_id_blanc,
                                negre, elo_negres, titol_negre, fide_id_negre, 
                                torneig, lloc, ronda, data, resultat, eco,
                                fen, variant, ritme, obertura, variacio,
                                estudi, capitol, comentarista, num_partida, jugades)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    headers.get("White", ""),
                    headers.get("WhiteElo", ""),
                    headers.get("WhiteTitle", ""),
                    headers.get("WhiteFideId", ""),
                    headers.get("Black", ""),
                    headers.get("BlackElo", ""),
                    headers.get("BlackTitle", ""),
                    headers.get("BlackFideId", ""),
                    headers.get("Event", ""),
                    headers.get("Site", ""),
                    headers.get("Round", ""),
                    headers.get("Date", ""),
                    headers.get("Result", ""),
                    headers.get("ECO", ""),
                    headers.get("FEN", ""),
                    headers.get("Variant", ""),
                    headers.get("TimeControl", ""),
                    headers.get("Opening", ""),
                    headers.get("Variation", ""),
                    headers.get("StudyName", ""),
                    headers.get("ChapterName", ""),
                    headers.get("Annotator", ""),
                    headers.get("SetUp", ""),
                    pgn_game
                ))

            # Guarda els canvis i tanca la connexió
            conn.commit()
            conn.close()
            print(f"Partides desades a {file_path}")
        except Exception as e:
            print(f"Error desant el fitxer SQLite: {e}")
            self.ui.te_PGN.setPlainText(f"Error desant el fitxer SQLite:\n{e}")  

#-------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    
    