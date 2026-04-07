# config.py
# ─────────────────────────────────────────
# Configuration de la connexion PostgreSQL
# Projet : Gestion EDT — Méthode XP
# Itération 1 — GEDT-01
# ─────────────────────────────────────────

# Informations de connexion à la BD
DB_CONFIG = {
    "host"    : "localhost",
    "port"    : "5432",
    "database": "gestion_edt",
    "user"    : "postgres",
    "password": "astraorigine"
}



# URL complète pour SQLAlchemy
DATABASE_URL = (
    f"postgresql://"
    f"{DB_CONFIG['user']}:"
    f"{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:"
    f"{DB_CONFIG['port']}/"
    f"{DB_CONFIG['database']}"
)