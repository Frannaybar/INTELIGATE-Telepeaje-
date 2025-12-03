import serial
import json
import smtplib
import re  # Importante para validar formatos
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
# LÓGICA DE TARIFAS Y VALIDACIÓN
# ===============================

def calcular_tarifa(patente):
    """
    Analiza el formato de la patente.
    Retorna (Tipo, Precio).
    Si el formato es inválido, retorna (None, None).
    """
    patente = patente.upper().strip()
    
    # Regex para AUTO (AA123BB): 2 Letras + 3 Números + 2 Letras
    if re.match(r'^[A-Z]{2}\d{3}[A-Z]{2}$', patente):
        return "Auto", 5000
        
    # Regex para MOTO (A123ABC): 1 Letra + 3 Números + 3 Letras
    elif re.match(r'^[A-Z]{1}\d{3}[A-Z]{3}$', patente):
        return "Moto", 3000
    
    # Si no coincide con ninguno, es inválido
    else:
        return None, None

# ===============================
# FUNCIONES DE EMAIL
# ===============================

def enviar_email(destinatario, asunto, cuerpo):
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

def enviar_email_notificacion(usuario, dni, patente, tipo, costo):
    cuerpo = f"""
Hola {usuario['nombre']},
Se registró un acceso con tu vehículo.

DETALLES:
-------------------------
• Patente: {patente}
• Tipo: {tipo}
• Costo: ${costo}
• Fecha: {datetime.now().strftime("%d/%m/%Y - %H:%M:%S")}
"""
    enviar_email(usuario["email"], f"🚗 Paso registrado - {tipo}", cuerpo)

def enviar_email_admin_acceso_ok(usuario, dni, patente, tipo, costo):
    cuerpo = f"""
ACCESO AUTORIZADO
========================
Nombre: {usuario['nombre']}
DNI: {dni}
Patente: {patente}
Vehículo: {tipo}
Cobrado: ${costo}
"""
    enviar_email(ADMIN_EMAIL, "✔ ACCESO AUTORIZADO", cuerpo)

def enviar_email_admin_acceso_denegado(dni_erroneo, motivo="DNI no registrado"):
    cuerpo = f"""
ACCESO DENEGADO
========================
ID/DNI: {dni_erroneo}
Motivo: {motivo}
Fecha: {datetime.now().strftime("%d/%m/%Y - %H:%M:%S")}
"""
    enviar_email(ADMIN_EMAIL, "❌ ACCESO DENEGADO", cuerpo)

# ===============================
# FUNCIONES PRINCIPALES
# ===============================

def procesar_dni(dni):
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
        
        # Mostrar opciones validando formato visualmente
        for i, pat in enumerate(patentes):
            tipo, costo = calcular_tarifa(pat)
            if tipo:
                print(f"  [{i+1}] {pat} ({tipo} - ${costo})")
            else:
                print(f"  [{i+1}] {pat} [FORMATO INVÁLIDO]")
            
        print("="*40 + "\n")
        arduino.write(b"PEDIR_OPCION\n")

    else:
        print("[DENEGADO] DNI no encontrado.")
        arduino.write(b"DENEGAR\n")
        enviar_email_admin_acceso_denegado(dni)
        usuario_esperando_seleccion = None

def procesar_seleccion(opcion_str):
    global usuario_esperando_seleccion

    if usuario_esperando_seleccion is None:
        arduino.write(b"DENEGAR\n")
        return

    try:
        indice = int(opcion_str) - 1
        usuario = usuario_esperando_seleccion["usuario"]
        patentes = usuario["patentes"]

        if 0 <= indice < len(patentes):
            patente = patentes[indice]
            
            # 1. VALIDAR PATENTE ANTES DE ABRIR
            tipo, costo = calcular_tarifa(patente)
            
            if tipo is None:
                # Si el formato es inválido, denegamos el acceso
                print(f"[ERROR] La patente {patente} tiene un formato inválido.")
                arduino.write(b"DENEGAR\n")
                enviar_email_admin_acceso_denegado(patente, "Formato de patente inválido")
            else:
                # Si es válido, abrimos
                print(f"[SELECCIONADO] {patente} -> {tipo} (${costo})")
                arduino.write(f"ABRIR:{patente}\n".encode())
                
                enviar_email_notificacion(usuario, usuario_esperando_seleccion["dni"], patente, tipo, costo)
                enviar_email_admin_acceso_ok(usuario, usuario_esperando_seleccion["dni"], patente, tipo, costo)

        else:
            print("[ERROR] Opción inválida.")
            arduino.write(b"DENEGAR\n")

    except ValueError:
        print("[ERROR] Opción no numérica.")
        arduino.write(b"DENEGAR\n")

    usuario_esperando_seleccion = None

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
        except Exception as e:
            print(f"[ERROR LECTURA] {e}")