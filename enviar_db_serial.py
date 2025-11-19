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
PUERTO = "COM3"
BAUDRATE = 9600

try:
    arduino = serial.Serial(PUERTO, BAUDRATE, timeout=1)
    sleep(2)
    print(f"[CONECTADO] Arduino en {PUERTO}")
except Exception as e:
    print(f"[ERROR] No se pudo conectar al Arduino: {e}")
    exit()

# ===============================
# CONFIGURACIÓN EMAIL
# ===============================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
REMITENTE = "franciscoaybar2110@gmail.com"
PASSWORD = "hcnlulbhwcwarzhf"
ADMIN_EMAIL = "inteligatex@gmail.com"

# ===============================
# BASE DE DATOS
# ===============================
ARCHIVO_DB = "basededatos.json"
usuario_esperando_seleccion = None

def cargar_base_datos():
    try:
        with open(ARCHIVO_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[ERROR] No se encontró el archivo basededatos.json")
        return {}

base = cargar_base_datos()

# ===============================
# FUNCIONES DE EMAIL
# ===============================
def enviar_email(destinatario, asunto, cuerpo):
    """Función genérica para enviar emails"""
    try:
        msg = MIMEMultipart()
        msg["From"] = REMITENTE
        msg["To"] = destinatario
        msg["Subject"] = asunto
        msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(REMITENTE, PASSWORD)
            server.send_message(msg)

        print(f"[EMAIL] Enviado a {destinatario}")

    except Exception as e:
        print(f"[EMAIL ERROR] {e}")

def enviar_email_notificacion(usuario, dni, patente):
    """Email al dueño del auto"""
    cuerpo = f"""
Hola {usuario['nombre']},
Se registró un acceso con tu vehículo.
• Patente: {patente}
• DNI: {dni}
• Fecha: {datetime.now().strftime("%d/%m/%Y - %H:%M:%S")}
"""
    enviar_email(usuario["email"], "🚗 Paso registrado - INTELIGATE", cuerpo)

# ===============================
# NUEVAS FUNCIONES PEDIDAS
# ===============================
def enviar_email_admin_acceso_ok(usuario, dni, patente):
    """Notifica al administrador cuando pasa un auto válido."""
    cuerpo = f"""
ACCESO AUTORIZADO
========================
Nombre: {usuario['nombre']}
DNI: {dni}
Patente: {patente}
Fecha y hora: {datetime.now().strftime("%d/%m/%Y - %H:%M:%S")}
"""
    enviar_email(ADMIN_EMAIL, "✔ ACCESO AUTORIZADO", cuerpo)

def enviar_email_admin_acceso_denegado(dni_erroneo):
    """Notifica al administrador cuando intentan pasar con DNI inválido."""
    cuerpo = f"""
ACCESO DENEGADO
========================
DNI ingresado: {dni_erroneo}
Motivo: No está registrado en la base de datos.
Fecha y hora: {datetime.now().strftime("%d/%m/%Y - %H:%M:%S")}
"""
    enviar_email(ADMIN_EMAIL, "❌ ACCESO DENEGADO", cuerpo)

# ===============================
# FUNCIONES PRINCIPALES
# ===============================
def procesar_dni(dni):
    """Busca el DNI y pide selección si existe."""
    global usuario_esperando_seleccion
    dni = dni.strip()
    print(f"\n[SOLICITUD] Verificando DNI: {dni}")

    if dni in base:
        usuario = base[dni]
        patentes = usuario["patentes"]

        usuario_esperando_seleccion = {"dni": dni, "usuario": usuario}

        print("\n" + "="*40)
        print(f"  USUARIO: {usuario['nombre']}")
        print("  SELECCIONAR VEHÍCULO:")
        print("="*40)
        for i, pat in enumerate(patentes):
            print(f"  [{i+1}] {pat}")
        print("="*40 + "\n")

        arduino.write(b"PEDIR_OPCION\n")
        print("-> Esperando selección desde el teclado...")

    else:
        print("[DENEGADO] DNI no encontrado.")
        arduino.write(b"DENEGAR\n")

        # 🔔 NUEVO: Notificar al administrador
        enviar_email_admin_acceso_denegado(dni)

        usuario_esperando_seleccion = None

def procesar_seleccion(opcion_str):
    """Valida la opción elegida y abre la barrera."""
    global usuario_esperando_seleccion

    if usuario_esperando_seleccion is None:
        print("[ERROR] Selección recibida sin usuario.")
        arduino.write(b"DENEGAR\n")
        return

    try:
        indice = int(opcion_str) - 1
        usuario = usuario_esperando_seleccion["usuario"]
        dni = usuario_esperando_seleccion["dni"]
        patentes = usuario["patentes"]

        if 0 <= indice < len(patentes):
            patente = patentes[indice]
            print(f"[SELECCIONADO] {patente}")
            arduino.write(f"ABRIR:{patente}\n".encode())

            # Email al dueño
            enviar_email_notificacion(usuario, dni, patente)

            # 🔔 NUEVO: Email al administrador
            enviar_email_admin_acceso_ok(usuario, dni, patente)

        else:
            print("[ERROR] Opción inválida.")
            arduino.write(b"DENEGAR\n")

    except ValueError:
        print("[ERROR] Opción no numérica.")
        arduino.write(b"DENEGAR\n")

    usuario_esperando_seleccion = None
    print("\n[LISTO] Esperando próximo vehículo...\n")

# ===============================
# BUCLE PRINCIPAL
# ===============================
print("[INTELIGATE] Sistema iniciado. Esperando Arduino...\n")

while True:
    if arduino.in_waiting > 0:
        try:
            linea = arduino.readline().decode('utf-8', errors='ignore').strip()

            if linea.startswith("VERIFICAR:"):
                procesar_dni(linea.split(":")[1])

            elif linea.startswith("SELECCION:"):
                procesar_seleccion(linea.split(":")[1])

            elif linea:
                print(f"[ARDUINO] {linea}")

        except Exception as e:
            print(f"[ERROR LECTURA] {e}")