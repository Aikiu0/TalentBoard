# config.py — Configuración central de TalentBoard
import os

# ============================================================
#  BASE DE DATOS  —  ¡AJUSTA ESTO A TU MYSQL WORKBENCH!
# ------------------------------------------------------------
#  Estos valores DEBEN coincidir con tu MySQL local:
#
#   - "user" y "password": el usuario con el que entras a Workbench.
#       Si usas el usuario por defecto, suele ser "root" y la
#       contraseña que pusiste al instalar MySQL.
#
#   - "database": el nombre EXACTO de tu esquema (schema) en Workbench
#       (el que ves en el panel izquierdo, bajo "SCHEMAS").
#
#   - "host": déjalo en "localhost" si MySQL corre en tu misma PC.
#   - "port": normalmente 3306 (cámbialo solo si tu MySQL usa otro).
# ============================================================
DB_CONFIG = {
    "host":     "localhost",
    "user":     "talentboard_user",
    "password": "TalentBoard2024!",
    "database": "talentboard",
    "charset":  "utf8mb4",
}

# --- Flask ---
SECRET_KEY = "talentboard-secret-key-2024"  # Cámbialo en producción
DEBUG = True
