import serial
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from time import sleep

# ===============================
# CONFIGURACIÓN SERIAL
# ===============================
PUERTO = "COM3"          # Cambiar según tu equipo (ej: "/dev/ttyUSB0" en Linux)
BAUDRATE = 9600
arduino = serial.Serial(PUERTO, BAUDRATE)
sleep(2)

# ===============================
# CONFIGURACIÓN DEL CORREO
# ===============================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
REMITENTE = "tucorreo@gmail.com"           # Cambiar por tu correo
PASSWORD = "tu_contraseña_de_aplicacion"   # Contraseña de aplicación Gmail

# ===============================
# CARGAR BASE DE DATOS
# ===============================
with open("basededatos.json", "r", encoding="utf-8") as f:
    base = json.load(f)

def enviar_email(destinatario, nombre, dni, patente):
    """Envía un correo notificando el paso por el telepeaje INTELIGATE."""
    fecha_hora = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
    asunto = "🚗 Notificación de paso por telepeaje INTELIGATE"
    
    cuerpo = (
        f"Hola {nombre},\n\n"
        f"Se ha registrado el paso de un vehículo a tu nombre por el telepeaje INTELIGATE.\n\n"
        f"📄 Detalles del registro:\n"
        f"   • DNI: {dni}\n"
        f"   • Patente: {patente}\n"
        f"   • Fecha y hora: {fecha_hora}\n\n"
        "Si no reconoces este paso, por favor comunícate con el área de soporte de INTELIGATE.\n\n"
        "Gracias por utilizar nuestro sistema.\n\n"
        "- Equipo INTELIGATE 🚦"
    )

    mensaje = MIMEMultipart()
    mensaje["From"] = REMITENTE
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto
    mensaje.attach(MIMEText(cuerpo, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(REMITENTE, PASSWORD)
            server.send_message(mensaje)
        print(f"[EMAIL] Notificación enviada correctamente a {destinatario}")
    except Exception as e:
        print(f"[ERROR] No se pudo enviar el email a {destinatario}: {e}")

def buscar_usuario_por_patente(patente):
    """Devuelve el usuario (dni, datos) asociado a una patente."""
    for dni, datos in base.items():
        if patente in datos["patentes"]:
            return dni, datos
    return None, None

# ===============================
# BUCLE PRINCIPAL
# ===============================
print("[INTELIGATE] Escuchando accesos desde Arduino...\n")

while True:
    if arduino.in_waiting > 0:
        linea = arduino.readline().decode().strip()

        if linea.startswith("ACCESO:"):
            patente = linea.split(":")[1]
            print(f"[INFO] Acceso detectado para patente: {patente}")

            dni, usuario = buscar_usuario_por_patente(patente)
            if usuario:
                enviar_email(usuario["email"], usuario["nombre"], dni, patente)
                print(f"[OK] Acceso registrado para {usuario['nombre']} (DNI {dni})\n")
            else:
                print("[WARN] Patente no registrada en la base de datos.\n")
