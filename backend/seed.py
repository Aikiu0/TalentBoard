# seed.py — Carga datos de ejemplo en TalentBoard
# Ejecútalo UNA vez con:  python seed.py
#
# Crea:
#   - 3 empresas (aprobadas) con login
#   - 1 candidato de prueba con login
#   - varias vacantes en CDMX y alrededores (con coordenadas para el mapa)
#
# Usuarios de prueba que crea (todos con contraseña: 123456):
#   empresa:   greensoft@test.com
#   empresa:   digitalent@test.com
#   empresa:   nucleo@test.com
#   candidato: ana@test.com

import sys
import os
import bcrypt

sys.path.insert(0, os.path.dirname(__file__))
from database.db import get_connection


def hashear(pw):
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


EMPRESAS = [
    {
        "correo": "greensoft@test.com",
        "nombre_empresa": "GreenSoft",
        "descripcion": "Empresa de software enfocada en soluciones sostenibles.",
        "vacantes": [
            {"titulo": "Diseñador/a UX/UI", "salario": 25000,
             "lat": 19.4326, "lng": -99.1332,
             "descripcion": "Buscamos diseñador UX/UI con experiencia en figma y prototipado. Tiempo completo, modalidad híbrida en Ciudad de México."},
            {"titulo": "Desarrollador Frontend React", "salario": 32000,
             "lat": 19.4361, "lng": -99.1410,
             "descripcion": "Desarrollo de interfaces con React. Conocimientos en HTML, CSS, JS y consumo de APIs REST."},
        ],
    },
    {
        "correo": "digitalent@test.com",
        "nombre_empresa": "Digitalent",
        "descripcion": "Consultora digital especializada en producto.",
        "vacantes": [
            {"titulo": "Product Designer", "salario": 28000,
             "lat": 20.6597, "lng": -103.3496,
             "descripcion": "Diseño de producto digital de inicio a fin. Guadalajara, Jalisco. Remoto."},
            {"titulo": "Analista de Datos", "salario": 30000,
             "lat": 20.6736, "lng": -103.3440,
             "descripcion": "Análisis de datos con SQL y Python. Generación de reportes y dashboards."},
        ],
    },
    {
        "correo": "nucleo@test.com",
        "nombre_empresa": "Núcleo Creativo",
        "descripcion": "Estudio de diseño y creatividad.",
        "vacantes": [
            {"titulo": "Diseñador Gráfico", "salario": 18000,
             "lat": 25.6866, "lng": -100.3161,
             "descripcion": "Diseño gráfico para campañas y branding. Monterrey, Nuevo León. Presencial."},
            {"titulo": "Community Manager", "salario": 16000,
             "lat": 25.6801, "lng": -100.3150,
             "descripcion": "Gestión de redes sociales y creación de contenido."},
        ],
    },
]

CANDIDATO = {
    "correo": "ana@test.com",
    "nombre_completo": "Ana Martínez",
    "especialidad": "Diseñadora UX/UI",
}


def usuario_existe(cursor, correo):
    cursor.execute("SELECT id_usuario FROM Usuarios WHERE correo = %s", (correo,))
    return cursor.fetchone()


def seed():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    pw_hash = hashear("123456")

    print("Sembrando datos de ejemplo...\n")

    # --- Empresas + vacantes ---
    for emp in EMPRESAS:
        existe = usuario_existe(cursor, emp["correo"])
        if existe:
            print(f"  - Empresa {emp['correo']} ya existe, omitida.")
            cursor.execute(
                "SELECT id_empresa FROM Empresas WHERE id_usuario = %s",
                (existe["id_usuario"],)
            )
            row = cursor.fetchone()
            id_empresa = row["id_empresa"] if row else None
        else:
            cursor.execute(
                "INSERT INTO Usuarios (correo, password, rol) VALUES (%s, %s, 'empresa')",
                (emp["correo"], pw_hash)
            )
            id_usuario = cursor.lastrowid
            cursor.execute(
                "INSERT INTO Empresas (id_usuario, nombre_empresa, descripcion, aprobada) "
                "VALUES (%s, %s, %s, TRUE)",
                (id_usuario, emp["nombre_empresa"], emp["descripcion"])
            )
            id_empresa = cursor.lastrowid
            print(f"  + Empresa creada: {emp['nombre_empresa']} ({emp['correo']})")

        # Vacantes
        if id_empresa:
            for v in emp["vacantes"]:
                cursor.execute("""
                    SELECT id_vacante FROM Vacantes
                    WHERE id_empresa = %s AND titulo = %s
                """, (id_empresa, v["titulo"]))
                if cursor.fetchone():
                    continue
                cursor.execute("""
                    INSERT INTO Vacantes (id_empresa, titulo, descripcion, salario, latitud, longitud)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (id_empresa, v["titulo"], v["descripcion"], v["salario"], v["lat"], v["lng"]))
                print(f"      · Vacante: {v['titulo']}")

    # --- Candidato de prueba ---
    existe = usuario_existe(cursor, CANDIDATO["correo"])
    if existe:
        print(f"\n  - Candidato {CANDIDATO['correo']} ya existe, omitido.")
    else:
        cursor.execute(
            "INSERT INTO Usuarios (correo, password, rol) VALUES (%s, %s, 'candidato')",
            (CANDIDATO["correo"], pw_hash)
        )
        id_usuario = cursor.lastrowid
        cursor.execute(
            "INSERT INTO Candidatos (id_usuario, nombre_completo, especialidad) "
            "VALUES (%s, %s, %s)",
            (id_usuario, CANDIDATO["nombre_completo"], CANDIDATO["especialidad"])
        )
        print(f"\n  + Candidato creado: {CANDIDATO['nombre_completo']} ({CANDIDATO['correo']})")

    conn.commit()
    cursor.close()
    conn.close()

    print("\n" + "=" * 55)
    print(" ¡Listo! Usuarios de prueba (contraseña: 123456):")
    print("   Empresa:   greensoft@test.com")
    print("   Empresa:   digitalent@test.com")
    print("   Empresa:   nucleo@test.com")
    print("   Candidato: ana@test.com")
    print("=" * 55)


if __name__ == "__main__":
    try:
        seed()
    except Exception as e:
        print("ERROR al sembrar datos:", e)
        print("¿Está corriendo MySQL y config.py tiene las credenciales correctas?")
