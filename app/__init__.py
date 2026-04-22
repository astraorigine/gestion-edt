# app/__init__.py
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import sys, os
sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
))
from config import DATABASE_URL

def create_app():
    """
    Crée et configure l'application Flask.
    Retourne l'app configurée.
    """
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )

    app.secret_key = "gestion_edt_xp_2026"

    # Enregistrer les routes
    from app.routes import main
    app.register_blueprint(main)

    return app