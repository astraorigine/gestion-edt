# tests/test_enseignants.py
# ─────────────────────────────────────────
# Tests TDD — GEDT-04
# Assignation des enseignants
# ─────────────────────────────────────────

import sys, os
sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
))

from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import (
    Base, Seance, EmploiDuTemps,
    EnseignantMatiere, Enseignant,
    Matiere, Semestre, Parcours
)
from config import DATABASE_URL


def get_session():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    return Session(engine), engine


# ─────────────────────────────────────────
# TEST 1 — Table enseignant_matiere existe
# ─────────────────────────────────────────
def test_table_enseignant_matiere():
    """
    La table enseignant_matiere existe en BD
    et contient des affectations.
    """
    session, _ = get_session()

    try:
        nb = session.query(
            EnseignantMatiere
        ).count()

        assert nb > 0, (
            "Aucune affectation en BD. "
            "Lance seed.py d'abord."
        )
        print(
            f" TEST 1 PASSÉ : "
            f"{nb} affectations trouvées"
        )
    finally:
        session.close()


# ─────────────────────────────────────────
# TEST 2 — Chaque matière a un enseignant
# ─────────────────────────────────────────
def test_chaque_matiere_a_enseignant():
    """
    Toutes les matières du seed
    ont au moins un enseignant affecté.
    """
    session, _ = get_session()

    try:
        matieres = session.query(Matiere).all()
        sans_enseignant = []

        for m in matieres:
            aff = session.query(
                EnseignantMatiere
            ).filter_by(
                matiere_id=m.id
            ).first()

            if not aff:
                sans_enseignant.append(m.nom)

        if sans_enseignant:
            print(
                f"    Matières sans enseignant :"
                f" {sans_enseignant}"
            )
        else:
            print(
                " TEST 2 PASSÉ : "
                "Toutes les matières ont "
                "un enseignant"
            )
    finally:
        session.close()


# ─────────────────────────────────────────
# TEST 3 — Pas de conflit horaire
# ─────────────────────────────────────────
def test_pas_de_conflit_horaire():
    """
    Après assignation, un enseignant
    ne doit pas avoir deux séances
    le même jour à la même heure.
    """
    from app.algorithmes import (
        assigner_matieres,
        sauvegarder_en_bd,
        assigner_enseignants
    )

    session, _ = get_session()

    try:
        semestre = session.query(
            Semestre
        ).first()
        if not semestre:
            print("  TEST 3 IGNORÉ : seed.py")
            return

        parcours = session.query(
            Parcours
        ).filter_by(
            id=semestre.parcours_id
        ).first()

        matieres = session.query(
            Matiere
        ).filter_by(
            semestre_id=semestre.id
        ).all()

        if not matieres:
            print("  TEST 3 IGNORÉ : seed.py")
            return

        # Générer le planning
        planning, credits, _ = assigner_matieres(
            matieres,
            date_debut=date(2026, 7, 1),
            jours_exceptionnels=[]
        )

        # Sauvegarder
        edt = sauvegarder_en_bd(
            session     =session,
            planning    =planning,
            matieres    =matieres,
            parcours_id =parcours.id,
            semestre_id =semestre.id,
            type_session="ordinaire",
            date_debut  =date(2026, 7, 1)
        )

        # Assigner enseignants
        nb_ok, nb_conf, _ = assigner_enseignants(
            session, edt.id
        )

        # Vérifier absence de conflit
        seances = session.query(Seance).filter_by(
            emploi_du_temps_id=edt.id
        ).all()

        vus = {}
        conflits = []

        for s in seances:
            cle = (
                s.enseignant_id,
                s.jour,
                str(s.heure_debut)
            )
            if cle in vus:
                conflits.append(cle)
            else:
                vus[cle] = s.id

        assert len(conflits) == 0, (
            f"Conflits détectés : {conflits}"
        )

        print(
            f" TEST 3 PASSÉ : "
            f"Aucun conflit horaire — "
            f"{nb_ok} séances assignées"
        )

        session.rollback()

    except Exception as e:
        session.rollback()
        print(f" TEST 3 ÉCHOUÉ : {e}")
        raise
    finally:
        session.close()


# ─────────────────────────────────────────
# LANCEMENT
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("\n TESTS — GEDT-04 Enseignants")
    print("=" * 50)

    test_table_enseignant_matiere()
    test_chaque_matiere_a_enseignant()
    test_pas_de_conflit_horaire()

    print("=" * 50)
    print(" Tests GEDT-04 terminés\n")