# routes/perfil.py — Datos de perfil y estadísticas para los dashboards
from flask import Blueprint, request, jsonify, session
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database.db import get_connection

perfil_bp = Blueprint("perfil", __name__)


# ------------------------------------------------------------------
# GET /api/me
# Devuelve los datos del usuario logueado (según su rol) + estadísticas
# para mostrar en el dashboard. Si no hay sesión, 401.
# ------------------------------------------------------------------
@perfil_bp.route("/api/me", methods=["GET"])
def me():
    if not session.get("id_usuario"):
        return jsonify({"error": "No autenticado"}), 401

    id_usuario = session["id_usuario"]
    rol = session.get("rol")

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id_usuario, correo, rol FROM Usuarios WHERE id_usuario = %s",
            (id_usuario,)
        )
        usuario = cursor.fetchone()
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        resp = {"usuario": usuario, "rol": rol}

        if rol == "candidato":
            cursor.execute("""
                SELECT id_candidato, nombre_completo, especialidad, url_cv
                FROM Candidatos WHERE id_usuario = %s
            """, (id_usuario,))
            cand = cursor.fetchone()
            resp["perfil"] = cand

            if cand:
                idc = cand["id_candidato"]
                cursor.execute(
                    "SELECT COUNT(*) AS n FROM Postulaciones WHERE id_candidato = %s",
                    (idc,)
                )
                total = cursor.fetchone()["n"]
                cursor.execute("""
                    SELECT COUNT(*) AS n FROM Postulaciones
                    WHERE id_candidato = %s AND estado = 'aceptado'
                """, (idc,))
                aceptadas = cursor.fetchone()["n"]
                cursor.execute("""
                    SELECT COUNT(*) AS n FROM Postulaciones
                    WHERE id_candidato = %s AND estado = 'revisado'
                """, (idc,))
                revisadas = cursor.fetchone()["n"]
                resp["stats"] = {
                    "postulaciones": total,
                    "aceptadas": aceptadas,
                    "revisadas": revisadas,
                }

        elif rol == "empresa":
            cursor.execute("""
                SELECT id_empresa, nombre_empresa, descripcion, aprobada
                FROM Empresas WHERE id_usuario = %s
            """, (id_usuario,))
            emp = cursor.fetchone()
            resp["perfil"] = emp

            if emp:
                ide = emp["id_empresa"]
                cursor.execute("""
                    SELECT COUNT(*) AS n FROM Vacantes
                    WHERE id_empresa = %s AND activa = TRUE
                """, (ide,))
                vac_activas = cursor.fetchone()["n"]
                cursor.execute("""
                    SELECT COUNT(*) AS n FROM Postulaciones p
                    JOIN Vacantes v ON p.id_vacante = v.id_vacante
                    WHERE v.id_empresa = %s
                """, (ide,))
                total_post = cursor.fetchone()["n"]
                cursor.execute("""
                    SELECT COUNT(*) AS n FROM Postulaciones p
                    JOIN Vacantes v ON p.id_vacante = v.id_vacante
                    WHERE v.id_empresa = %s AND p.estado = 'pendiente'
                """, (ide,))
                pendientes = cursor.fetchone()["n"]
                resp["stats"] = {
                    "vacantes_activas": vac_activas,
                    "postulaciones_totales": total_post,
                    "postulaciones_pendientes": pendientes,
                }

        return jsonify(resp), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


# ------------------------------------------------------------------
# PUT /api/perfil/candidato
# Actualiza nombre/especialidad del candidato logueado.
# Body: { nombre_completo?, especialidad? }
# ------------------------------------------------------------------
@perfil_bp.route("/api/perfil/candidato", methods=["PUT"])
def actualizar_candidato():
    if session.get("rol") != "candidato":
        return jsonify({"error": "Solo para candidatos"}), 403

    data = request.get_json() or {}
    nombre = (data.get("nombre_completo") or "").strip()
    especialidad = (data.get("especialidad") or "").strip()

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Candidatos
            SET nombre_completo = %s, especialidad = %s
            WHERE id_usuario = %s
        """, (nombre, especialidad, session["id_usuario"]))
        conn.commit()
        return jsonify({"message": "Perfil actualizado"}), 200
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


# ------------------------------------------------------------------
# PUT /api/perfil/empresa
# Actualiza nombre/descripción de la empresa logueada.
# ------------------------------------------------------------------
@perfil_bp.route("/api/perfil/empresa", methods=["PUT"])
def actualizar_empresa():
    if session.get("rol") != "empresa":
        return jsonify({"error": "Solo para empresas"}), 403

    data = request.get_json() or {}
    nombre = (data.get("nombre_empresa") or "").strip()
    descripcion = (data.get("descripcion") or "").strip()

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Empresas
            SET nombre_empresa = %s, descripcion = %s
            WHERE id_usuario = %s
        """, (nombre, descripcion, session["id_usuario"]))
        conn.commit()
        return jsonify({"message": "Perfil actualizado"}), 200
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
