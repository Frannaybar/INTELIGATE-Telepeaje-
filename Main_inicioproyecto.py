import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import json
import os
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QMessageBox, QVBoxLayout,
    QLabel, QLineEdit, QPushButton,
)
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

        # verificar que la patente no esté registrada en otra persona
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
        self.ui.lineEdit_4.setPlaceholderText("Ingrese las patentes separadas por comas o espacios")

        # Cargar logos
        self.ui.label.setPixmap(QPixmap("inteligate.jpeg"))
        self.ui.label_2.setPixmap(QPixmap("inteligate.jpeg"))
        self.ui.label_3.setPixmap(QPixmap("inteligate.jpeg"))
        self.ui.label_4.setPixmap(QPixmap("inteligate.jpeg"))

        
    def registrar(self):
        nombre = self.ui.lineEdit.text().strip()
        email = self.ui.lineEdit_2.text().strip()
        documento = self.ui.lineEdit_3.text().strip()
        patentes_texto = self.ui.lineEdit_4.text().strip()

        # ---------------- VALIDACIONES NUEVAS ---------------- #
        # Validar campos vacíos
        if not nombre or not email or not documento:
            QMessageBox.warning(self, "Error", "Complete todos los campos obligatorios.")
            return

        # Validar email
        if "@" not in email or email.startswith("@") or email.endswith("@"):
            QMessageBox.warning(self, "Error en Email", "El email ingresado no es válido (debe contener '@').")
            return

        # Validar nombre (no debe contener números)
        if any(char.isdigit() for char in nombre):
            QMessageBox.warning(self, "Error en Nombre", "El nombre no debe contener números.")
            return

        # Validar documento (debe tener 8 dígitos)
        if not documento.isdigit() or len(documento) != 8:
            QMessageBox.warning(self, "Error en DNI", "El DNI debe tener exactamente 8 dígitos numéricos.")
            return
        # ------------------------------------------------------- #

        # Procesar las patentes (separar por coma o espacio)
        patentes = []
        if patentes_texto:
            patentes = [p.strip().upper() for p in patentes_texto.replace(",", " ").split() if p.strip()]

        db = get_database()

        # Si el documento ya existe
        if documento in db:
            QMessageBox.information(self, "Usuario existente",
                                    f"Bienvenido nuevamente, {db[documento]['nombre']}.\n"
                                    "Puede agregar nuevas patentes.")
            self.abrir_ventana_patentes(documento, db[documento]["nombre"])
        else:
            # Si el documento no existe, verificar que las patentes no estén duplicadas
            for p in patentes:
                if p in [x for d in db.values() for x in d["patentes"]]:
                    QMessageBox.warning(self, "Error", f"La patente {p} ya está registrada a otra persona.")
                    return

            # Crear nueva persona
            persona = {
                "nombre": nombre,
                "email": email,
                "patentes": patentes
            }
            db[documento] = persona
            save_database(db)

            # Definir las credenciales
            remitente = "franciscoaybar2110@gmail.com"
            password = "hcnlulbhwcwarzhf"

            # Definir los detalles del destinatario
            destinatario = email
            asunto = "Registro Telepeaje"

            # Crear el mensaje
            mensaje = MIMEMultipart()
            mensaje["From"] = remitente
            mensaje["To"] = destinatario
            mensaje["Subject"] = asunto

            # Agregar cuerpo
            cuerpo = f"su DNI {documento} ha sido registrado a nombre del gmail {email} por INTELIGATE\nAhora usted posee sus patentes {patentes} registradas y puede acceder por todo telepeaje INTELIGATE"
            mensaje.attach(MIMEText(cuerpo, "plain"))

            # Iniciar sesión en servidor SMTP de gmail
            server = smtplib.SMTP("smtp.gmail.com", 587) 
            server.starttls()
            server.login(remitente, password)

            # Enviar Correo
            texto = mensaje.as_string()
            server.sendmail(remitente, destinatario, texto)
            server.quit()
            
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
