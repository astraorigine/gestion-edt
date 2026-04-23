# run.py
# ─────────────────────────────────────────
# Point d'entrée de l'application Flask
# Projet : Gestion EDT — Méthode XP(AstraTeams)
# ─────────────────────────────────────────

from app import create_app

app = create_app()

if __name__ == "__main__":
    print(" Gestion EDT — Interface Web")
    print("   Accès : http://localhost:5000")
    print("   Arrêt : Ctrl+C")
    app.run(
        debug=True,
        port=5000
    )