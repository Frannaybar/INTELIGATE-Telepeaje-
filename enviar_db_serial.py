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
PUERTO = "COM3"          # Asegúrate que sea el correcto
BAUDRATE = 9600

try:
    arduino = serial.Serial(PUERTO, BAUDRATE, timeout=1)
    sleep(2) # Esperar reinicio de Arduino
    print(f"[CONECTADO] Arduino en {PUERTO}")
except Exception as e:
    print(f"[ERROR] No se pudo conectar al Arduino: {e}")
    exit()

# ===============================
# CONFIGURACIÓN DEL CORREO
# ===============================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
REMITENTE = "tucorreo@gmail.com"
PASSWORD = "tu_contraseña_app"
ADMIN_EMAIL = "inteligatex@gmail.com"

# ===============================
# BASE DE DATOS
# ===============================
ARCHIVO_DB = "basededatos.json"

def cargar_base_datos():
    try:
        with open(ARCHIVO_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[ERROR] No se encontró el archivo basededatos.json")
        return {}

# Cargar DB al inicio
base = cargar_base_datos()

# ===============================
# FUNCIONES EMAIL
# ===============================
def enviar_emails_notificacion(usuario, dni, patente):
    """Envía correos al usuario y al admin"""
    fecha_hora = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
    
    # 1. Email al Usuario
    try:
        msg = MIMEMultipart()
        msg["From"] = REMITENTE
        msg["To"] = usuario["email"]
        msg["Subject"] = "🚗 Paso registrado - INTELIGATE"
        
        cuerpo_usuario = f"""Hola {usuario['nombre']},
        Se registró un acceso con tu vehículo.
        • Patente: {patente}
        • Fecha: {fecha_hora}
        """
        msg.attach(MIMEText(cuerpo_usuario, "plain"))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(REMITENTE, PASSWORD)
            server.send_message(msg)
        print(f"[EMAIL] Enviado a usuario: {usuario['email']}")
    except Exception as e:
        print(f"[EMAIL ERROR] Usuario: {e}")

    # 2. Email al Admin (Opcional, simplificado para no bloquear)
    # (Puedes duplicar la lógica anterior aquí si deseas enviar al admin)

# ===============================
# LÓGICA PRINCIPAL
# ===============================

def procesar_solicitud(dni_recibido):
    """Busca el DNI en el JSON y responde al Arduino"""
    dni_recibido = dni_recibido.strip()
    print(f"[SOLICITUD] Verificando DNI: {dni_recibido}")

    # Recargar DB por si hubo cambios en caliente (opcional)
    # base = cargar_base_datos() 

    if dni_recibido in base:
        usuario = base[dni_recibido]
        # Asumimos que tomamos la primera patente registrada
        patente = usuario["patentes"][0] 
        nombre = usuario["nombre"]

        print(f"[OK] Usuario encontrado: {nombre} | Patente: {patente}")
        
        # 1. Responder al Arduino para que abra la barrera
        comando = f"ABRIR:{patente}\n"
        arduino.write(comando.encode())
        
        # 2. Enviar correos
        enviar_emails_notificacion(usuario, dni_recibido, patente)
        
    else:
        print("[DENEGADO] DNI no encontrado en la base de datos.")
        arduino.write(b"DENEGAR\n")

# ===============================
# BUCLE DE ESCUCHA
# ===============================
print("[INTELIGATE] Sistema iniciado. Esperando datos...\n")

while True:
    if arduino.in_waiting > 0:
        try:
            linea = arduino.readline().decode('utf-8', errors='ignore').strip()
            
            # Arduino envía: "VERIFICAR:12345678"
            if linea.startswith("VERIFICAR:"):
                dni = linea.split(":")[1]
                procesar_solicitud(dni)
                
            # Mensajes de debug del Arduino (opcional verlos)
            elif linea: 
                print(f"[ARDUINO] {linea}")
                
        except Exception as e:
            print(f"[ERROR LECTURA] {e}")