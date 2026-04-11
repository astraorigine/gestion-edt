# tests/test_algorithmes.py
# ─────────────────────────────────────────
# Tests TDD — GEDT-03
# Algorithme d'assignation des matières
# Méthode XP — Itération 2
# ─────────────────────────────────────────

import sys
import os
sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import (
    Base, Matiere, TypeMatiere,
    Parcours, Semestre
)
from config import DATABASE_URL


# ─────────────────────────────────────────
# CLASSE UTILITAIRE POUR LES TESTS
# Simule un objet Matiere sans BD
# ─────────────────────────────────────────
class MatiereSimulee:
    def __init__(self, nom, credit, couleur):
        self.nom    = nom
        self.credit = credit

        class Type:
            pass

        self.type         = Type()
        self.type.couleur = couleur

    def __repr__(self):
        return (f"<MatiereSimulee "
                f"{self.nom} "
                f"{self.credit}h "
                f"{self.type.couleur}>")


# ─────────────────────────────────────────
# TEST 1 — Import de la fonction principale
# ─────────────────────────────────────────
def test_import_algorithme():
    """
    Vérifie que toutes les fonctions
    existent dans algorithmes.py
    """
    try:
        from app.algorithmes import (
            assigner_matieres,
            valider_credit_journalier,
            trier_matieres_par_priorite,
            créneau_est_libre,
            generer_creneaux,
            initialiser_planning
        )
        print(" TEST 1 PASSÉ : "
              "Toutes les fonctions importées")
    except ImportError as e:
        print(f" TEST 1 ÉCHOUÉ : {e}")
        raise


# ─────────────────────────────────────────
# TEST 2 — Validation crédit journalier R₁
# ─────────────────────────────────────────
def test_validation_credit_journalier():
    """
    R₁ — Somme crédits/jour ≥ 3 et ≤ 5
    """
    from app.algorithmes import (
        valider_credit_journalier
    )

    # Cas VALIDES
    assert valider_credit_journalier(3.0) == True
    assert valider_credit_journalier(4.0) == True
    assert valider_credit_journalier(5.0) == True
    assert valider_credit_journalier(3.5) == True
    assert valider_credit_journalier(4.5) == True

    # Cas INVALIDES
    assert valider_credit_journalier(2.0) == False
    assert valider_credit_journalier(5.5) == False
    assert valider_credit_journalier(0.0) == False
    assert valider_credit_journalier(6.0) == False
    assert valider_credit_journalier(2.9) == False

    print(" TEST 2 PASSÉ : "
          "Validation crédit journalier OK")


# ─────────────────────────────────────────
# TEST 3 — Génération des créneaux
# ─────────────────────────────────────────
def test_generation_creneaux():
    """
    Vérifie que les créneaux sont
    générés correctement selon
    heure_debut et heure_fin.
    Pause de 1h à 13h.
    """
    from app.algorithmes import generer_creneaux

    # Test avec valeurs par défaut (09h-15h)
    creneaux = generer_creneaux(9, 15)

    assert len(creneaux) == 3
    assert creneaux[0] == "09h-11h"
    assert creneaux[1] == "11h-13h"
    assert creneaux[2] == "14h-16h"

    # Test avec autres valeurs (08h-18h)
    creneaux2 = generer_creneaux(8, 18)

    assert "08h-10h" in creneaux2
    assert "10h-12h" in creneaux2
    assert "14h-16h" in creneaux2
    assert "16h-18h" in creneaux2

    print(" TEST 3 PASSÉ : "
          "Génération créneaux OK")


# ─────────────────────────────────────────
# TEST 4 — Tri par priorité R₂
# ─────────────────────────────────────────
def test_tri_matieres_par_priorite():
    """
    R₂ — Ordre : bleu → jaune → noir → rouge
    """
    from app.algorithmes import (
        trier_matieres_par_priorite
    )

    matieres_test = [
        MatiereSimulee("TP Algo",     2.0, "rouge"),
        MatiereSimulee("Cours Std",   1.5, "noir"),
        MatiereSimulee("Transversal", 2.0, "bleu"),
        MatiereSimulee("Anticipée",   1.5, "jaune"),
        MatiereSimulee("TP Réseau",   2.0, "rouge"),
        MatiereSimulee("Transv 2",    2.0, "bleu"),
    ]

    resultat = trier_matieres_par_priorite(
        matieres_test
    )

    # Les 2 premiers → bleu
    assert resultat[0].type.couleur == "bleu"
    assert resultat[1].type.couleur == "bleu"

    # Le 3ème → jaune
    assert resultat[2].type.couleur == "jaune"

    # Le 4ème → noir
    assert resultat[3].type.couleur == "noir"

    # Les 2 derniers → rouge
    assert resultat[4].type.couleur == "rouge"
    assert resultat[5].type.couleur == "rouge"

    print(" TEST 4 PASSÉ : "
          "Tri bleu→jaune→noir→rouge OK")


# ─────────────────────────────────────────
# TEST 5 — Créneau libre
# ─────────────────────────────────────────
def test_créneau_libre():
    """
    Vérifie la détection de créneau libre.
    """
    from app.algorithmes import créneau_est_libre

    planning = {
        "Lundi": {
            "09h-11h": "Algorithmique",
            "11h-13h": None,
            "14h-16h": None,
        },
        "Mardi": {
            "09h-11h": None,
            "11h-13h": None,
            "14h-16h": None,
        }
    }

    # Créneau occupé → False
    assert créneau_est_libre(
        planning, "Lundi", "09h-11h"
    ) == False

    # Créneau libre → True
    assert créneau_est_libre(
        planning, "Lundi", "11h-13h"
    ) == True

    # Jour différent → True
    assert créneau_est_libre(
        planning, "Mardi", "09h-11h"
    ) == True

    # Jour inexistant → True
    assert créneau_est_libre(
        planning, "Jeudi", "09h-11h"
    ) == True

    print(" TEST 5 PASSÉ : "
          "Détection créneau libre OK")


# ─────────────────────────────────────────
# TEST 6 — Algorithme complet
# ─────────────────────────────────────────
def test_algorithme_complet():
    """
    Vérifie que l'algorithme assigne
    toutes les matières correctement.
    """
    from app.algorithmes import assigner_matieres

    matieres_test = [
        MatiereSimulee("Algo",    2.0, "bleu"),
        MatiereSimulee("Maths",   1.5, "jaune"),
        MatiereSimulee("Gestion", 1.5, "noir"),
        MatiereSimulee("TP BD",   2.0, "rouge"),
    ]

    planning, credits, non_ass = assigner_matieres(
        matieres_test
    )

    # Toutes assignées
    total = sum(
        1
        for jour in planning
        for cr in planning[jour]
        if planning[jour][cr] is not None
    )

    assert total == 4
    assert len(non_ass) == 0

    print(" TEST 6 PASSÉ : "
          "Algorithme complet OK")


# ─────────────────────────────────────────
# TEST 7 — R₁ respectée dans le planning
# ─────────────────────────────────────────
def test_r1_respectée():
    """
    Aucun jour ne dépasse 5h de crédits.
    """
    from app.algorithmes import assigner_matieres

    matieres_test = [
        MatiereSimulee("M1", 2.0, "bleu"),
        MatiereSimulee("M2", 2.0, "rouge"),
        MatiereSimulee("M3", 1.5, "jaune"),
        MatiereSimulee("M4", 2.0, "noir"),
        MatiereSimulee("M5", 1.5, "noir"),
    ]

    planning, credits, _ = assigner_matieres(
        matieres_test
    )

    for jour, total in credits.items():
        if total > 0:
            assert total <= 5.0, (
                f" {jour} dépasse 5h : {total}h"
            )

    print(" TEST 7 PASSÉ : "
          "R₁ respectée — aucun jour > 5h")


# ─────────────────────────────────────────
# TEST 8 — Mélanges de types par jour
# ─────────────────────────────────────────
def test_mélanges_types():
    """
    Vérifie que les mélanges de types
    sont correctement gérés.
    Ex : bleu+noir, rouge+jaune, etc.
    """
    from app.algorithmes import assigner_matieres

    matieres_test = [
        MatiereSimulee("Bleu1",  2.0, "bleu"),
        MatiereSimulee("Noir1",  1.5, "noir"),
        MatiereSimulee("Rouge1", 2.0, "rouge"),
        MatiereSimulee("Jaune1", 1.5, "jaune"),
    ]

    planning, credits, non_ass = assigner_matieres(
        matieres_test
    )

    # Aucune matière non assignée
    assert len(non_ass) == 0

    # Chaque jour avec des matières
    # doit respecter R₁
    for jour, total in credits.items():
        if total > 0:
            assert total <= 5.0

    print(" TEST 8 PASSÉ : "
          "Mélanges de types OK")


# ─────────────────────────────────────────
# LANCEMENT
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("\n TESTS — GEDT-03 Algorithmes")
    print("=" * 45)

    test_import_algorithme()
    test_validation_credit_journalier()
    test_generation_creneaux()
    test_tri_matieres_par_priorite()
    test_créneau_libre()
    test_algorithme_complet()
    test_r1_respectée()
    test_mélanges_types()

    print("=" * 45)
    print(" Tous les tests GEDT-03 terminés\n")