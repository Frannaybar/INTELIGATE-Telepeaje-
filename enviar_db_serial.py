import serial          # Manejo del puerto serial para comunicarse con Arduino
import json            # Para leer la base de datos .json
import smtplib         # Para enviar correos mediante SMTP
import re              # Para expresiones regulares (validar patentes)
from email.mime.text import MIMEText          # Construcción del cuerpo del email
from email.mime.multipart import MIMEMultipart # Emails con múltiples partes
from datetime import datetime   # Obtener fecha y hora actual
from time import sleep          # Pausas de espera

# ===============================
# CONFIGURACIÓN SERIAL
# ===============================

PUERTO = "COM3"      # Puerto donde está conectado Arduino
BAUDRATE = 9600      # Velocidad del puerto serial

try:
    arduino = serial.Serial(PUERTO, BAUDRATE, timeout=1)  # Intenta abrir el puerto
    sleep(2)                                              # Espera a que Arduino reinicie
    print(f"[CONECTADO] Arduino en {PUERTO}")             # Mensaje de éxito
except Exception as e:
    print(f"[ERROR] No se pudo conectar al Arduino: {e}") # Mensaje de error
    exit()                                                # Detiene el programa

# ===============================
# CONFIGURACIÓN EMAIL
# ===============================

SMTP_SERVER = "smtp.gmail.com"       # Servidor de Gmail
SMTP_PORT = 587                      # Puerto SMTP 
REMITENTE = "franciscoaybar2110@gmail.com"  # Email que envía mensajes
PASSWORD = "hcnlulbhwcwarzhf"        # Contraseña de aplicación
ADMIN_EMAIL = "inteligatex@gmail.com" # Email del administrador

# ===============================
# BASE DE DATOS
# ===============================

ARCHIVO_DB = "basededatos.json"   # Archivo json con usuarios
usuario_esperando_seleccion = None # Variable global para saber si estamos esperando patente

def cargar_base_datos():
    try:
        with open(ARCHIVO_DB, "r", encoding="utf-8") as f:  # Abre JSON
            return json.load(f)                            # Devuelve contenido
    except FileNotFoundError:
        print("[ERROR] No se encontró el archivo basededatos.json") # Error si no existe
        return {}

base = cargar_base_datos()  # Carga la base de usuarios al iniciar

# ===============================
# LÓGICA DE TARIFAS Y VALIDACIÓN
# ===============================

def calcular_tarifa(patente):
    """
    Valida el formato de la patente y define el precio.
    Retorna (tipo, costo). Si no coincide, retorna (None, None).
    """
    patente = patente.upper().strip()     # Normaliza la patente (mayuscula y guarda el valor)

    # Patente de AUTO: AA123BB
    if re.match(r'^[A-Z]{2}\d{3}[A-Z]{2}$', patente):
        return "Auto", 5000

    # Patente de MOTO: A123ABC
    elif re.match(r'^[A-Z]{1}\d{3}[A-Z]{3}$', patente):
        return "Moto", 3000

    # Formato inválido
    else:
        return None, None

# ===============================
# FUNCIONES DE EMAIL
# ===============================

def enviar_email(destinatario, asunto, cuerpo):
    try:
        msg = MIMEMultipart()            # Crea email multiparte
        msg["From"] = REMITENTE          # Remitente
        msg["To"] = destinatario         # Destinatario
        msg["Subject"] = asunto          # Asunto
        msg.attach(MIMEText(cuerpo, "plain", "utf-8"))  # Texto del email

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server: # Conexión SMTP
            server.starttls()                               # Activa TLS
            server.login(REMITENTE, PASSWORD)               # Login
            server.send_message(msg)                        # Envía email
        print(f"[EMAIL] Enviado a {destinatario}")          # éxito
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")                         # error

def enviar_email_notificacion(usuario, dni, patente, tipo, costo):
    # Genera cuerpo del mail para el usuario
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
    # Mail para el administrador
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
    # Mail de acceso fallido
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
    """Busca usuario por DNI y pide selección de patente."""
    global usuario_esperando_seleccion
    dni = dni.strip()    # Limpia espacios
    print(f"\n[SOLICITUD] Verificando DNI: {dni}")

    if dni in base:      # Si el DNI existe en la base
        usuario = base[dni]
        patentes = usuario["patentes"]
        usuario_esperando_seleccion = {"dni": dni, "usuario": usuario} # Guarda usuario temporal

        # Imprime opciones en consola
        print("\n" + "="*40)
        print(f"  USUARIO: {usuario['nombre']}")
        print("  SELECCIONAR VEHÍCULO:")
        print("="*40)
        
        for i, pat in enumerate(patentes):  # Recorre patentes del usuario
            tipo, costo = calcular_tarifa(pat)
            if tipo:
                print(f"  [{i+1}] {pat} ({tipo} - ${costo})")
            else:
                print(f"  [{i+1}] {pat} [FORMATO INVÁLIDO]")
            
        print("="*40 + "\n")

        arduino.write(b"PEDIR_OPCION\n")  # Arduino pide número de selección
        print("-> Esperando selección desde el teclado...")

    else:
        print("[DENEGADO] DNI no encontrado.") # Mensaje de error
        arduino.write(b"DENEGAR\n")            # Arduino cierra acceso
        enviar_email_admin_acceso_denegado(dni) # Notifica al admin
        usuario_esperando_seleccion = None      # Limpia estado

def procesar_seleccion(opcion_str):
    """Procesa el número elegido y autoriza o rechaza el acceso."""
    global usuario_esperando_seleccion

    if usuario_esperando_seleccion is None:  # Si se recibe selección sin DNI previo
        print("[ERROR] Selección recibida sin usuario.")
        arduino.write(b"DENEGAR\n")
        return

    try:
        indice = int(opcion_str) - 1     # Convierte opción a índice
        usuario = usuario_esperando_seleccion["usuario"]
        patentes = usuario["patentes"]

        # Valida si la opción existe
        if 0 <= indice < len(patentes):
            patente = patentes[indice]   # Obtiene patente seleccionada
            tipo, costo = calcular_tarifa(patente)

            if tipo is None:
                # Si la patente es inválida
                print(f"[ERROR] La patente {patente} tiene un formato inválido.")
                arduino.write(b"DENEGAR\n")
                enviar_email_admin_acceso_denegado(patente, "Formato de patente inválido")

            else:
                print(f"[SELECCIONADO] {patente} -> {tipo} (${costo})")
                arduino.write(f"ABRIR:{patente}\n".encode())  # Arduino abre barrera

                # Notificaciones por email
                enviar_email_notificacion(usuario, usuario_esperando_seleccion["dni"], patente, tipo, costo)
                enviar_email_admin_acceso_ok(usuario, usuario_esperando_seleccion["dni"], patente, tipo, costo)

        else:
            print("[ERROR] Opción inválida.") # Si se elige un número inexistente
            arduino.write(b"DENEGAR\n")

    except ValueError:
        print("[ERROR] Opción no numérica.")  # Si mandan letra u otra cosa
        arduino.write(b"DENEGAR\n")

    usuario_esperando_seleccion = None      # Limpia estado
    print("\n[LISTO] Esperando próximo vehículo...\n")

# ===============================
# BUCLE PRINCIPAL
# ===============================

print("[INTELIGATE] Sistema iniciado. Esperando Arduino...\n")

while True:
    if arduino.in_waiting > 0:               # Si Arduino envió algo
        try:
            linea = arduino.readline().decode('utf-8', errors='ignore').strip()  # Lee comando

            # Recibe DNI desde Arduino
            if linea.startswith("VERIFICAR:"):
                procesar_dni(linea.split(":")[1])

            # Recibe número de opción
            elif linea.startswith("SELECCION:"):
                procesar_seleccion(linea.split(":")[1])

            # Emergencia desde Arduino
            elif linea == "EMERGENCIA":
                print("\n\n!!! 🚨 ¡ALERTA DE EMERGENCIA! Botón presionado. 🚨 !!!\n")

            # Tecla presionada (privacidad)
            elif linea == "TECLA_PULSADA":
                print("*", end="", flush=True)   # Muestra asterisco

            # Mensajes genéricos
            elif linea:
                print(f"[ARDUINO] {linea}")

        except Exception as e:
            print(f"[ERROR LECTURA] {e}")  # Error leyendo serial
