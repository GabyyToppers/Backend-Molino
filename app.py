from flask import Flask, request, jsonify
from flask_cors import CORS
from tinydb import Query
from database import usuarios_table
from services.email_service import configurar_mail, enviar_correo
import random
import datetime

# Crear la aplicación Flask
app = Flask(__name__)
CORS(app)

# Configurar correo
configurar_mail(app)

# Importar las rutas después de crear app
from routes.empleados_routes import empleados
from routes.contratos_routes import contratos

# Registrar los blueprints
app.register_blueprint(empleados)
app.register_blueprint(contratos)

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

    # Generar código temporal de 6 dígitos
    codigo = str(random.randint(100000, 999999))
    expira_en = (datetime.datetime.now() + datetime.timedelta(minutes=10)).isoformat()

    usuarios_table.update(
        {"codigo_recuperacion": codigo, "expira_en": expira_en},
        Usuario.correo == correo
    )

    try:
        enviar_correo(
            correo,
            "Recuperación de contraseña - Molino de Arroz",
            f"Tu código de recuperación es: {codigo}. Este código expirará en 10 minutos."
        )
        return jsonify({"message": "Código de recuperación enviado al correo ✅"}), 200
    except Exception as e:
        return jsonify({"error": f"No se pudo enviar el correo: {str(e)}"}), 500


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
        enviar_correo("destinatario@correo.com", "Prueba Flask", "Correo de prueba desde Flask.")
        return {"message": "Correo enviado correctamente ✅"}
    except Exception as e:
        return {"error": str(e)}, 500


# ------------------- EJECUCIÓN -------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
