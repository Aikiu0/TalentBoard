# app.py — Punto de entrada de TalentBoard Backend
from flask import Flask
from flask_cors import CORS

import sys
import os

# Para que Python encuentre config.py y las rutas correctamente
sys.path.insert(0, os.path.dirname(__file__))

from config import SECRET_KEY, DEBUG
from routes.auth import auth_bp
from routes.vacantes import vacantes_bp
from routes.postulaciones import postulaciones_bp
from routes.perfil import perfil_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY

# ------------------------------------------------------------
# Configuración de la cookie de sesión.
#
# Usamos SameSite="Lax" porque funciona sobre HTTP (desarrollo local)
# SIEMPRE QUE el frontend y el backend estén en el MISMO host.
#
#   -> El frontend DEBE abrirse en  http://127.0.0.1:5500
#      y el backend corre en        http://127.0.0.1:5000
#      (mismo host 127.0.0.1, distinto puerto: la cookie SÍ viaja con Lax).
#
# NO uses "localhost" en uno y "127.0.0.1" en el otro: para el navegador
# son sitios distintos y la cookie no se compartiría.
#
# (Evitamos SameSite="None" porque Chrome exige Secure=True/HTTPS con él,
#  y en desarrollo no tenemos HTTPS.)
# ------------------------------------------------------------
app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
)

# Permite peticiones desde el frontend.
# Incluimos las dos formas (localhost y 127.0.0.1) y los puertos
# típicos de Live Server (5500) y http.server. Si tu frontend corre
# en otro puerto, agrégalo aquí.
CORS(app, supports_credentials=True, origins=[
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:5501",
    "http://localhost:5501",
])

# Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(vacantes_bp)
app.register_blueprint(postulaciones_bp)
app.register_blueprint(perfil_bp)


if __name__ == "__main__":
    app.run(debug=DEBUG, port=5000)
