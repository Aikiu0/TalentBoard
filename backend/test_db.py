# test_db.py — Diagnóstico de conexión a MySQL
# Ejecútalo con:  python test_db.py
# Te dirá EXACTAMENTE qué está fallando con la base de datos.

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

print("=" * 55)
print(" DIAGNÓSTICO DE BASE DE DATOS - TalentBoard")
print("=" * 55)

# 1) ¿Está instalado el conector?
try:
    import mysql.connector
    from mysql.connector import errorcode
    print("[OK] mysql-connector-python está instalado.")
except ImportError:
    print("[ERROR] Falta el conector. Ejecuta:")
    print("        pip install mysql-connector-python")
    sys.exit(1)

# 2) Leer la config
try:
    from config import DB_CONFIG
    print(f"[OK] config.py leído.")
    print(f"     host={DB_CONFIG.get('host')}  port={DB_CONFIG.get('port', 3306)}")
    print(f"     user={DB_CONFIG.get('user')}  database={DB_CONFIG.get('database')}")
except Exception as e:
    print(f"[ERROR] No se pudo leer config.py: {e}")
    sys.exit(1)

# 3) Intentar conectar
print("-" * 55)
print("Intentando conectar...")
conn = None
try:
    conn = mysql.connector.connect(**DB_CONFIG)
    print("[OK] ¡Conexión exitosa a la base de datos!")
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("[ERROR] Usuario o contraseña INCORRECTOS.")
        print("        Revisa 'user' y 'password' en config.py.")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("[ERROR] La base de datos NO EXISTE.")
        print(f"        El schema '{DB_CONFIG.get('database')}' no está en tu MySQL.")
        print("        Verifica el nombre exacto en Workbench (panel SCHEMAS).")
    elif err.errno == 2003:
        print("[ERROR] No se puede conectar al servidor MySQL.")
        print("        ¿Está MySQL encendido? ¿El puerto es correcto (3306)?")
    else:
        print(f"[ERROR] {err}")
    sys.exit(1)

# 4) Revisar la tabla Usuarios y la columna rol
try:
    cur = conn.cursor()
    cur.execute("SHOW TABLES LIKE 'Usuarios'")
    if not cur.fetchone():
        print("[AVISO] No existe la tabla 'Usuarios'.")
        print("        Ejecuta el script schema.sql (incluido en backend/).")
    else:
        print("[OK] La tabla 'Usuarios' existe.")
        cur.execute("SHOW COLUMNS FROM Usuarios LIKE 'rol'")
        if cur.fetchone():
            print("[OK] La columna 'rol' existe en Usuarios.")
        else:
            print("[AVISO] Falta la columna 'rol' en Usuarios.")
            print("        Ejecuta: ALTER TABLE Usuarios ADD COLUMN rol VARCHAR(20);")
    cur.close()
except Exception as e:
    print(f"[AVISO] No se pudo revisar la tabla: {e}")

conn.close()
print("=" * 55)
print(" Diagnóstico terminado.")
print("=" * 55)
