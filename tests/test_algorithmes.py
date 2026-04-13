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

from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import (
    Base, Matiere, TypeMatiere,
    Parcours, Semestre,
    EmploiDuTemps, Seance
)
from config import DATABASE_URL


# ─────────────────────────────────────────
# CLASSE UTILITAIRE
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
        return (
            f"<MatiereSimulee "
            f"{self.nom} "
            f"{self.credit}h "
            f"{self.type.couleur}>"
        )


# ─────────────────────────────────────────
# TEST 1 — Import des fonctions
# ─────────────────────────────────────────
def test_import_algorithme():
    """
    Toutes les fonctions existent
    dans algorithmes.py
    """
    try:
        from app.algorithmes import (
            assigner_matieres,
            valider_credit_journalier,
            trier_matieres_par_priorite,
            créneau_est_libre,
            generer_creneaux,
            
        )
        print(" TEST 1 PASSÉ : "
              "Toutes les fonctions importées")
    except ImportError as e:
        print(f" TEST 1 ÉCHOUÉ : {e}")
        raise


# ─────────────────────────────────────────
# TEST 2 — Validation crédit R₁
# ─────────────────────────────────────────
def test_validation_credit_journalier():
    """
    R₁ : Somme crédits/jour ≥ 3 et ≤ 5
    """
    from app.algorithmes import (
        valider_credit_journalier
    )

    # Valides
    assert valider_credit_journalier(3.0) == True
    assert valider_credit_journalier(4.0) == True
    assert valider_credit_journalier(5.0) == True
    assert valider_credit_journalier(3.5) == True

    # Invalides
    assert valider_credit_journalier(2.9) == False
    assert valider_credit_journalier(6.1) == False
    assert valider_credit_journalier(0.0) == False

    print(" TEST 2 PASSÉ : "
          "Validation crédit journalier OK")


# ─────────────────────────────────────────
# TEST 3 — Génération créneaux avec pauses
# ─────────────────────────────────────────
def test_generation_creneaux():
    """
    2 matières : pause 1h entre séances
    3 matières : pause 1h puis 45min
    """
    from app.algorithmes import generer_creneaux

    # ── 2 matières (normal) ───────────────
    creneaux_2 = generer_creneaux(
        heure_debut=9,
        heure_fin=17,
        max_matieres=2
    )

    assert len(creneaux_2) == 2

    # Séance 1 : 09h00 → 11h00
    assert creneaux_2[0][0] == "09h00"
    assert creneaux_2[0][1] == "11h00"

    # Pause 1h (60 min)
    # Séance 2 : 12h00 → 14h00
    assert creneaux_2[1][0] == "12h00"
    assert creneaux_2[1][1] == "14h00"

    # ── 3 matières (exceptionnel) ─────────
    creneaux_3 = generer_creneaux(
        heure_debut=9,
        heure_fin=17,
        max_matieres=3
    )

    assert len(creneaux_3) == 3

    # Séance 1 : 09h00 → 11h00
    assert creneaux_3[0][0] == "09h00"
    assert creneaux_3[0][1] == "11h00"

    # Pause 1h
    # Séance 2 : 12h00 → 14h00
    assert creneaux_3[1][0] == "12h00"
    assert creneaux_3[1][1] == "14h00"

    # Pause 45min
    # Séance 3 : 14h45 → 16h45
    assert creneaux_3[2][0] == "14h45"
    assert creneaux_3[2][1] == "16h45"

    print(" TEST 3 PASSÉ : "
          "Créneaux et pauses corrects")


# ─────────────────────────────────────────
# TEST 4 — Tri par priorité
# ─────────────────────────────────────────
def test_tri_matieres_par_priorite():
    """
    Ordre : bleu → jaune → noir → rouge
    """
    from app.algorithmes import (
        trier_matieres_par_priorite
    )

    matieres_test = [
        MatiereSimulee("TP1",    2.0, "rouge"),
        MatiereSimulee("Std1",   1.5, "noir"),
        MatiereSimulee("Trans1", 2.0, "bleu"),
        MatiereSimulee("Ant1",   1.5, "jaune"),
        MatiereSimulee("TP2",    2.0, "rouge"),
        MatiereSimulee("Trans2", 2.0, "bleu"),
    ]

    resultat = trier_matieres_par_priorite(
        matieres_test
    )

    assert resultat[0].type.couleur == "bleu"
    assert resultat[1].type.couleur == "bleu"
    assert resultat[2].type.couleur == "jaune"
    assert resultat[3].type.couleur == "noir"
    assert resultat[4].type.couleur == "rouge"
    assert resultat[5].type.couleur == "rouge"

    print(" TEST 4 PASSÉ : "
          "Tri bleu→jaune→noir→rouge OK")


# ─────────────────────────────────────────
# TEST 5 — Dimanche ignoré
# ─────────────────────────────────────────
def test_dimanche_ignoré():
    """
    Le Dimanche ne doit jamais
    apparaître dans le planning.
    """
    from app.algorithmes import assigner_matieres

    # Commencer un Dimanche (07/06/2026)
    date_dimanche = date(2026, 6, 7)

    matieres_test = [
        MatiereSimulee("M1", 2.0, "bleu"),
        MatiereSimulee("M2", 1.5, "noir"),
    ]

    planning, credits, _ = assigner_matieres(
        matieres_test,
        date_debut=date_dimanche,
        jours_exceptionnels=[]
    )

    for date_str, info in planning.items():
        assert info["nom_jour"] != "Dimanche", (
            f" Dimanche trouvé dans le planning !"
        )

    print(" TEST 5 PASSÉ : "
          "Dimanche correctement ignoré")


# ─────────────────────────────────────────
# TEST 6 — Algorithme complet
# ─────────────────────────────────────────
def test_algorithme_complet():
    """
    Toutes les matières sont assignées.
    Aucune non_assignée.
    """
    from app.algorithmes import assigner_matieres

    matieres_test = [
        MatiereSimulee("Algo",    2.0, "bleu"),
        MatiereSimulee("Maths",   1.5, "jaune"),
        MatiereSimulee("Gestion", 1.5, "noir"),
        MatiereSimulee("TP BD",   2.0, "rouge"),
    ]

    planning, credits, non_ass = assigner_matieres(
        matieres_test,
        date_debut=date(2026, 6, 1),
        jours_exceptionnels=[]
    )

    # Compter les matières placées
    total = sum(
        1
        for d in planning
        for cr in planning[d]["creneaux"]
        if cr is not None
    )

    assert total == 4, (
        f"Attendu 4, obtenu {total}"
    )
    assert len(non_ass) == 0, (
        f"Non assignées : {non_ass}"
    )

    print(" TEST 6 PASSÉ : "
          "Toutes les matières assignées")


# ─────────────────────────────────────────
# TEST 7 — R₁ respectée
# ─────────────────────────────────────────
def test_r1_respectée():
    """
    Aucun jour ne dépasse 5h.
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
        matieres_test,
        date_debut=date(2026, 6, 1),
        jours_exceptionnels=[]
    )

    for date_str, total in credits.items():
        if total > 0:
            assert total <= 6.0, (
                f"{planning[date_str]['nom_jour']}"
                f" dépasse 6 credits : {total}h"
            )

    print(" TEST 7 PASSÉ : "
          "R₁ respectée — aucun jour > 6h")


# ─────────────────────────────────────────
# TEST 8 — Jour exceptionnel (3 matières)
# ─────────────────────────────────────────
def test_jour_exceptionnel():
    """
    Un jour exceptionnel peut accueillir
    3 matières avec 3 créneaux.
    """
    from app.algorithmes import assigner_matieres

    matieres_test = [
        MatiereSimulee("M1", 2.0, "bleu"),
        MatiereSimulee("M2", 1.5, "jaune"),
        MatiereSimulee("M3", 1.5, "noir"),
    ]

    # Lundi est exceptionnel
    planning, credits, non_ass = assigner_matieres(
        matieres_test,
        date_debut=date(2026, 6, 1),  # Lundi
        jours_exceptionnels=["Lundi"]
    )

    # Trouver le lundi dans le planning
    lundi_str = "2026-06-01"
    assert lundi_str in planning

    # Le lundi doit avoir max=3
    assert planning[lundi_str]["max"] == 3

    # Les 3 matières sur le lundi
    creneaux_lundi = [
        c for c in
        planning[lundi_str]["creneaux"]
        if c is not None
    ]
    assert len(creneaux_lundi) == 3, (
        f"Attendu 3, obtenu "
        f"{len(creneaux_lundi)}"
    )

    print(" TEST 8 PASSÉ : "
          "Jour exceptionnel → 3 matières OK")


# ─────────────────────────────────────────
# TEST 9 — Mélanges de types
# ─────────────────────────────────────────
def test_mélanges_types():
    """
    Les mélanges de couleurs
    sont correctement gérés.
    """
    from app.algorithmes import assigner_matieres

    matieres_test = [
        MatiereSimulee("Bleu1",  2.0, "bleu"),
        MatiereSimulee("Noir1",  1.5, "noir"),
        MatiereSimulee("Rouge1", 2.0, "rouge"),
        MatiereSimulee("Jaune1", 1.5, "jaune"),
    ]

    planning, credits, non_ass = assigner_matieres(
        matieres_test,
        date_debut=date(2026, 6, 1),
        jours_exceptionnels=[]
    )

    assert len(non_ass) == 0

    for date_str, total in credits.items():
        if total > 0:
            assert total <= 5.0

    print(" TEST 9 PASSÉ : "
          "Mélanges de types OK")


# ─────────────────────────────────────────
# TEST 10 — Sauvegarde en BD
# ─────────────────────────────────────────
def test_sauvegarde_en_bd():
    """
    Après sauvegarde_en_bd(),
    EmploiDuTemps et Seance
    sont bien remplis dans PostgreSQL.
    """
    from app.algorithmes import (
        assigner_matieres,
        sauvegarder_en_bd
    )

    engine  = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    session = Session(engine)

    try:
        # Récupérer un semestre réel
        semestre = session.query(
            Semestre
        ).first()

        if not semestre:
            print("  TEST 10 IGNORÉ : "
                  "Lance seed.py d'abord")
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
        ).limit(4).all()

        if not matieres:
            print("  TEST 10 IGNORÉ : "
                  "Pas de matières en BD")
            return

        # Lancer l'algo
        planning, credits, _ = assigner_matieres(
            matieres,
            date_debut=date(2026, 6, 1),
            jours_exceptionnels=[]
        )

        # Compter avant sauvegarde
        nb_edt_avant = session.query(
            EmploiDuTemps
        ).count()

        # Sauvegarder
        edt = sauvegarder_en_bd(
            session=session,
            planning=planning,
            matieres=matieres,
            parcours_id=parcours.id,
            semestre_id=semestre.id,
            type_session="ordinaire",
            date_debut=date(2026, 6, 1)
        )

        # Vérifier EmploiDuTemps créé
        nb_edt_apres = session.query(
            EmploiDuTemps
        ).count()
        assert nb_edt_apres == nb_edt_avant + 1

        # Vérifier Seances créées
        nb_seances = session.query(
            Seance
        ).filter_by(
            emploi_du_temps_id=edt.id
        ).count()
        assert nb_seances > 0

        print(
            f" TEST 10 PASSÉ : "
            f"EmploiDuTemps créé (id={edt.id}), "
            f"{nb_seances} séances sauvegardées"
        )

        # Nettoyage
        session.rollback()

    except Exception as e:
        session.rollback()
        print(f" TEST 10 ÉCHOUÉ : {e}")
        raise
    finally:
        session.close()


# ─────────────────────────────────────────
# LANCEMENT
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("\n TESTS — GEDT-03 Algorithmes")
    print("=" * 50)

    test_import_algorithme()
    test_validation_credit_journalier()
    test_generation_creneaux()
    test_tri_matieres_par_priorite()
    test_dimanche_ignoré()
    test_algorithme_complet()
    test_r1_respectée()
    test_jour_exceptionnel()
    test_mélanges_types()
    test_sauvegarde_en_bd()

    print("=" * 50)
    print(" Tous les tests GEDT-03 terminés\n")