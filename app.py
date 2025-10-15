from flask import Flask, request, jsonify
from flask_cors import CORS
from tinydb import Query
from database import usuarios_table
from routes.empleados_routes import empleados
from routes.contratos_routes import contratos
import threading
import smtplib
import socket
import time
import logging
import random
import datetime

# ------------------- CONFIGURACIÓN BÁSICA -------------------
app = Flask(__name__)
CORS(app)
app.register_blueprint(empleados)
app.register_blueprint(contratos)
logging.basicConfig(level=logging.INFO)

# ------------------- CONFIGURACIÓN DEL CORREO -------------------
SMTP_HOST = 'smtp.example.com'
SMTP_PORT = 587
SMTP_USER = 'user@example.com'
SMTP_PASS = 'supersecret'
FROM_EMAIL = 'no-reply@tu-dominio.com'

# ------------------- FUNCIONES DE CORREO -------------------
def send_recovery_email(correo, codigo):
    """Envía el correo de recuperación en background con reintentos y timeout."""
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            logging.info("Intentando enviar correo a %s (intento %d)", correo, attempt)
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
                smtp.starttls()
                smtp.login(SMTP_USER, SMTP_PASS)
                subject = "Recuperación de contraseña - Molino de Arroz"
                body = f"Tu código de recuperación es: {codigo}. Este código expirará en 10 minutos."
                msg = f"From: Molino <{FROM_EMAIL}>\r\nTo: {correo}\r\nSubject: {subject}\r\n\r\n{body}"
                smtp.sendmail(FROM_EMAIL, [correo], msg)
            logging.info("Correo enviado correctamente a %s", correo)
            return True
        except (smtplib.SMTPException, socket.timeout, ConnectionRefusedError) as e:
            logging.exception("Error enviando correo (intento %d): %s", attempt, e)
            time.sleep(2 ** attempt)
        except Exception as e:
            logging.exception("Error inesperado al enviar correo: %s", e)
            break
    logging.error("No se pudo enviar el correo a %s después de %d intentos", correo, max_retries)
    return False

# ------------------- RUTAS PRINCIPALES -------------------
@app.route('/')
def home():
    return {"message": "Backend SIRH del Molino de Arroz funcionando correctamente ✅"}

# ---------- LOGIN ----------
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    correo = data.get('correo')
    password = data.get('password')

    Usuario = Query()
    user = usuarios_table.get((Usuario.correo == correo) & (Usuario.password == password))

    if user:
        return jsonify({"message": "Login exitoso"}), 200
    return jsonify({"error": "Credenciales incorrectas"}), 401

# ---------- RECUPERACIÓN DE CONTRASEÑA ----------
@app.route('/recuperar', methods=['POST'])
def recuperar():
    data = request.get_json()
    correo = data.get('correo')

    Usuario = Query()
    user = usuarios_table.get(Usuario.correo == correo)

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Generar código temporal de 6 dígitos y expiración
    codigo = str(random.randint(100000, 999999))
    expira_en = (datetime.datetime.now() + datetime.timedelta(minutes=10)).isoformat()

    usuarios_table.update(
        {"codigo_recuperacion": codigo, "expira_en": expira_en},
        Usuario.correo == correo
    )

    # Enviar correo en background
    thread = threading.Thread(target=send_recovery_email, args=(correo, codigo), daemon=True)
    thread.start()

    return jsonify({"message": "Código de recuperación enviado al correo ✅"}), 200

# ---------- VALIDAR CÓDIGO Y CAMBIAR CONTRASEÑA ----------
@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    correo = data.get('correo')
    codigo = data.get('codigo')
    nueva_password = data.get('nueva_password')

    Usuario = Query()
    user = usuarios_table.get(Usuario.correo == correo)

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    if user.get('codigo_recuperacion') != codigo:
        return jsonify({"error": "Código incorrecto"}), 400

    # Verificar que el código no haya expirado
    if user.get('expira_en'):
        expira = datetime.datetime.fromisoformat(user['expira_en'])
        if datetime.datetime.now() > expira:
            return jsonify({"error": "El código ha expirado"}), 400

    # Actualizar contraseña y limpiar código temporal
    usuarios_table.update(
        {"password": nueva_password, "codigo_recuperacion": None, "expira_en": None},
        Usuario.correo == correo
    )

    return jsonify({"message": "Contraseña actualizada correctamente ✅"}), 200

# Ruta de prueba para envío de correo (opcional)
@app.route('/test-mail')
def test_mail():
    try:
        # Se puede probar con el mismo send_recovery_email para consistencia
        thread = threading.Thread(target=send_recovery_email, args=("destinatario@correo.com", "123456"), daemon=True)
        thread.start()
        return {"message": "Correo enviado correctamente ✅"}
    except Exception as e:
        return {"error": str(e)}, 500

# ------------------- EJECUCIÓN -------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
