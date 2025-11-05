import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import json
import os
from PyQt6 import uic
from PyQt6.QtGui import QColor

"""
from Archivo convertido con pyside2-uic archivo.ui > interfaz.py
import nombself.ui.label_2.setPixmap(QPixmap("tux.jpg")) #carga la imagen en el label_2re de la clase del archivo convertido
"""
from ui_proyecto import Ui_MainWindow

BASE_DE_DATOS = "./basededatos.json"


class MainWindow(QMainWindow):  #Clase MainWindow heredada de QMainWindow, que es una clase de PyQt para crear la ventana principal de la app.
    def __init__(self): #constructor method. Se ejuecuta cuando la instancia de la clase es creada.
        super().__init__() #llama al constructor de la clase QMainWindow, para inicializar las funcionalidades básicas de la ventana principal de la app.
        self.ui = Ui_MainWindow() #crea una instancia de Ui_MainWindow class, la cual es la definición de la interfaz del usuario para la ventana principal.
        self.ui.setupUi(self) #llama al método setupUi() de la instancia Ui_MainWindow, para setear los componenetes de la interfaz del usuario dentro de main window.
        self.show()
        self.lineEdit.setPlaceholderText("Ingrese su nombre")
        self.lineEdit_2.setPlaceholderText("ingrese su email")
        self.lineEdit_3.setPlaceholderText("Ingrese su documento")

    def get_database():
        with open(BASE_DE_DATOS, "r") as db_file:
            db = json.loads(db_file)

        return db
    

    def save_database(db):
        with open(BASE_DE_DATOS, "w") as db_file:
            json.dump(db)

        
    def registrar(self):
        nombre = self.txtNombre.text().strip()
        email = self.txtMail.text().strip()
        documento = self.txtPass.text().strip()

        db = get_database()

        documentos = db.keys

        if documento in documentos:
            print("ERROR")

        persona = {
            "nombre": nombre,
            "email": email,
            "patentes": []
        }

        db[documento] = persona

        save_database(db)
        
        self.mostrar_mensaje("Cuenta creada con éxito ", "exito")
    
    

    # opcional:
    #def abrir_interfaz_principal(self, nombre):
     #   from interfaz import InterfazPrincipal
      #  self.ventana_principal = InterfazPrincipal(nombre)
       # self.ventana_principal.show()
        #self.close()
    
    
if __name__ == "__main__": #checkea si el script está siendo ejecutado como el prog principal (no importado como un modulo).
    app = QApplication(sys.argv)    # Crea un Qt widget, la cual va ser nuestra ventana.
    window = MainWindow() #crea una intancia de MainWindow 
    window.show()   # IMPORTANT!!!!! la ventanas estan ocultas por defecto.
    sys.exit(app.exec_()) # Start the event loop.