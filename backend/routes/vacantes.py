# routes/vacantes.py — Endpoints de vacantes
from flask import Blueprint, request, jsonify, session
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database.db import get_connection

vacantes_bp = Blueprint("vacantes", __name__)


def _id_empresa_de_sesion(cursor):
    """Devuelve el id_empresa asociado al usuario logueado (o None)."""
    cursor.execute(
        "SELECT id_empresa FROM Empresas WHERE id_usuario = %s",
        (session.get("id_usuario"),)
    )
    fila = cursor.fetchone()
    return fila["id_empresa"] if fila else None


# ------------------------------------------------------------------
# GET /api/vacantes
# Lista todas las vacantes activas (para el candidato).
# Soporta búsqueda opcional:  ?q=texto
# ------------------------------------------------------------------
@vacantes_bp.route("/api/vacantes", methods=["GET"])
def listar_vacantes():
    q = request.args.get("q", "").strip()

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
            SELECT v.id_vacante, v.titulo, v.descripcion, v.salario,
                   v.latitud, v.longitud, v.activa,
                   e.nombre_empresa, e.id_empresa
            FROM Vacantes v
            JOIN Empresas e ON v.id_empresa = e.id_empresa
            WHERE v.activa = TRUE
        """
        params = []
        if q:
            sql += " AND (v.titulo LIKE %s OR e.nombre_empresa LIKE %s OR v.descripcion LIKE %s)"
            like = "%" + q + "%"
            params = [like, like, like]
        sql += " ORDER BY v.id_vacante DESC"

        cursor.execute(sql, params)
        vacantes = cursor.fetchall()

        # Convertir Decimal a float para JSON
        for v in vacantes:
            if v["salario"] is not None:
                v["salario"] = float(v["salario"])
            if v["latitud"] is not None:
                v["latitud"] = float(v["latitud"])
            if v["longitud"] is not None:
                v["longitud"] = float(v["longitud"])

        return jsonify({"vacantes": vacantes}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


# ------------------------------------------------------------------
# GET /api/vacantes/<id>
# Detalle de una vacante.
# ------------------------------------------------------------------
@vacantes_bp.route("/api/vacantes/<int:id_vacante>", methods=["GET"])
def detalle_vacante(id_vacante):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT v.id_vacante, v.titulo, v.descripcion, v.salario,
                   v.latitud, v.longitud, v.activa,
                   e.nombre_empresa, e.descripcion AS descripcion_empresa
            FROM Vacantes v
            JOIN Empresas e ON v.id_empresa = e.id_empresa
            WHERE v.id_vacante = %s
        """, (id_vacante,))
        vac = cursor.fetchone()
        if not vac:
            return jsonify({"error": "Vacante no encontrada"}), 404
        if vac["salario"] is not None:
            vac["salario"] = float(vac["salario"])
        return jsonify(vac), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


# ------------------------------------------------------------------
# POST /api/vacantes
# Crea una vacante (solo empresas logueadas).
# Body: { titulo, descripcion, salario?, latitud?, longitud? }
# ------------------------------------------------------------------
@vacantes_bp.route("/api/vacantes", methods=["POST"])
def crear_vacante():
    if session.get("rol") != "empresa":
        return jsonify({"error": "Solo las empresas pueden crear vacantes"}), 403

    data = request.get_json() or {}
    titulo      = (data.get("titulo") or "").strip()
    descripcion = (data.get("descripcion") or "").strip()
    salario     = data.get("salario")
    latitud     = data.get("latitud")
    longitud    = data.get("longitud")

    if not titulo or not descripcion:
        return jsonify({"error": "Título y descripción son obligatorios"}), 400

    # Normalizar números vacíos a None
    def _num(x):
        if x in (None, "", "null"):
            return None
        try:
            return float(x)
        except (TypeError, ValueError):
            return None

    salario  = _num(salario)
    latitud  = _num(latitud)
    longitud = _num(longitud)

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        id_empresa = _id_empresa_de_sesion(cursor)
        if not id_empresa:
            return jsonify({"error": "No se encontró la empresa del usuario"}), 400

        cursor.execute("""
            INSERT INTO Vacantes (id_empresa, titulo, descripcion, salario, latitud, longitud)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (id_empresa, titulo, descripcion, salario, latitud, longitud))
        conn.commit()

        return jsonify({
            "message": "Vacante creada exitosamente",
            "id_vacante": cursor.lastrowid
        }), 201

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


# ------------------------------------------------------------------
# GET /api/mis-vacantes
# Vacantes publicadas por la empresa logueada, con conteo de postulaciones.
# ------------------------------------------------------------------
@vacantes_bp.route("/api/mis-vacantes", methods=["GET"])
def mis_vacantes():
    if session.get("rol") != "empresa":
        return jsonify({"error": "Solo para empresas"}), 403

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        id_empresa = _id_empresa_de_sesion(cursor)
        if not id_empresa:
            return jsonify({"vacantes": []}), 200

        cursor.execute("""
            SELECT v.id_vacante, v.titulo, v.descripcion, v.salario, v.activa,
                   (SELECT COUNT(*) FROM Postulaciones p WHERE p.id_vacante = v.id_vacante)
                       AS num_postulaciones
            FROM Vacantes v
            WHERE v.id_empresa = %s
            ORDER BY v.id_vacante DESC
        """, (id_empresa,))
        vacantes = cursor.fetchall()
        for v in vacantes:
            if v["salario"] is not None:
                v["salario"] = float(v["salario"])
        return jsonify({"vacantes": vacantes}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


# ------------------------------------------------------------------
# DELETE /api/vacantes/<id>  (en realidad la desactiva)
# ------------------------------------------------------------------
@vacantes_bp.route("/api/vacantes/<int:id_vacante>", methods=["DELETE"])
def desactivar_vacante(id_vacante):
    if session.get("rol") != "empresa":
        return jsonify({"error": "Solo para empresas"}), 403

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        id_empresa = _id_empresa_de_sesion(cursor)

        # Verificar que la vacante sea de esta empresa
        cursor.execute(
            "SELECT id_empresa FROM Vacantes WHERE id_vacante = %s",
            (id_vacante,)
        )
        fila = cursor.fetchone()
        if not fila or fila["id_empresa"] != id_empresa:
            return jsonify({"error": "No autorizado"}), 403

        cursor.execute(
            "UPDATE Vacantes SET activa = FALSE WHERE id_vacante = %s",
            (id_vacante,)
        )
        conn.commit()
        return jsonify({"message": "Vacante desactivada"}), 200
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
