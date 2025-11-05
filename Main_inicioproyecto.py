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

def get_database():
        with open(BASE_DE_DATOS, "r") as db_file:
            db = json.load(db_file)

        return db
    

def save_database(db):
    with open(BASE_DE_DATOS, "w") as db_file:
        json.dump(db, db_file)



# --------------------- Ventana Principal ---------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("Registro de Usuarios")
        self.ui.lineEdit.setPlaceholderText("Ingrese su nombre")
        self.ui.lineEdit_2.setPlaceholderText("Ingrese su email")
        self.ui.lineEdit_3.setPlaceholderText("Ingrese su documento")
        self.ui.lineEdit_3.setPlaceholderText("Ingrese sus patentes")

        # conectar botón registrar
        self.ui.pushButton.clicked.connect(self.registrar)

    def registrar(self):
        nombre = self.ui.lineEdit.text().strip()
        email = self.ui.lineEdit_2.text().strip()
        documento = self.ui.lineEdit_3.text().strip()

        if not nombre or not email or not documento:
            QMessageBox.warning(self, "Error", "Complete todos los campos.")
            return

        db = get_database()

        # Si el documento ya existe en la base
        if documento in db:
            QMessageBox.information(self, "Usuario existente", 
                                    f"Bienvenido nuevamente, {db[documento]['nombre']}.\n"
                                    "Puede agregar nuevas patentes.")
            self.abrir_ventana_patentes(documento, db[documento]["nombre"])
        else:
            # Si el documento no existe, lo agregamos
            persona = {
                "nombre": nombre,
                "email": email,
                "patentes": []
            }
            db[documento] = persona
            save_database(db)
            QMessageBox.information(self, "Registro exitoso", f"{nombre} fue agregado correctamente.")
            self.abrir_ventana_patentes(documento, nombre)

    def abrir_ventana_patentes(self, dni, nombre):
        self.ventana_patentes = VentanaPatentes(dni, nombre)
        self.ventana_patentes.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
