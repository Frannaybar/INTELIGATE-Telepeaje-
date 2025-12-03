
from PySide6.QtUiTools import QUiLoader
import random
from datetime import datetime
import urllib.request
import smtplib
import re  # <--- IMPORTADO PARA VALIDAR
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


# --------------------- FUNCION DE VALIDACION (NUEVA) ---------------------
def validar_formato_patente(patente):
    """
    Retorna True si es Auto (AA123BB) o Moto (A123ABC).
    Retorna False si no cumple ninguno.
    """
    patron_auto = r"^[A-Z]{2}\d{3}[A-Z]{2}$"
    patron_moto = r"^[A-Z]{1}\d{3}[A-Z]{3}$"
    
    if re.match(patron_auto, patente) or re.match(patron_moto, patente):
        return True
    return False
# -------------------------------------------------------------------------


# --------------------- Ventana para agregar patentes ---------------------
class VentanaPatentes(QWidget):
    def __init__(self, dni, nombre):
        super().__init__()
        self.dni = dni
        self.nombre = nombre
        self.setWindowTitle(f"Agregar Patentes - {nombre}")
        self.setGeometry(400, 250, 450, 250)

        # --- Diseño visual mejorado ---
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        self.label_titulo = QLabel("🚗 Agregar nuevas patentes")
        self.label_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        self.label_info = QLabel(f"Titular: {nombre} (DNI: {dni})")
        self.label_info.setStyleSheet("color: #34495e; font-size: 14px;")

        self.input_patente = QLineEdit()
        self.input_patente.setPlaceholderText("Ej: AA123BB (Auto) o A123ABC (Moto)")
        self.input_patente.setStyleSheet(
            "padding: 8px; font-size: 14px; border: 1px solid #bdc3c7; border-radius: 6px;"
        )

        self.boton_agregar = QPushButton("Agregar Patentes")
        self.boton_agregar.setStyleSheet(
            "background-color: #2ecc71; color: white; font-weight: bold; padding: 8px; border-radius: 6px;"
        )
        self.boton_agregar.clicked.connect(self.agregar_patente)

        layout.addWidget(self.label_titulo)
        layout.addWidget(self.label_info)
        layout.addWidget(self.input_patente)
        layout.addWidget(self.boton_agregar)

        self.setLayout(layout)

    def agregar_patente(self):
        texto = self.input_patente.text().strip().upper()
        if not texto:
            QMessageBox.warning(self, "Error", "Debe ingresar al menos una patente.")
            return

        # Separar múltiples patentes (coma o espacio)
        nuevas_patentes = [p.strip() for p in texto.replace(",", " ").split() if p.strip()]
        
        # --- VALIDACIÓN DE FORMATO ---
        errores = []
        for p in nuevas_patentes:
            if not validar_formato_patente(p):
                errores.append(p)
        
        if errores:
            QMessageBox.critical(self, "Formato Inválido", 
                f"Las siguientes patentes no son válidas:\n{', '.join(errores)}\n\n"
                "Use formato Auto (AA123BB) o Moto (A123ABC).")
            return
        # -----------------------------

        db = get_database()
        patentes_existentes = [p for d in db.values() for p in d["patentes"]]

        # Verificar duplicadas globales
        duplicadas = [p for p in nuevas_patentes if p in patentes_existentes]
        if duplicadas:
            QMessageBox.warning(
                self,
                "Patentes duplicadas",
                f"Las siguientes patentes ya están registradas:\n{', '.join(duplicadas)}"
            )
            return

        # Agregar las nuevas patentes
        db[self.dni]["patentes"].extend(nuevas_patentes)
        save_database(db)

        QMessageBox.information(
            self,
            "Éxito",
            f"Se agregaron correctamente:\n{', '.join(nuevas_patentes)}"
        )

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
        self.ui.lineEdit_4.setPlaceholderText("Ej: AA123BB, A123ABC")

        # Cargar logos (asegúrate de que la imagen exista)
        self.ui.label.setPixmap(QPixmap("inteligate.jpeg"))

        # Mostrar datos iniciales
        self.actualizar_datos()
        self.actualizar_clima()

    def salir(self):
        self.close()
    
    def actualizar_clima(self):
        try:
            url = (
                "https://api.open-meteo.com/v1/forecast?"
                "latitude=-31.4167&longitude=-64.1833&current=temperature_2m,weather_code"
            )

            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())

            temperatura = data["current"]["temperature_2m"]
            codigo_clima = data["current"]["weather_code"]

            descripcion = self.descripcion_clima(codigo_clima)

            self.ui.lblTemperaturaClima.setText(f"{temperatura} °C")
            self.ui.lblIconoClima.setText(descripcion)

        except Exception as e:
            # Silencioso para no molestar si falla internet
            print(f"Clima error: {e}")

    def descripcion_clima(self, codigo):
        condiciones = {
            0: "Despejado ☀️", 1: "Mayormente despejado 🌤️", 2: "Parcialmente nublado ⛅",
            3: "Nublado ☁️", 45: "Niebla 🌫️", 51: "Llovizna 🌧️", 61: "Lluvia ligera 🌧️",
            63: "Lluvia moderada 🌦️", 65: "Lluvia intensa 🌧️", 80: "Tormentas ⛈️",
        }
        return condiciones.get(codigo, "Desconocido")
    
    def actualizar_datos(self):
        ahora = datetime.now()
        self.ui.lblHora.setText(ahora.strftime("%H:%M:%S"))
        self.ui.lblFecha.setText(ahora.strftime("%d/%m/%Y"))
        
    def registrar(self):
        nombre = self.ui.lineEdit.text().strip()
        email = self.ui.lineEdit_2.text().strip()
        documento = self.ui.lineEdit_3.text().strip()
        patentes_texto = self.ui.lineEdit_4.text().strip()

        # Validar campos vacíos
        if not nombre or not email or not documento:
            QMessageBox.warning(self, "Error", "Complete todos los campos obligatorios.")
            return

        # Validar email
        if "@" not in email or email.startswith("@") or email.endswith("@"):
            QMessageBox.warning(self, "Error en Email", "El email ingresado no es válido.")
            return

        # Validar nombre
        if any(char.isdigit() for char in nombre):
            QMessageBox.warning(self, "Error en Nombre", "El nombre no debe contener números.")
            return

        # Validar documento
        if not documento.isdigit() or len(documento) != 8:
            QMessageBox.warning(self, "Error en DNI", "El DNI debe tener 8 dígitos numéricos.")
            return

        # Procesar patentes
        patentes = []
        if patentes_texto:
            patentes = [p.strip().upper() for p in patentes_texto.replace(",", " ").split() if p.strip()]

        # --- VALIDACIÓN DE FORMATO PATENTE ---
        errores_patente = []
        for p in patentes:
            if not validar_formato_patente(p):
                errores_patente.append(p)
        
        if errores_patente:
            QMessageBox.critical(self, "Patente Inválida", 
                f"Patentes con formato incorrecto:\n{', '.join(errores_patente)}\n\n"
                "Formatos permitidos:\n- Auto: AA123BB\n- Moto: A123ABC")
            return
        # -------------------------------------

        db = get_database()

        if documento in db:
            QMessageBox.information(self, "Usuario existente",
                                    f"Bienvenido nuevamente, {db[documento]['nombre']}.\n"
                                    "Puede agregar nuevas patentes.")
            self.abrir_ventana_patentes(documento, db[documento]["nombre"])
        else:
            for p in patentes:
                if p in [x for d in db.values() for x in d["patentes"]]:
                    QMessageBox.warning(self, "Error", f"La patente {p} ya está registrada.")
                    return

            persona = {
                "nombre": nombre,
                "email": email,
                "patentes": patentes
            }
            db[documento] = persona
            save_database(db)

            # Envío de Emails (Envuelta en Try para que no cierre la app si falla internet)
            try:
                self.enviar_correos_bienvenida(email, nombre, documento, patentes)
            except Exception as e:
                print(f"Error enviando emails: {e}")
                QMessageBox.information(self, "Info", "Usuario registrado, pero falló el envío del email.")

            QMessageBox.information(self, "Registro exitoso", f"{nombre} fue agregado correctamente.")
            self.abrir_ventana_patentes(documento, nombre)

    def enviar_correos_bienvenida(self, email, nombre, documento, patentes):
        remitente = "franciscoaybar2110@gmail.com"
        password = "hcnlulbhwcwarzhf" # Considera usar variables de entorno
        
        # 1. Email al Usuario
        msg_user = MIMEMultipart()
        msg_user["From"] = remitente
        msg_user["To"] = email
        msg_user["Subject"] = "Registro Telepeaje - INTELIGATE"
        cuerpo_user = f"Hola {nombre},\nTu DNI {documento} ha sido registrado.\nPatentes asociadas: {', '.join(patentes)}"
        msg_user.attach(MIMEText(cuerpo_user, "plain"))

        # 2. Email al Admin
        msg_admin = MIMEMultipart()
        msg_admin["From"] = remitente
        msg_admin["To"] = "inteligatex@gmail.com"
        msg_admin["Subject"] = "Nuevo Usuario Registrado"
        cuerpo_admin = f"NUEVO USUARIO\nNombre: {nombre}\nEmail: {email}\nDNI: {documento}\nPatentes: {patentes}"
        msg_admin.attach(MIMEText(cuerpo_admin, "plain"))

        # Enviar ambos en una sola conexión
        server = smtplib.SMTP("smtp.gmail.com", 587) 
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg_user)
        server.send_message(msg_admin)
        server.quit()

    def abrir_ventana_patentes(self, dni, nombre):
        self.ventana_patentes = VentanaPatentes(dni, nombre)
        self.ventana_patentes.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())