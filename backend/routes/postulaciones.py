# routes/postulaciones.py — Postulaciones de candidatos a vacantes
from flask import Blueprint, request, jsonify, session
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database.db import get_connection

postulaciones_bp = Blueprint("postulaciones", __name__)


def _fecha_str(valor):
    """Devuelve la fecha como 'YYYY-MM-DD' tanto si es datetime como si es string.
    (MySQL devuelve datetime; otros entornos podrían devolver string.)"""
    if valor is None:
        return None
    if hasattr(valor, "strftime"):
        return valor.strftime("%Y-%m-%d")
    # Si ya es string, recortar a los primeros 10 caracteres (la fecha)
    return str(valor)[:10]


def _id_candidato_de_sesion(cursor):
    cursor.execute(
        "SELECT id_candidato FROM Candidatos WHERE id_usuario = %s",
        (session.get("id_usuario"),)
    )
    fila = cursor.fetchone()
    return fila["id_candidato"] if fila else None


def _id_empresa_de_sesion(cursor):
    cursor.execute(
        "SELECT id_empresa FROM Empresas WHERE id_usuario = %s",
        (session.get("id_usuario"),)
    )
    fila = cursor.fetchone()
    return fila["id_empresa"] if fila else None


# ------------------------------------------------------------------
# POST /api/postulaciones
# El candidato logueado se postula a una vacante.
# Body: { id_vacante }
# ------------------------------------------------------------------
@postulaciones_bp.route("/api/postulaciones", methods=["POST"])
def postularse():
    if session.get("rol") != "candidato":
        return jsonify({"error": "Solo los candidatos pueden postularse"}), 403

    data = request.get_json() or {}
    id_vacante = data.get("id_vacante")
    if not id_vacante:
        return jsonify({"error": "Falta la vacante"}), 400

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        id_candidato = _id_candidato_de_sesion(cursor)
        if not id_candidato:
            return jsonify({"error": "No se encontró el candidato"}), 400

        # ¿Ya se postuló antes?
        cursor.execute("""
            SELECT id_postulacion FROM Postulaciones
            WHERE id_candidato = %s AND id_vacante = %s
        """, (id_candidato, id_vacante))
        if cursor.fetchone():
            return jsonify({"error": "Ya te postulaste a esta vacante"}), 409

        cursor.execute("""
            INSERT INTO Postulaciones (id_candidato, id_vacante)
            VALUES (%s, %s)
        """, (id_candidato, id_vacante))
        conn.commit()
        return jsonify({"message": "¡Postulación enviada!"}), 201

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


# ------------------------------------------------------------------
# GET /api/mis-postulaciones
# Postulaciones del candidato logueado.
# ------------------------------------------------------------------
@postulaciones_bp.route("/api/mis-postulaciones", methods=["GET"])
def mis_postulaciones():
    if session.get("rol") != "candidato":
        return jsonify({"error": "Solo para candidatos"}), 403

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        id_candidato = _id_candidato_de_sesion(cursor)
        if not id_candidato:
            return jsonify({"postulaciones": []}), 200

        cursor.execute("""
            SELECT p.id_postulacion, p.estado, p.fecha_postulacion,
                   v.titulo, v.salario, e.nombre_empresa
            FROM Postulaciones p
            JOIN Vacantes v ON p.id_vacante = v.id_vacante
            JOIN Empresas e ON v.id_empresa = e.id_empresa
            WHERE p.id_candidato = %s
            ORDER BY p.fecha_postulacion DESC
        """, (id_candidato,))
        posts = cursor.fetchall()
        for p in posts:
            if p["salario"] is not None:
                p["salario"] = float(p["salario"])
            p["fecha_postulacion"] = _fecha_str(p.get("fecha_postulacion"))
        return jsonify({"postulaciones": posts}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


# ------------------------------------------------------------------
# GET /api/vacantes/<id>/postulaciones
# La empresa ve quién se postuló a una de sus vacantes.
# ------------------------------------------------------------------
@postulaciones_bp.route("/api/vacantes/<int:id_vacante>/postulaciones", methods=["GET"])
def postulaciones_de_vacante(id_vacante):
    if session.get("rol") != "empresa":
        return jsonify({"error": "Solo para empresas"}), 403

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        id_empresa = _id_empresa_de_sesion(cursor)
        # Verificar que la vacante sea de esta empresa
        cursor.execute("SELECT id_empresa FROM Vacantes WHERE id_vacante = %s", (id_vacante,))
        fila = cursor.fetchone()
        if not fila or fila["id_empresa"] != id_empresa:
            return jsonify({"error": "No autorizado"}), 403

        cursor.execute("""
            SELECT p.id_postulacion, p.estado, p.fecha_postulacion,
                   c.nombre_completo, c.especialidad, u.correo
            FROM Postulaciones p
            JOIN Candidatos c ON p.id_candidato = c.id_candidato
            JOIN Usuarios u ON c.id_usuario = u.id_usuario
            WHERE p.id_vacante = %s
            ORDER BY p.fecha_postulacion DESC
        """, (id_vacante,))
        posts = cursor.fetchall()
        for p in posts:
            p["fecha_postulacion"] = _fecha_str(p.get("fecha_postulacion"))
        return jsonify({"postulaciones": posts}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


# ------------------------------------------------------------------
# PUT /api/postulaciones/<id>/estado
# La empresa cambia el estado de una postulación.
# Body: { estado: "revisado"|"aceptado"|"rechazado" }
# ------------------------------------------------------------------
@postulaciones_bp.route("/api/postulaciones/<int:id_postulacion>/estado", methods=["PUT"])
def cambiar_estado(id_postulacion):
    if session.get("rol") != "empresa":
        return jsonify({"error": "Solo para empresas"}), 403

    data = request.get_json() or {}
    estado = (data.get("estado") or "").strip()
    if estado not in ["pendiente", "revisado", "aceptado", "rechazado"]:
        return jsonify({"error": "Estado inválido"}), 400

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        id_empresa = _id_empresa_de_sesion(cursor)

        # Verificar que la postulación pertenece a una vacante de esta empresa
        cursor.execute("""
            SELECT v.id_empresa
            FROM Postulaciones p
            JOIN Vacantes v ON p.id_vacante = v.id_vacante
            WHERE p.id_postulacion = %s
        """, (id_postulacion,))
        fila = cursor.fetchone()
        if not fila or fila["id_empresa"] != id_empresa:
            return jsonify({"error": "No autorizado"}), 403

        cursor.execute(
            "UPDATE Postulaciones SET estado = %s WHERE id_postulacion = %s",
            (estado, id_postulacion)
        )
        conn.commit()
        return jsonify({"message": "Estado actualizado"}), 200
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
