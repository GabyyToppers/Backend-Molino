import smtplib
from email.mime.text import MIMEText

# Configuración del correo
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USERNAME = "gabrielapereiradiaz1@gmail.com"  # tu correo real
MAIL_PASSWORD = "jxrs oxyw zokx aupf"  # tu contraseña de aplicación generada

MAIL_USE_TLS = True
MAIL_USE_SSL = False


def configurar_mail(app):
    app.config['MAIL_SERVER'] = MAIL_SERVER
    app.config['MAIL_PORT'] = MAIL_PORT
    app.config['MAIL_USERNAME'] = MAIL_USERNAME
    app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
    app.config['MAIL_USE_TLS'] = MAIL_USE_TLS
    app.config['MAIL_USE_SSL'] = MAIL_USE_SSL
    return app


def enviar_correo(destinatario, asunto, mensaje):
    msg = MIMEText(mensaje)
    msg['Subject'] = asunto
    msg['From'] = MAIL_USERNAME
    msg['To'] = destinatario

    try:
        if MAIL_USE_SSL:
            server = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
        else:
            server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
        if MAIL_USE_TLS:
            server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_USERNAME, destinatario, msg.as_string())
        server.quit()
        print(f"✅ Correo enviado correctamente a {destinatario}")
    except Exception as e:
        print(f"❌ Error enviando correo: {e}")
