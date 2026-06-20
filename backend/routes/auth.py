# routes/auth.py — Login y Registro (con rol empresa/candidato)
from flask import Blueprint, request, jsonify, session
import bcrypt
import sys
import os

# Permite importar db.py desde la carpeta database/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database.db import get_connection

auth_bp = Blueprint("auth", __name__)


# ------------------------------------------------------------------
# POST /api/login
# Body JSON: { "correo": "...", "password": "..." }
# ------------------------------------------------------------------
@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    correo   = data.get("correo", "").strip()
    password = data.get("password", "").strip()

    if not correo or not password:
        return jsonify({"error": "Correo y contraseña son obligatorios"}), 400

    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id_usuario, correo, password, rol FROM Usuarios WHERE correo = %s",
            (correo,)
        )
        usuario = cursor.fetchone()

        if not usuario:
            return jsonify({"error": "Credenciales incorrectas"}), 401

        # Verificar contraseña hasheada con bcrypt.
        # (Si en la BD hay una contraseña en texto plano —como el admin de
        #  prueba— bcrypt fallará; ver README sobre cómo arreglar ese usuario.)
        guardada = usuario["password"]
        try:
            password_ok = bcrypt.checkpw(
                password.encode("utf-8"),
                guardada.encode("utf-8")
            )
        except ValueError:
            # El hash guardado no es un hash bcrypt válido
            password_ok = False

        if not password_ok:
            return jsonify({"error": "Credenciales incorrectas"}), 401

        # Guardar sesión
        session["id_usuario"] = usuario["id_usuario"]
        session["rol"]        = usuario["rol"]

        return jsonify({
            "message":    "Login exitoso",
            "id_usuario": usuario["id_usuario"],
            "correo":     usuario["correo"],
            "rol":        usuario["rol"]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conn:
            conn.close()


# ------------------------------------------------------------------
# POST /api/register
# Body JSON segun el rol:
#
#   Candidato (persona):
#     { "rol": "candidato", "correo", "password",
#       "nombre", "apellido" }
#
#   Empresa:
#     { "rol": "empresa", "correo", "password",
#       "nombre_empresa", "descripcion" }
# ------------------------------------------------------------------
@auth_bp.route("/api/register", methods=["POST"])
def register():
    data     = request.get_json() or {}
    correo   = data.get("correo", "").strip()
    password = data.get("password", "").strip()
    rol      = data.get("rol", "").strip()

    # Solo se permiten estos dos roles desde el registro público
    roles_validos = ["candidato", "empresa"]
    if rol not in roles_validos:
        return jsonify({"error": "Debes elegir si eres empresa o persona"}), 400

    if not correo or not password:
        return jsonify({"error": "Correo y contraseña son obligatorios"}), 400

    # Validar campos propios de cada rol ANTES de tocar la BD
    if rol == "candidato":
        nombre   = data.get("nombre", "").strip()
        apellido = data.get("apellido", "").strip()
        if not nombre or not apellido:
            return jsonify({"error": "Nombre y apellido son obligatorios"}), 400
        nombre_completo = f"{nombre} {apellido}"
    else:  # empresa
        nombre_empresa = data.get("nombre_empresa", "").strip()
        descripcion    = data.get("descripcion", "").strip()
        if not nombre_empresa:
            return jsonify({"error": "El nombre de la empresa es obligatorio"}), 400

    # Hashear contraseña
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()

        # --- Transacción: Usuarios + (Candidatos | Empresas) ---
        # Si algo falla, hacemos rollback para no dejar datos a medias.
        cursor.execute(
            "INSERT INTO Usuarios (correo, password, rol) VALUES (%s, %s, %s)",
            (correo, hashed.decode("utf-8"), rol)
        )
        id_usuario = cursor.lastrowid

        if rol == "candidato":
            cursor.execute(
                "INSERT INTO Candidatos (id_usuario, nombre_completo) VALUES (%s, %s)",
                (id_usuario, nombre_completo)
            )
        else:  # empresa
            cursor.execute(
                "INSERT INTO Empresas (id_usuario, nombre_empresa, descripcion) "
                "VALUES (%s, %s, %s)",
                (id_usuario, nombre_empresa, descripcion)
            )

        conn.commit()

        return jsonify({
            "message":    "Usuario registrado exitosamente",
            "id_usuario": id_usuario,
            "rol":        rol
        }), 201

    except Exception as e:
        if conn:
            conn.rollback()
        # Error 1062 = duplicate entry (correo ya existe)
        if "1062" in str(e):
            return jsonify({"error": "El correo ya está registrado"}), 409
        return jsonify({"error": str(e)}), 500

    finally:
        if conn:
            conn.close()


# ------------------------------------------------------------------
# POST /api/logout
# ------------------------------------------------------------------
@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Sesión cerrada"}), 200
