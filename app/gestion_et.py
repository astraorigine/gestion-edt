# app/gestion_et.py
# ─────────────────────────────────────────
# Logique métier — Gestion des ET
# Projet : Gestion EDT — Méthode XP
# Itération 3 — GEDT-05/06/07
# ─────────────────────────────────────────

import sys
import os
sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
))

from datetime import date, datetime
from app.models import (
    EmploiDuTemps,
    Seance,
    Matiere,
    Parcours,
    Semestre
)


# ═════════════════════════════════════════
# GEDT-05 — CRÉER UN ET
# ═════════════════════════════════════════

def creer_et(
    session,
    parcours_id,
    semestre_id,
    type_session,
    date_debut
):
    """
    Crée un EmploiDuTemps en BD.

    Paramètres :
      session      : session SQLAlchemy
      parcours_id  : int
      semestre_id  : int
      type_session : "ordinaire" ou
                     "rattrapage"
      date_debut   : date Python

    Retourne :
      EmploiDuTemps créé
    Lève :
      ValueError si règle métier violée
    """

    # ── Règle 1 : date pas dans le passé
    if date_debut < date.today():
        raise ValueError(
            "La date de début ne peut pas "
            "être dans le passé."
        )

    # ── Règle 2 : pas de doublon
    # Un seul ET par parcours/semestre/session
    existant = session.query(
        EmploiDuTemps
    ).filter_by(
        parcours_id  = parcours_id,
        semestre_id  = semestre_id,
        session      = type_session
    ).filter(
        EmploiDuTemps.archive == 0
    ).first()

    if existant:
        raise ValueError(
            f"Un emploi du temps "
            f"{type_session} existe déjà "
            f"pour ce parcours et semestre. "
            f"(id={existant.id})"
        )

    # ── Créer l'ET ────────────────────────
    edt = EmploiDuTemps(
        session    = type_session,
        date_debut = date_debut,
        parcours_id= parcours_id,
        semestre_id= semestre_id,
        publie     = 0,
        archive    = 0
    )
    session.add(edt)
    session.commit()

    print(
        f" Emploi du Temps  créé : "
        f"{type_session} "
        f"(id={edt.id})"
    )

    return edt

# ═════════════════════════════════════════
# GEDT-05 — PUBLIER UN ET
# ═════════════════════════════════════════

def publier_et(session, edt_id):
    """
    Publie un EmploiDuTemps.
    Rend l'ET visible aux utilisateurs.

    Paramètres :
      session : session SQLAlchemy
      edt_id  : int — id de l'ET

    Retourne :
      EmploiDuTemps mis à jour
    Lève :
      ValueError si règle violée
    """

    # ── Récupérer l'ET ────────────────────
    edt = session.query(
        EmploiDuTemps
    ).filter_by(id=edt_id).first()

    if not edt:
        raise ValueError(
            f"Aucun ET trouvé (id={edt_id})"
        )

    # ── Règle : pas archivé ───────────────
    if edt.archive == 1:
        raise ValueError(
            "Impossible de publier un ET "
            "archivé."
        )

    # ── Règle : pas déjà publié ───────────
    if edt.publie == 1:
        raise ValueError(
            f"Cet ET est déjà publié "
            f"(id={edt_id})."
        )

    # ── Vérifier qu'il a des séances ──────
    nb_seances = session.query(
        Seance
    ).filter_by(
        emploi_du_temps_id=edt_id
    ).count()

    if nb_seances == 0:
        raise ValueError(
            "Impossible de publier un ET "
            "sans séances. "
            "Lance l'algorithme d'abord."
        )

    # ── Publier ───────────────────────────
    edt.publie           = 1
    edt.date_publication = date.today()

    session.commit()

    print(
        f" Emploi du Temps  publié : "
        f"id={edt_id} "
        f"(date={edt.date_publication})"
    )

    return edt

# ═════════════════════════════════════════
# GEDT-06 — MODIFIER UNE SÉANCE
# ═════════════════════════════════════════

def modifier_seance(
    session,
    seance_id,
    nouveau_jour=None,
    nouvelle_heure=None
):
    """
    Modifie le jour et/ou l'heure
    d'une séance existante.

    Paramètres :
      session        : SQLAlchemy session
      seance_id      : int
      nouveau_jour   : str ou None
      nouvelle_heure : time ou None

    Retourne :
      Seance modifiée
    Lève :
      ValueError si règle violée
    """

    # ── Récupérer la séance ───────────────
    seance = session.query(
        Seance
    ).filter_by(id=seance_id).first()

    if not seance:
        raise ValueError(
            f"Séance introuvable (id={seance_id})"
        )

    # ── Vérifier que l'ET n'est pas archivé
    edt = session.query(
        EmploiDuTemps
    ).filter_by(
        id=seance.emploi_du_temps_id
    ).first()

    if edt.archive == 1:
        raise ValueError(
            "Modification impossible : "
            "l'ET est archivé (lecture seule)."
        )

    # ── Vérifier conflit horaire ──────────
    if nouveau_jour or nouvelle_heure:
        jour_verif  = nouveau_jour  or seance.jour
        heure_verif = (
            nouvelle_heure or seance.heure_debut
        )

        conflit = session.query(
            Seance
        ).filter(
            Seance.emploi_du_temps_id
            == seance.emploi_du_temps_id,
            Seance.jour        == jour_verif,
            Seance.heure_debut == heure_verif,
            Seance.id          != seance_id
        ).first()

        if conflit:
            raise ValueError(
                f"Conflit détecté : "
                f"ce créneau est déjà occupé "
                f"({jour_verif} "
                f"{heure_verif})."
            )

    # ── Appliquer les modifications ───────
    if nouveau_jour:
        seance.jour        = nouveau_jour
    if nouvelle_heure:
        seance.heure_debut = nouvelle_heure

    session.commit()

    print(
        f" Séance modifiée : "
        f"id={seance_id} → "
        f"{seance.jour} {seance.heure_debut}"
    )

    return seance


# ═════════════════════════════════════════
# GEDT-06 — SUPPRIMER UN ET
# ═════════════════════════════════════════

def supprimer_et(session, edt_id):
    """
    Supprime un ET et toutes ses séances.
    Impossible si session active.

    Paramètres :
      session : SQLAlchemy session
      edt_id  : int

    Retourne :
      True si suppression réussie
    Lève :
      ValueError si règle violée
    """

    # ── Récupérer l'ET ────────────────────
    edt = session.query(
        EmploiDuTemps
    ).filter_by(id=edt_id).first()

    if not edt:
        raise ValueError(
            f"ET introuvable (id={edt_id})"
        )

    # ── Règle : session active = impossible
    # Une session est active si :
    # date_debut <= aujourd'hui
    # ET ET publié
    if (edt.publie == 1
            and edt.date_debut <= date.today()):
        raise ValueError(
            "Suppression impossible : "
            "la session est en cours."
        )

    # ── Supprimer séances d'abord (FK) ────
    nb_seances = session.query(
        Seance
    ).filter_by(
        emploi_du_temps_id=edt_id
    ).delete()

    # ── Supprimer l'ET ────────────────────
    session.delete(edt)
    session.commit()

    print(
        f" Emploi du Temps supprimé : id={edt_id} "
        f"({nb_seances} séances supprimées)"
    )

    return True


# ═════════════════════════════════════════
# GEDT-06 — ARCHIVER UN ET
# ═════════════════════════════════════════

def archiver_et(session, edt_id):
    """
    Archive un ET.
    L'ET devient en lecture seule.
    Reste consultable mais non modifiable.

    Paramètres :
      session : SQLAlchemy session
      edt_id  : int

    Retourne :
      EmploiDuTemps archivé
    Lève :
      ValueError si déjà archivé
    """

    edt = session.query(
        EmploiDuTemps
    ).filter_by(id=edt_id).first()

    if not edt:
        raise ValueError(
            f"ET introuvable (id={edt_id})"
        )

    if edt.archive == 1:
        raise ValueError(
            f"Cet ET est déjà archivé "
            f"(id={edt_id})."
        )

    edt.archive = 1
    session.commit()

    print(
        f" Emploi du Temps archivé : id={edt_id} "
        f"(lecture seule)"
    )

    return edt

# ═════════════════════════════════════════
# GEDT-07 — CONSULTER UN ET
# ═════════════════════════════════════════

def consulter_et(
    session,
    parcours_id,
    semestre_id,
    type_session
):
    """
    Récupère l'ET publié correspondant
    aux filtres donnés.

    Paramètres :
      session      : SQLAlchemy session
      parcours_id  : int
      semestre_id  : int
      type_session : "ordinaire" ou
                     "rattrapage"

    Retourne :
      EmploiDuTemps si trouvé et publié
      None sinon
    """

    edt = session.query(
        EmploiDuTemps
    ).filter_by(
        parcours_id = parcours_id,
        semestre_id = semestre_id,
        session     = type_session,
        publie      = 1
    ).filter(
        EmploiDuTemps.archive == 0
    ).first()

    if not edt:
        print(
            "  Aucun ET publié trouvé "
            "pour ces critères."
        )
        return None

    # Récupérer les séances de cet ET
    seances = session.query(
        Seance
    ).filter_by(
        emploi_du_temps_id=edt.id
    ).order_by(
        Seance.jour,
        Seance.heure_debut
    ).all()

    print(
        f"\n EMPLOI DU TEMPS — "
        f"{type_session.upper()}"
    )
    print(
        f"   ET id={edt.id} | "
        f"Publié le : {edt.date_publication}"
    )
    print("-" * 45)

    if not seances:
        print("  Aucune séance trouvée.")
    else:
        jour_actuel = None
        for s in seances:
            if s.jour != jour_actuel:
                print(f"\n   {s.jour.upper()}")
                jour_actuel = s.jour

            matiere = session.query(
                Matiere
            ).filter_by(id=s.matiere_id).first()

            print(
                f"    {s.heure_debut} → "
                f"{s.duree}h : "
                f"{matiere.nom}"
            )

    return edt


# ═════════════════════════════════════════
# AFFICHAGE DÉTAILLÉ D'UN ET
# ═════════════════════════════════════════

def afficher_et_complet(session, edt_id):
    """
    Affiche un ET complet avec
    toutes ses séances et enseignants.

    Paramètres :
      session : SQLAlchemy session
      edt_id  : int
    """
    from app.models import Enseignant

    edt = session.query(
        EmploiDuTemps
    ).filter_by(id=edt_id).first()

    if not edt:
        print(f" ET introuvable (id={edt_id})")
        return

    parcours = session.query(
        Parcours
    ).filter_by(id=edt.parcours_id).first()

    semestre = session.query(
        Semestre
    ).filter_by(id=edt.semestre_id).first()

    statut = (
        "Publié "    if edt.publie  == 1
        else "Brouillon "
    )
    archive = (
        " | Archivé " if edt.archive == 1
        else ""
    )

    print("\n" + "=" * 55)
    print(
        f"  EMPLOI DU TEMPS — "
        f"{edt.session.upper()}"
    )
    print(
        f"  {parcours.nom} — "
        f"Semestre {semestre.numero}"
    )
    print(f"  Statut : {statut}{archive}")
    print(
        f"  Début  : {edt.date_debut}"
    )
    if edt.date_publication:
        print(
            f"  Publié : {edt.date_publication}"
        )
    print("=" * 55)

    seances = session.query(
        Seance
    ).filter_by(
        emploi_du_temps_id=edt_id
    ).order_by(
        Seance.jour,
        Seance.heure_debut
    ).all()

    jour_actuel = None
    for s in seances:
        if s.jour != jour_actuel:
            print(f"\n  {s.jour.upper()}")
            jour_actuel = s.jour

        matiere = session.query(
            Matiere
        ).filter_by(id=s.matiere_id).first()

        enseignant = session.query(
            Enseignant
        ).filter_by(id=s.enseignant_id).first()

        ens_nom = (
            f"{enseignant.grade} "
            f"{enseignant.nom}"
            if enseignant else "Non assigné"
        )

        print(
            f"    {str(s.heure_debut)[:5]} → "
            f"{s.duree}h : "
            f"{matiere.nom:25s} "
            f"| {ens_nom}"
        )

    print("\n" + "=" * 55)