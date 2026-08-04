# database/db.py — Conexión reutilizable a MySQL
import mysql.connector
from config import DB_CONFIG


def get_connection():
    """
    Retorna una conexión activa a la base de datos talentboard.
    Úsala siempre con un bloque try/finally para cerrarla.
    """
    return mysql.connector.connect(**DB_CONFIG)
