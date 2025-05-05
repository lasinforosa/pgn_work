# src/main.py

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtUiTools import QUiLoader   
# from ui_mainwindow import Ui_MainWindow
import chess
import chess.pgn

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        
        # OPCIO 1:
        # ui convertit a python
        # pyside6-uic main.ui > ui_mainwindow.py
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)

        # OPCIO 2:
        # ui carregat com XML
        self.ui = QUiLoader().load("../ui/main.ui")
        self.setCentralWidget(self.ui)

        # Accions dels botons panell dret
        self.ui.bt_llegirPGN.clicked.connect(self.llegirPGN)
        self.ui.bt_editaPartida.clicked.connect(self.pendent)
        self.ui.bt_EsborraPartida.clicked.connect(self.pendent)
        self.ui.bt_salvaPGN.clicked.connect(self.pendent)
        self.ui.bt_salvaNouPGN.clicked.connect(self.pendent)
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
        self.ui.cb_TitBlanc.setCurrentIndex(0)
        self.ui.le_Negre.clear()
        self.ui.cb_TitNegre.setCurrentIndex(0)
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
        """Obre un diàleg per seleccionar un fitxer PGN i mostra'l al twidgwt"""
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Selecciona un fitxer PGN",
            "../assets/pgn",
            "Fitxers PGN (*.pgn);;Tots els fitxers (*)",
            options=options
        )

        if filename:
            print(f"Llegint fitxer PGN: {filename}")


#-------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    
    