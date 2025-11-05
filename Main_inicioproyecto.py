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

class MainWindow(QMainWindow):  #Clase MainWindow heredada de QMainWindow, que es una clase de PyQt para crear la ventana principal de la app.
    def _init_(self): #constructor method. Se ejuecuta cuando la instancia de la clase es creada.
        super()._init_() #llama al constructor de la clase QMainWindow, para inicializar las funcionalidades básicas de la ventana principal de la app.
        self.ui = Ui_MainWindow() #crea una instancia de Ui_MainWindow class, la cual es la definición de la interfaz del usuario para la ventana principal.
        self.ui.setupUi(self) #llama al método setupUi() de la instancia Ui_MainWindow, para setear los componenetes de la interfaz del usuario dentro de main window.
        uic.loadUi("login.ui", self)
        self.btnLogin.clicked.connect(self.iniciar_sesion)
        
        self.Documentos = "usuarios.json"
        
        if not os.path.exists(self.Documentos):
            with open(self.Documentos, "w") as f:
                json.dump([], f)
 
        self.show()
    def presionar(self):
        print("Pauliii")
        
    def iniciar_sesion(self):
        usuario = self.txtMail.text().strip()
        password = self.txtPass.text().strip()
        doc = self.txtPass.text().strip()
        
        with open(self.Documentos, "r") as f:
            usuarios = json.load(f)
        
        for DNI in Documentos:
            if DNI["documento"] ==  doc:
                self.mostrar_mensaje(f"Bienvenido, {usuario['nombre']} ", "exito")
                # TODO: abrir interfaz principal
                
                return

        self.mostrar_mensaje("DNI inexistente", "error")
    
    def mostrar_mensaje(self, texto, tipo):
        self.lblError.setText(texto)
        if tipo == "error":
            self.lblError.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.lblError.setStyleSheet("color: green; font-weight: bold;")
    
    def presionar():
        print("hola")

    # opcional:
    #def abrir_interfaz_principal(self, nombre):
     #   from interfaz import InterfazPrincipal
      #  self.ventana_principal = InterfazPrincipal(nombre)
       # self.ventana_principal.show()
        #self.close()
    
    
if _name_ == "_main_": #checkea si el script está siendo ejecutado como el prog principal (no importado como un modulo).
    app = QApplication(sys.argv)    # Crea un Qt widget, la cual va ser nuestra ventana.
    window = MainWindow() #crea una intancia de MainWindow 
    window.show()   # IMPORTANT!!!!! la ventanas estan ocultas por defecto.
    sys.exit(app.exec_()) # Start the event loop.