import sys
import json
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QMessageBox, QVBoxLayout,
    QLabel, QLineEdit, QPushButton
)
from PySide6.QtGui import QPixmap
from ui_proyecto import Ui_MainWindow

BASE_DE_DATOS = "./basededatos.json"

def get_database():
    if not os.path.exists(BASE_DE_DATOS):
        with open(BASE_DE_DATOS, "w") as f:
            json.dump({}, f)
    with open(BASE_DE_DATOS, "r") as db_file:
        return json.load(db_file)

def save_database(db):
    with open(BASE_DE_DATOS, "w") as db_file:
        json.dump(db, db_file, indent=4)


# --------------------- Ventana para agregar patentes ---------------------
class VentanaPatentes(QWidget):
    def __init__(self, dni, nombre):
        super().__init__()
        self.dni = dni
        self.nombre = nombre
        self.setWindowTitle(f"Agregar Patentes - {nombre}")
        self.setGeometry(200, 200, 400, 200)

        layout = QVBoxLayout()

        self.label_info = QLabel(f"Agregar patente para {nombre} (DNI: {dni})")
        self.input_patente = QLineEdit()
        self.input_patente.setPlaceholderText("Ingrese nueva patente")

        self.boton_agregar = QPushButton("Agregar Patente")
        self.boton_agregar.clicked.connect(self.agregar_patente)

        layout.addWidget(self.label_info)
        layout.addWidget(self.input_patente)
        layout.addWidget(self.boton_agregar)

        self.setLayout(layout)

    def agregar_patente(self):
        patente = self.input_patente.text().strip().upper()
        if not patente:
            QMessageBox.warning(self, "Error", "Debe ingresar una patente válida.")
            return

        db = get_database()

        if patente in [p for d in db.values() for p in d["patentes"]]:
            QMessageBox.warning(self, "Error", "Esa patente ya está registrada a otra persona.")
            return

        db[self.dni]["patentes"].append(patente)
        save_database(db)

        QMessageBox.information(self, "Éxito", f"Patente {patente} agregada correctamente.")
        self.input_patente.clear()


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
        self.ui.lineEdit_4.setPlaceholderText("Ingrese sus patentes")

        self.ui.label.setPixmap(QPixmap("inteligate.jpeg"))


        # conectar botón registrar
        self.ui.btnregistrar.clicked.connect(self.registrar)

    def registrar(self):
        nombre = self.ui.lineEdit.text().strip()
        email = self.ui.lineEdit_2.text().strip()
        documento = self.ui.lineEdit_3.text().strip()
        patentes = self.ui.lineEdit_4.text().strip()

        if not nombre or not email or not documento or not patentes:
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
                "patentes": [patentes]
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
