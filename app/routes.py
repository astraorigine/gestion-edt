# app/routes.py
# ─────────────────────────────────────────
# Routes Flask — Interface Web
# Projet : Gestion EDT — Méthode XP
# Itération 4 — GEDT-08
# ─────────────────────────────────────────

from flask import (
    Blueprint, render_template,
    request, redirect, url_for,
    flash, jsonify, send_file
)
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import date
import sys, os
sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
))
from config import DATABASE_URL
from app.models import (
    Parcours, Semestre, Matiere,
    EmploiDuTemps, Seance, Enseignant
)
from app.gestion_et import (
    creer_et, publier_et,
    consulter_et, archiver_et,
    modifier_seance, supprimer_et
)
from app.algorithmes import (
    assigner_matieres,
    sauvegarder_en_bd,
    assigner_enseignants
)

from app.auth import (
    hacher_mdp, verifier_mdp,
    login_requis, role_requis,
    get_utilisateur_connecte
)
from app.models import Utilisateur

main = Blueprint("main", __name__)

# ═════════════════════════════════════════
# CONNEXION
# ═════════════════════════════════════════
@main.route(
    "/connexion",
    methods=["GET", "POST"]
)
def connexion():
    """
    Page de connexion.
    Redirige vers accueil si déjà connecté.
    """
    from flask import session as flask_session

    # Déjà connecté
    if "utilisateur_id" in flask_session:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email   = request.form["email"].strip()
        mdp     = request.form["mot_de_passe"]

        db = get_db()
        try:
            utilisateur = db.query(
                Utilisateur
            ).filter_by(
                email=email, actif=1
            ).first()

            if not utilisateur:
                flash(
                    "Email introuvable "
                    "ou compte désactivé.",
                    "error"
                )
                return render_template(
                    "connexion.html"
                )

            if not verifier_mdp(
                mdp,
                utilisateur.mot_de_passe
            ):
                flash(
                    "Mot de passe incorrect.",
                    "error"
                )
                return render_template(
                    "connexion.html"
                )

            # Connexion réussie
            flask_session["utilisateur_id"] = (
                utilisateur.id
            )
            flask_session["utilisateur_nom"] = (
                utilisateur.nom
            )
            flask_session["utilisateur_prenom"] = (
                utilisateur.prenom
            )
            flask_session["utilisateur_email"] = (
                utilisateur.email
            )
            flask_session["utilisateur_role"] = (
                utilisateur.role
            )

            flash(
                f"Bienvenue "
                f"{utilisateur.prenom} "
                f"{utilisateur.nom} ! ",
                "success"
            )
            return redirect(
                url_for("main.index")
            )

        finally:
            db.close()

    return render_template("connexion.html")


# ═════════════════════════════════════════
# DÉCONNEXION
# ═════════════════════════════════════════
@main.route("/deconnexion")
def deconnexion():
    from flask import session as flask_session
    flask_session.clear()
    flash(
        "Vous avez été déconnecté.",
        "info"
    )
    return redirect(url_for("main.connexion"))


def get_db():
    engine = create_engine(DATABASE_URL)
    return Session(engine)


def enrichir_et(db, edt):
    """
    Ajoute nom parcours, numéro semestre
    et nombre de séances à un EmploiDuTemps.
    """
    p = db.query(Parcours).filter_by(
        id=edt.parcours_id
    ).first()
    s = db.query(Semestre).filter_by(
        id=edt.semestre_id
    ).first()
    nb = db.query(Seance).filter_by(
        emploi_du_temps_id=edt.id
    ).count()
    return {
        "edt"       : edt,
        "parcours"  : p.nom if p else "?",
        "semestre"  : s.numero if s else "?",
        "nb_seances": nb
    }


def get_seances_dict(db, edt_id):
    """
    Retourne les séances organisées
    par jour → liste de séances enrichies.
    """
    seances = db.query(Seance).filter_by(
        emploi_du_temps_id=edt_id
    ).order_by(
        Seance.jour, Seance.heure_debut
    ).all()

    seances_dict = {}
    for s in seances:
        if s.jour not in seances_dict:
            seances_dict[s.jour] = []
        matiere = db.query(Matiere).filter_by(
            id=s.matiere_id
        ).first()
        enseignant = db.query(Enseignant).filter_by(
            id=s.enseignant_id
        ).first()
        seances_dict[s.jour].append({
            "heure"     : s.heure_debut,
            "duree"     : s.duree,
            "matiere"   : matiere,
            "enseignant": enseignant
        })
    return seances_dict


# ═════════════════════════════════════════
# ACCUEIL
# ═════════════════════════════════════════
@main.route("/")
@login_requis
def index():
    db = get_db()
    try:
        nb_parcours   = db.query(Parcours).count()
        nb_et         = db.query(EmploiDuTemps).count()
        nb_publies    = db.query(EmploiDuTemps).filter_by(
            publie=1
        ).count()
        nb_brouillons = db.query(EmploiDuTemps).filter_by(
            publie=0, archive=0
        ).count()

        # Derniers emplois du temps créés
        derniers = db.query(EmploiDuTemps).filter_by(
            archive=0
        ).order_by(
            EmploiDuTemps.id.desc()
        ).limit(5).all()

        derniers_et = [
            enrichir_et(db, edt)
            for edt in derniers
        ]

        return render_template(
            "index.html",
            nb_parcours   = nb_parcours,
            nb_et         = nb_et,
            nb_publies    = nb_publies,
            nb_brouillons = nb_brouillons,
            derniers_et   = derniers_et
        )
    finally:
        db.close()


# ═════════════════════════════════════════
# CRÉATION
# ═════════════════════════════════════════
@main.route(
    "/creation",
    methods=["GET", "POST"]
)
@login_requis
@role_requis("cd")
def creation():
    db = get_db()
    try:
        parcours_list = db.query(Parcours).all()

        if request.method == "POST":
            parcours_id  = int(
                request.form["parcours_id"]
            )
            semestre_id  = int(
                request.form["semestre_id"]
            )
            type_session = request.form["type_session"]
            date_str     = request.form["date_debut"]
            heure_debut  = int(
                request.form.get("heure_debut", 9)
            )
            jours_exc    = request.form.getlist(
                "jours_exceptionnels"
            )

            try:
                d = date.fromisoformat(date_str)
# Créer l'emploi du temps
                edt = creer_et(
                    session      = db,
                    parcours_id  = parcours_id,
                    semestre_id  = semestre_id,
                    type_session = type_session,
                    date_debut   = d
                )

                # Récupérer les matières
                matieres = db.query(
                    Matiere
                ).filter_by(
                    semestre_id=semestre_id
                ).all()

                if not matieres:
                    flash(
                        "Aucune matière pour "
                        "ce semestre.",
                        "error"
                    )
                    return redirect(
                        url_for("main.creation")
                    )

                # Lancer l'algorithme
                planning, credits, non_ass = (
                    assigner_matieres(
                        matieres,
                        date_debut = d,
                        jours_exceptionnels = jours_exc,
                        heure_debut = heure_debut
                    )
                )

                # Sauvegarder les séances
                # sur l'emploi du temps existant
                sauvegarder_en_bd(
                    session  = db,
                    planning = planning,
                    matieres = matieres,
                    edt_id   = edt.id  # ← passe l'id
                )

                # Assigner les enseignants
                assigner_enseignants(db, edt.id)

                msg = (
                    f" Emploi du temps créé ! "
                    f"(id={edt.id})"
                )
                if non_ass:
                    msg += (
                        f" — ⚠️ {len(non_ass)} "
                        f"matière(s) non assignée(s) : "
                        f"{', '.join(non_ass)}"
                    )

                flash(msg, "success")
                return redirect(
                    url_for("main.detail_et",
                            edt_id=edt.id)
                )

            except ValueError as e:
                flash(str(e), "error")

        return render_template(
            "creation.html",
            parcours_list = parcours_list,
            today         = date.today().isoformat()
        )
    finally:
        db.close()


# ═════════════════════════════════════════
# DÉTAIL D'UN EMPLOI DU TEMPS
# ═════════════════════════════════════════
@main.route("/et/<int:edt_id>")
@login_requis
def detail_et(edt_id):
    db = get_db()
    try:
        edt = db.query(EmploiDuTemps).filter_by(
            id=edt_id
        ).first()

        if not edt:
            flash(
                f"Emploi du temps #{edt_id} "
                f"introuvable.",
                "error"
            )
            return redirect(url_for("main.gestion"))

        p = db.query(Parcours).filter_by(
            id=edt.parcours_id
        ).first()
        s = db.query(Semestre).filter_by(
            id=edt.semestre_id
        ).first()

        seances_dict  = get_seances_dict(db, edt_id)
        total_seances = sum(
            len(v) for v in seances_dict.values()
        )

        return render_template(
            "detail_et.html",
            edt           = edt,
            parcours_nom  = p.nom if p else "?",
            semestre_num  = s.numero if s else "?",
            seances_dict  = seances_dict,
            total_seances = total_seances
        )
    finally:
        db.close()


# ═════════════════════════════════════════
# API — SEMESTRES PAR PARCOURS
# ═════════════════════════════════════════
@main.route(
    "/api/semestres/<int:parcours_id>"
)
@login_requis
def get_semestres(parcours_id):
    db = get_db()
    try:
        semestres = db.query(Semestre).filter_by(
            parcours_id=parcours_id
        ).all()
        return jsonify([{
            "id"    : s.id,
            "numero": s.numero
        } for s in semestres])
    finally:
        db.close()


# ═════════════════════════════════════════
# PUBLICATION
# ═════════════════════════════════════════
@main.route(
    "/publication",
    methods=["GET", "POST"]
)
@login_requis
@role_requis("cd")
def publication():
    db = get_db()
    try:
        if request.method == "POST":
            edt_id = int(request.form["edt_id"])
            try:
                edt = publier_et(db, edt_id)
                flash(
                    f" Emploi du temps publié "
                    f"le {edt.date_publication} !",
                    "success"
                )
            except ValueError as e:
                flash(str(e), "error")
            return redirect(
                url_for("main.publication")
            )

        # Emplois du temps non publiés
        ets_non_publies = db.query(
            EmploiDuTemps
        ).filter_by(
            publie=0, archive=0
        ).order_by(
            EmploiDuTemps.id.desc()
        ).all()

        ets = [
            enrichir_et(db, edt)
            for edt in ets_non_publies
        ]

        return render_template(
            "publication.html",
            ets=ets
        )
    finally:
        db.close()


# ═════════════════════════════════════════
# GESTION
# ═════════════════════════════════════════
@main.route(
    "/gestion",
    methods=["GET", "POST"]
)
@login_requis
@role_requis("cd")
def gestion():
    db = get_db()
    try:
        if request.method == "POST":
            action = request.form["action"]
            edt_id = int(request.form["edt_id"])

            try:
                if action == "archiver":
                    archiver_et(db, edt_id)
                    flash(
                        f" Emploi du temps "
                        f"archivé (id={edt_id})",
                        "success"
                    )
                elif action == "supprimer":
                    supprimer_et(db, edt_id)
                    flash(
                        f" Emploi du temps "
                        f"supprimé (id={edt_id})",
                        "success"
                    )
            except ValueError as e:
                flash(str(e), "error")

            return redirect(
                url_for("main.gestion")
            )

        ets_actifs = db.query(
            EmploiDuTemps
        ).filter_by(archive=0).order_by(
            EmploiDuTemps.id.desc()
        ).all()

        ets = [
            enrichir_et(db, edt)
            for edt in ets_actifs
        ]

        return render_template(
            "gestion.html",
            ets=ets
        )
    finally:
        db.close()


# ═════════════════════════════════════════
# CONSULTATION
# ═════════════════════════════════════════
@main.route(
    "/consultation",
    methods=["GET", "POST"]
)
@login_requis
def consultation():
    db = get_db()
    try:
        parcours_list    = db.query(Parcours).all()
        et_result        = None
        seances_dict     = {}
        searched         = False
        selected_parcours = None
        selected_semestre = None
        selected_session  = "ordinaire"
        semestres_list   = []

        if request.method == "POST":
            searched         = True
            parcours_id      = int(
                request.form["parcours_id"]
            )
            semestre_id      = int(
                request.form["semestre_id"]
            )
            type_session     = request.form[
                "type_session"
            ]
            selected_parcours = parcours_id
            selected_semestre = semestre_id
            selected_session  = type_session

            # Recharger les semestres
            semestres_list = db.query(
                Semestre
            ).filter_by(
                parcours_id=parcours_id
            ).all()

            # Chercher l'emploi du temps
            et_result = consulter_et(
                session      = db,
                parcours_id  = parcours_id,
                semestre_id  = semestre_id,
                type_session = type_session
            )

            if et_result:
                seances_dict = get_seances_dict(
                    db, et_result.id
                )

        return render_template(
            "consultation.html",
            parcours_list     = parcours_list,
            semestres_list    = semestres_list,
            et_result         = et_result,
            seances_dict      = seances_dict,
            searched          = searched,
            selected_parcours = selected_parcours,
            selected_semestre = selected_semestre,
            selected_session  = selected_session
        )
    finally:
        db.close()


# ═════════════════════════════════════════
# EXPORT EXCEL
# ═════════════════════════════════════════
@main.route("/export/excel/<int:edt_id>")
@login_requis
def export_excel(edt_id):
    db = get_db()
    try:
        from app.export import generer_excel
        chemin = generer_excel(db, edt_id)
        return send_file(
            chemin,
            as_attachment=True,
            download_name=f"ET_{edt_id}.xlsx"
        )
    except Exception as e:
        flash(str(e), "error")
        return redirect(
            url_for("main.detail_et",
                    edt_id=edt_id)
        )
    finally:
        db.close()


# ═════════════════════════════════════════
# EXPORT PDF
# ═════════════════════════════════════════
@main.route("/export/pdf/<int:edt_id>")
@login_requis
def export_pdf(edt_id):
    db = get_db()
    try:
        from app.export import generer_pdf
        chemin = generer_pdf(db, edt_id)
        return send_file(
            chemin,
            as_attachment=True,
            download_name=f"ET_{edt_id}.pdf"
        )
    except Exception as e:
        flash(str(e), "error")
        return redirect(
            url_for("main.detail_et",
                    edt_id=edt_id)
        )
    finally:
        db.close()