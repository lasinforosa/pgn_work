# src/main.py

import sys
from PySide6.QtWidgets import QApplication, QMainWindow 
from PySide6.QtUiTools import QUiLoader   
# from ui_mainwindow import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.init_ui()
       
        # OPCIO 1:
        # ui convertit a python
        # pyside6-uic main.ui > ui_mainwindow.py
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)

        # OPCIO 2:
        # ui carregat com XML
        self.ui = QUiLoader().load("../ui/main.ui")
        self.setCentralWidget(self.ui)

    def init_ui(self):
        pass


#-------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    
    