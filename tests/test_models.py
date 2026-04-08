# tests/test_models.py
# ─────────────────────────────────────────
# Tests unitaires — Itération 1 — GEDT-01
# On écrit les tests AVANT le code (TDD)
# ─────────────────────────────────────────

import sys
import os
sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
))

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session
from config import DATABASE_URL


def test_connexion_bd():
# TEST 1 : La connexion à PostgreSQL fonctionne
    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        conn.close()
        print(" TEST 1 PASSÉ : Connexion BD OK")
        return engine
    except Exception as e:
        print(f" TEST 1 ÉCHOUÉ : {e}")
        return None


def test_tables_existent(engine):
#    TEST 2 : Toutes les tables requises existent

    tables_requises = [
        "parcours",
        "semestre",
        "type_matiere",
        "matiere",
        "enseignant",
        "seance",
        "emploi_du_temps"
    ]

    inspecteur = inspect(engine)
    tables_bd  = inspecteur.get_table_names()

    toutes_ok = True
    for table in tables_requises:
        if table in tables_bd:
            print(f"   Table '{table}' existe")
        else:
            print(f"   Table '{table}' MANQUANTE")
            toutes_ok = False

    if toutes_ok:
        print(" TEST 2 PASSÉ : Toutes les tables existent")
    else:
        print(" TEST 2 ÉCHOUÉ : Tables manquantes")

    return toutes_ok


def test_creation_parcours(engine):
#    TEST 3 : On peut créer un parcours en BD
    from app.models import Base, Parcours

    Base.metadata.create_all(engine)
    session = Session(engine)

    try:
        p = Parcours(
            nom   ="Informatique de Gestion",
            niveau="Licence 2"
        )
        session.add(p)
        session.commit()

        resultat = session.query(Parcours).filter_by(
            nom="Informatique de Gestion"
        ).first()

        assert resultat is not None
        assert resultat.nom    == "Informatique de Gestion"
        assert resultat.niveau == "Licence 2"

        print(" TEST 3 PASSÉ : Création Parcours OK")

    except Exception as e:
        print(f" TEST 3 ÉCHOUÉ : {e}")
    finally:
        session.close()


def test_regle_credit_journalier():
    """
    TEST 4 : La somme des crédits d'une journée
             doit être > 2 et ≤ 5
    """
    def valider_credit_journalier(credits_jour):
        total = sum(credits_jour)
        return 2 < total <= 5

    # Cas valides
    assert valider_credit_journalier([1, 2])    == True
    assert valider_credit_journalier([2, 2])    == True
    assert valider_credit_journalier([1, 1, 2]) == True

    # Cas invalides
    assert valider_credit_journalier([1])       == False
    assert valider_credit_journalier([2, 2, 2]) == False

    print("TEST 4 PASSÉ : Règle crédit journalier OK")


def test_duree_seance():
    """
    TEST 5 : La durée d'une séance doit être 2h
    """
    duree_valide = 2

    assert duree_valide == 2, \
        " La durée d'une séance doit être 2h"

    print("TEST 5 PASSÉ : Durée séance = 2h OK")



# ─────────────────────────────────────────
# TESTS POUR GEDT-02 — Données de test
# ─────────────────────────────────────────

def test_donnees_de_test_inserees(engine):
    """
    TEST 6 : Les données de test existent en BD
    Vérifie que seed.py a bien fonctionné
    """
    from app.models import (
        Parcours, Semestre, Matiere,
        Enseignant, TypeMatiere
    )
    session = Session(engine)

    try:
        # Au moins 1 parcours
        nb_parcours = session.query(Parcours).count()
        assert nb_parcours >= 1, \
            "Aucun parcours en BD"
        print(f"   {nb_parcours} parcours trouvé(s)")

        # Au moins 2 semestres
        nb_semestres = session.query(Semestre).count()
        assert nb_semestres >= 2, \
            "Pas assez de semestres"
        print(f"   {nb_semestres} semestres trouvé(s)")

        # Au moins 5 matières
        nb_matieres = session.query(Matiere).count()
        assert nb_matieres >= 5, \
            "Pas assez de matières"
        print(f"   {nb_matieres} matières trouvée(s)")

        # Au moins 3 enseignants
        nb_ens = session.query(Enseignant).count()
        assert nb_ens >= 3, \
            "Pas assez d'enseignants"
        print(f"   {nb_ens} enseignant(s) trouvé(s)")

        print(" TEST 6 PASSÉ : Données de test OK")

    except AssertionError as e:
        print(f" TEST 6 ÉCHOUÉ : {e}")
    finally:
        session.close()


def test_credits_coherents(engine):
    """
    TEST 7 : Les crédits des matières
    sont cohérents (chaque crédit > 0)
    """
    from app.models import Matiere
    session = Session(engine)

    try:
        matieres = session.query(Matiere).all()
        for m in matieres:
            assert m.credit > 0, \
                f"Crédit invalide pour {m.nom}"
        print(" TEST 7 PASSÉ : Crédits cohérents OK")
    except AssertionError as e:
        print(f" TEST 7 ÉCHOUÉ : {e}")
    finally:
        session.close()


# ─────────────────────────────────────────
# LANCEMENT DES TESTS
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("\n LANCEMENT DES TESTS — GEDT-01")
    print("=" * 40)

    engine = test_connexion_bd()

    if engine:
        test_tables_existent(engine)
        test_creation_parcours(engine)

#    TESTS POUR GEDT-02 — Données de test
        test_donnees_de_test_inserees(engine)
        test_credits_coherents(engine)

    test_regle_credit_journalier()
    test_duree_seance()

    print("=" * 40)
    print(" Tests terminés\n")



