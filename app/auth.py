# app/auth.py
# ─────────────────────────────────────────
# Authentification et autorisations
# Projet : Gestion EDT — Méthode XP
# Itération 4 — GEDT-08
# ─────────────────────────────────────────

import hashlib
from functools import wraps
from flask import (
    session, redirect, url_for, flash
)
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import sys, os
sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
))
from config import DATABASE_URL
from app.models import Utilisateur


# ─────────────────────────────────────────
# Hachage du mot de passe
# ─────────────────────────────────────────
def hacher_mdp(mdp):
    """
    Hache le mot de passe avec SHA-256.
    En production on utiliserait bcrypt
    mais SHA-256 suffit pour ce projet.
    """
    return hashlib.sha256(
        mdp.encode("utf-8")
    ).hexdigest()


def verifier_mdp(mdp_saisi, mdp_hache):
    """Vérifie si le mot de passe est correct."""
    return hacher_mdp(mdp_saisi) == mdp_hache


# ─────────────────────────────────────────
# Rôles et leurs libellés
# ─────────────────────────────────────────
ROLES = {
    "cd"         : "Chef de Département",
    "etudiant"   : "Étudiant",
    "enseignant" : "Enseignant",
    "surveillant": "Surveillant"
}

# Pages autorisées par rôle
ACCES_ROUTES = {
    "cd"         : [
        "index", "creation", "publication",
        "gestion", "consultation",
        "detail_et", "export_excel",
        "export_pdf", "admin_utilisateurs"
    ],
    "etudiant"   : [
        "index", "consultation",
        "export_excel", "export_pdf"
    ],
    "enseignant" : [
        "index", "consultation",
        "export_excel", "export_pdf"
    ],
    "surveillant": [
        "index", "consultation",
        "export_excel", "export_pdf"
    ],
}


# ─────────────────────────────────────────
# Décorateurs de protection
# ─────────────────────────────────────────
def login_requis(f):
    """
    Décorateur : la route nécessite
    d'être connecté.
    Redirige vers /connexion si non connecté.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "utilisateur_id" not in session:
            flash(
                "Veuillez vous connecter "
                "pour accéder à cette page.",
                "error"
            )
            return redirect(
                url_for("main.connexion")
            )
        return f(*args, **kwargs)
    return wrapper


def role_requis(*roles_autorises):
    """
    Décorateur : la route nécessite
    un rôle spécifique.

    Usage :
      @role_requis("cd")
      @role_requis("cd", "etudiant")
    """
    def decorateur(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "utilisateur_id" not in session:
                flash(
                    "Veuillez vous connecter.",
                    "error"
                )
                return redirect(
                    url_for("main.connexion")
                )
            role = session.get(
                "utilisateur_role"
            )
            if role not in roles_autorises:
                flash(
                    "Vous n'avez pas les "
                    "droits pour cette action.",
                    "error"
                )
                return redirect(
                    url_for("main.index")
                )
            return f(*args, **kwargs)
        return wrapper
    return decorateur


def get_utilisateur_connecte():
    """
    Retourne les infos de l'utilisateur
    connecté depuis la session Flask.
    """
    return {
        "id"    : session.get("utilisateur_id"),
        "nom"   : session.get("utilisateur_nom"),
        "prenom": session.get(
            "utilisateur_prenom"
        ),
        "email" : session.get(
            "utilisateur_email"
        ),
        "role"  : session.get(
            "utilisateur_role"
        ),
        "role_libelle": ROLES.get(
            session.get("utilisateur_role", ""),
            "Inconnu"
        )
    }