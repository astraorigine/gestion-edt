# tests/test_gestion_et.py
# ─────────────────────────────────────────
# Tests TDD — GEDT-05/06/07
# Gestion de l'Emploi du Temps
# Méthode XP — Itération 3
# ─────────────────────────────────────────

import sys
import os
sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
))

from datetime import date, time
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import (
    Base, EmploiDuTemps,
    Seance, Parcours, Semestre,
    Matiere
)
from config import DATABASE_URL


# ─────────────────────────────────────────
# UTILITAIRES
# ─────────────────────────────────────────

def get_session():
    """Crée une session BD pour les tests."""
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    return Session(engine)


def nettoyer_bd(session):
    """
    Supprime tous les ET et séances
    avant chaque test.

    Pourquoi ?
    → Les tests précédents ou l'algo
      ont peut-être laissé des données
    → creer_et() refuse les doublons
    → On repart d'une BD propre
    """
    session.query(Seance).delete()
    session.query(EmploiDuTemps).delete()
    session.commit()
    print("   BD nettoyée avant le test")


def get_parcours_semestre(session):
    """
    Récupère le premier parcours
    et semestre disponibles en BD.
    Retourne (parcours, semestre)
    ou (None, None) si BD vide.
    """
    semestre = session.query(
        Semestre
    ).first()

    if not semestre:
        return None, None

    parcours = session.query(
        Parcours
    ).filter_by(
        id=semestre.parcours_id
    ).first()

    return parcours, semestre


# ─────────────────────────────────────────
# TEST 1 — Création d'un ET
# ─────────────────────────────────────────
def test_creer_et():
    """
    creer_et() crée un EmploiDuTemps
    en BD avec les bons paramètres.
    publie = 0 et archive = 0 par défaut.
    """
    from app.gestion_et import creer_et

    session = get_session()

    try:
        # Nettoyage avant le test
        nettoyer_bd(session)

        parcours, semestre = (
            get_parcours_semestre(session)
        )

        if not parcours:
            print("  TEST 1 IGNORÉ : "
                  "Lance seed.py d'abord")
            return

        # Compter avant
        nb_avant = session.query(
            EmploiDuTemps
        ).count()

        # Créer l'ET
        edt = creer_et(
            session      = session,
            parcours_id  = parcours.id,
            semestre_id  = semestre.id,
            type_session = "ordinaire",
            date_debut   = date(2026, 8, 1)
        )

        # Vérifications
        nb_apres = session.query(
            EmploiDuTemps
        ).count()

        assert nb_apres == nb_avant + 1
        assert edt.id           is not None
        assert edt.session      == "ordinaire"
        assert edt.parcours_id  == parcours.id
        assert edt.semestre_id  == semestre.id
        assert edt.publie       == 0
        assert edt.archive      == 0

        print(
            f" TEST 1 PASSÉ : "
            f"ET créé (id={edt.id})"
        )

    except Exception as e:
        print(f" TEST 1 ÉCHOUÉ : {e}")
        raise
    finally:
        # Nettoyage après le test
        nettoyer_bd(session)
        session.close()


# ─────────────────────────────────────────
# TEST 2 — Publication d'un ET
# ─────────────────────────────────────────
def test_publier_et():
    """
    publier_et() :
    → publie = 1
    → date_publication = aujourd'hui
    → Échoue si ET déjà archivé
    """
    from app.gestion_et import (
        creer_et, publier_et
    )
    from app.algorithmes import (
        assigner_matieres,
        sauvegarder_en_bd
    )

    session = get_session()

    try:
        nettoyer_bd(session)

        parcours, semestre = (
            get_parcours_semestre(session)
        )

        if not parcours:
            print("  TEST 2 IGNORÉ")
            return

        # Créer l'ET
        edt = creer_et(
            session      = session,
            parcours_id  = parcours.id,
            semestre_id  = semestre.id,
            type_session = "ordinaire",
            date_debut   = date(2026, 8, 1)
        )

        # Ajouter des séances pour
        # pouvoir publier
        matieres = session.query(
            Matiere
        ).filter_by(
            semestre_id=semestre.id
        ).limit(3).all()

        if matieres:
            planning, credits, _ = (
                assigner_matieres(
                    matieres,
                    date_debut=date(2026, 8, 1),
                    jours_exceptionnels=[]
                )
            )
            # Sauvegarder les séances
            # directement sur l'ET existant
            from datetime import time as dt_time
            idx_mat = {m.nom: m for m in matieres}

            for date_str, jour_info in (
                planning.items()
            ):
                for idx, etiquette in enumerate(
                    jour_info["creneaux"]
                ):
                    if etiquette is None:
                        continue
                    nom = etiquette.split(" [")[0]
                    mat = idx_mat.get(nom)
                    if not mat:
                        continue
                    h_str = jour_info[
                        "horaires"
                    ][idx][0]
                    h = int(h_str[:2])
                    m = int(h_str[3:5])
                    seance = Seance(
                        jour=jour_info["nom_jour"],
                        heure_debut=dt_time(h, m),
                        duree=2,
                        matiere_id=mat.id,
                        enseignant_id=1,
                        emploi_du_temps_id=edt.id
                    )
                    session.add(seance)
            session.commit()

        # Vérifier non publié
        assert edt.publie == 0

        # Publier
        edt = publier_et(session, edt.id)

        # Vérifications
        assert edt.publie           == 1
        assert edt.date_publication is not None

        print(
            f" TEST 2 PASSÉ : "
            f"ET publié "
            f"(date={edt.date_publication})"
        )

    except Exception as e:
        print(f" TEST 2 ÉCHOUÉ : {e}")
        raise
    finally:
        nettoyer_bd(session)
        session.close()


# ─────────────────────────────────────────
# TEST 3 — Consultation d'un ET
# ─────────────────────────────────────────
def test_consulter_et():
    """
    consulter_et() retourne l'ET publié.
    Retourne None si non publié
    ou mauvais type de session.
    """
    from app.gestion_et import (
        creer_et, publier_et, consulter_et
    )

    session = get_session()

    try:
        nettoyer_bd(session)

        parcours, semestre = (
            get_parcours_semestre(session)
        )

        if not parcours:
            print("⚠️  TEST 3 IGNORÉ")
            return

        # Créer et publier
        edt = creer_et(
            session      = session,
            parcours_id  = parcours.id,
            semestre_id  = semestre.id,
            type_session = "ordinaire",
            date_debut   = date(2026, 8, 1)
        )

        # Ajouter 1 séance minimale
        # pour pouvoir publier
        matiere = session.query(
            Matiere
        ).filter_by(
            semestre_id=semestre.id
        ).first()

        if matiere:
            seance = Seance(
                jour               = "Lundi",
                heure_debut        = time(9, 0),
                duree              = 2,
                matiere_id         = matiere.id,
                enseignant_id      = 1,
                emploi_du_temps_id = edt.id
            )
            session.add(seance)
            session.commit()

        publier_et(session, edt.id)

        # Consulter → doit trouver
        resultat = consulter_et(
            session      = session,
            parcours_id  = parcours.id,
            semestre_id  = semestre.id,
            type_session = "ordinaire"
        )

        assert resultat is not None
        assert resultat.publie == 1

        # Consulter rattrapage → None
        resultat_ratt = consulter_et(
            session      = session,
            parcours_id  = parcours.id,
            semestre_id  = semestre.id,
            type_session = "rattrapage"
        )

        assert resultat_ratt is None

        print(
            " TEST 3 PASSÉ : "
            "Consultation ET OK"
        )

    except Exception as e:
        print(f" TEST 3 ÉCHOUÉ : {e}")
        raise
    finally:
        nettoyer_bd(session)
        session.close()


# ─────────────────────────────────────────
# TEST 4 — Modification d'une séance
# ─────────────────────────────────────────
def test_modifier_seance():
    """
    modifier_seance() met à jour
    le jour et l'heure d'une séance.
    Impossible si ET archivé.
    """
    from app.gestion_et import (
        creer_et, modifier_seance
    )

    session = get_session()

    try:
        nettoyer_bd(session)

        parcours, semestre = (
            get_parcours_semestre(session)
        )

        if not parcours:
            print("  TEST 4 IGNORÉ")
            return

        # Créer un ET
        edt = creer_et(
            session      = session,
            parcours_id  = parcours.id,
            semestre_id  = semestre.id,
            type_session = "ordinaire",
            date_debut   = date(2026, 8, 1)
        )

        # Ajouter une séance
        matiere = session.query(
            Matiere
        ).filter_by(
            semestre_id=semestre.id
        ).first()

        seance = Seance(
            jour               = "Lundi",
            heure_debut        = time(9, 0),
            duree              = 2,
            matiere_id         = matiere.id,
            enseignant_id      = 1,
            emploi_du_temps_id = edt.id
        )
        session.add(seance)
        session.commit()

        # Modifier
        nouvelle_heure = time(14, 0)
        nouveau_jour   = "Mercredi"

        seance_modifiee = modifier_seance(
            session        = session,
            seance_id      = seance.id,
            nouveau_jour   = nouveau_jour,
            nouvelle_heure = nouvelle_heure
        )

        assert seance_modifiee.jour == nouveau_jour
        assert (
            seance_modifiee.heure_debut
            == nouvelle_heure
        )

        print(" TEST 4 PASSÉ : "
              "Modification séance OK")

    except Exception as e:
        print(f" TEST 4 ÉCHOUÉ : {e}")
        raise
    finally:
        nettoyer_bd(session)
        session.close()


# ─────────────────────────────────────────
# TEST 5 — Archivage d'un ET
# ─────────────────────────────────────────
def test_archiver_et():
    """
    archiver_et() passe archive = 1.
    L'ET devient en lecture seule.
    """
    from app.gestion_et import (
        creer_et, archiver_et
    )

    session = get_session()

    try:
        nettoyer_bd(session)

        parcours, semestre = (
            get_parcours_semestre(session)
        )

        if not parcours:
            print("  TEST 5 IGNORÉ")
            return

        edt = creer_et(
            session      = session,
            parcours_id  = parcours.id,
            semestre_id  = semestre.id,
            type_session = "rattrapage",
            date_debut   = date(2026, 9, 1)
        )

        # Vérifier non archivé
        assert edt.archive == 0

        # Archiver
        edt = archiver_et(session, edt.id)

        # Vérifier archivé
        assert edt.archive == 1

        print(" TEST 5 PASSÉ : "
              "Archivage ET OK")

    except Exception as e:
        print(f" TEST 5 ÉCHOUÉ : {e}")
        raise
    finally:
        nettoyer_bd(session)
        session.close()


# ─────────────────────────────────────────
# LANCEMENT
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("\n TESTS — GEDT-05/06/07")
    print("=" * 50)

    test_creer_et()
    test_publier_et()
    test_consulter_et()
    test_modifier_seance()
    test_archiver_et()

    print("=" * 50)
    print(" Tests GEDT-05/06/07 terminés\n")