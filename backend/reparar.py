# reparar.py — Diagnostica y repara usuarios "huérfanos"
#
# Un usuario huérfano es uno que tiene fila en Usuarios pero le falta su fila
# en Candidatos (si rol=candidato) o en Empresas (si rol=empresa). Esto puede
# pasar con usuarios creados antes de que el registro insertara en ambas tablas.
#
# Ejecútalo con:  python reparar.py

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from database.db import get_connection


def reparar():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    print("=" * 55)
    print(" DIAGNÓSTICO DE USUARIOS")
    print("=" * 55)

    # Todos los usuarios
    cursor.execute("SELECT id_usuario, correo, rol FROM Usuarios ORDER BY id_usuario")
    usuarios = cursor.fetchall()
    print(f"\nTotal de usuarios: {len(usuarios)}\n")

    reparados = 0

    for u in usuarios:
        idu = u["id_usuario"]
        rol = u["rol"]
        correo = u["correo"]

        if rol == "candidato":
            cursor.execute("SELECT id_candidato FROM Candidatos WHERE id_usuario = %s", (idu,))
            if cursor.fetchone():
                print(f"  OK       {correo} (candidato) tiene su ficha.")
            else:
                # Reparar: crear fila en Candidatos con un nombre por defecto
                nombre_def = correo.split("@")[0]
                cursor.execute(
                    "INSERT INTO Candidatos (id_usuario, nombre_completo) VALUES (%s, %s)",
                    (idu, nombre_def)
                )
                print(f"  REPARADO {correo} (candidato): se creó su ficha como '{nombre_def}'.")
                reparados += 1

        elif rol == "empresa":
            cursor.execute("SELECT id_empresa FROM Empresas WHERE id_usuario = %s", (idu,))
            if cursor.fetchone():
                print(f"  OK       {correo} (empresa) tiene su ficha.")
            else:
                nombre_def = correo.split("@")[0]
                cursor.execute(
                    "INSERT INTO Empresas (id_usuario, nombre_empresa, aprobada) VALUES (%s, %s, TRUE)",
                    (idu, nombre_def)
                )
                print(f"  REPARADO {correo} (empresa): se creó su ficha como '{nombre_def}'.")
                reparados += 1

        else:  # administrador u otro
            print(f"  -        {correo} ({rol}): no requiere ficha.")

    conn.commit()
    cursor.close()
    conn.close()

    print("\n" + "=" * 55)
    if reparados:
        print(f" Se repararon {reparados} usuario(s).")
        print(" Ya puedes postularte / crear vacantes con ellos.")
    else:
        print(" Todo en orden. No había usuarios huérfanos.")
    print("=" * 55)


if __name__ == "__main__":
    try:
        reparar()
    except Exception as e:
        print("ERROR:", e)
        print("¿Está corriendo MySQL y config.py tiene las credenciales correctas?")
