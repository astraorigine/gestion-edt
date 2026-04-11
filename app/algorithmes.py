# app/algorithmes.py
# ─────────────────────────────────────────
# Algorithmes d'assignation
# Projet : Gestion EDT — Méthode XP
# Itération 2 — GEDT-03
# ─────────────────────────────────────────

from models import (
    Matiere, TypeMatiere,
    Seance, EmploiDuTemps
)


# ═════════════════════════════════════════
# CONSTANTES
# ═════════════════════════════════════════

JOURS_DISPONIBLES = [
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi"
]

HEURE_DEBUT_DEFAUT = 9   # 09h
HEURE_FIN_DEFAUT   = 15  # 15h
HEURE_PAUSE        = 13  # Pause à 13h
DUREE_PAUSE        = 1   # 1h de pause
DUREE_SEANCE       = 2   # 2h par séance


# ═════════════════════════════════════════
# ÉTAPE 0 — GÉNÉRATION DES CRÉNEAUX
# ═════════════════════════════════════════

def generer_creneaux(
    heure_debut=HEURE_DEBUT_DEFAUT,
    heure_fin=HEURE_FIN_DEFAUT
):
    """
    Génère les créneaux de 2h
    entre heure_debut et heure_fin.
    Insère une pause de 1h à 13h.

    Paramètres :
      heure_debut (int) : ex 9 pour 09h
      heure_fin   (int) : ex 15 pour 15h

    Retourne :
      liste de créneaux :
      ex ["09h-11h", "11h-13h", "14h-16h"]
    """
    creneaux = []
    heure    = heure_debut

    while heure + DUREE_SEANCE <= heure_fin + DUREE_PAUSE:

        # Si on arrive à l'heure de pause
        if heure == HEURE_PAUSE:
            heure += DUREE_PAUSE
            continue

        # Si le créneau chevauche la pause
        if (heure < HEURE_PAUSE
                and heure + DUREE_SEANCE > HEURE_PAUSE):
            heure = HEURE_PAUSE
            continue

        debut = f"{heure:02d}h"
        fin   = f"{heure + DUREE_SEANCE:02d}h"
        creneaux.append(f"{debut}-{fin}")
        heure += DUREE_SEANCE

    return creneaux


# ═════════════════════════════════════════
# ÉTAPE 1 — INITIALISATION DU PLANNING
# ═════════════════════════════════════════

def initialiser_planning(
    heure_debut=HEURE_DEBUT_DEFAUT,
    heure_fin=HEURE_FIN_DEFAUT
):
    """
    Crée un planning vide.
    Tous les créneaux sont à None.

    Retourne :
      planning    (dict) : structure vide
      credit_jour (dict) : compteurs à 0
      creneaux    (list) : créneaux générés
    """
    creneaux    = generer_creneaux(
        heure_debut, heure_fin
    )
    planning    = {}
    credit_jour = {}

    for jour in JOURS_DISPONIBLES:
        planning[jour]    = {}
        credit_jour[jour] = 0.0

        for créneau in creneaux:
            planning[jour][créneau] = None

    return planning, credit_jour, creneaux


# ═════════════════════════════════════════
# ÉTAPE 2 — TRI PAR PRIORITÉ
# ═════════════════════════════════════════

def trier_matieres_par_priorite(matieres):
    """
    Trie les matières par priorité R₂ :
    bleu(1) -> jaune(2) -> noir(3) -> rouge(4)

    Paramètre :
      matieres : liste de matières
      (objets Matiere ou MatiereSimulee)

    Retourne :
      Liste triée par priorité
    """
    priorite = {
        "bleu" : 1,
        "jaune": 2,
        "noir" : 3,
        "rouge": 4
    }

    def get_priorite(matiere):
        if isinstance(matiere, dict):
            couleur = matiere["couleur"]
        else:
            couleur = matiere.type.couleur

        return priorite.get(couleur, 99)

    return sorted(matieres, key=get_priorite)


# ═════════════════════════════════════════
# ÉTAPE 3A — VÉRIFICATION CRÉNEAU LIBRE
# ═════════════════════════════════════════

def créneau_est_libre(planning, jour, heure):
    """
    Vérifie si un créneau est disponible.

    Paramètres :
      planning (dict) : planning actuel
      jour     (str)  : ex "Lundi"
      heure    (str)  : ex "09h-11h"

    Retourne :
      True  si le créneau est libre
      False si le créneau est occupé
    """
    if jour not in planning:
        return True

    if heure not in planning[jour]:
        return True

    return planning[jour][heure] is None


# ═════════════════════════════════════════
# ÉTAPE 3B — VALIDATION CRÉDIT JOURNALIER
# ═════════════════════════════════════════

def valider_credit_journalier(total_credits):
    """
    Vérifie la règle R₁ :
    Somme crédits/jour ≥ 3 et ≤ 5.

    Paramètre :
      total_credits (float) : total du jour

    Retourne :
      True  si ≥ 3 et ≤ 5
      False sinon
    """
    return 3.0 <= total_credits <= 5.0


# ═════════════════════════════════════════
# ÉTAPE 3C — PREMIER CRÉNEAU LIBRE
# ═════════════════════════════════════════

def trouver_créneau_libre(
    planning, jour, creneaux
):
    """
    Cherche le premier créneau libre
    dans un jour donné.

    Paramètres :
      planning (dict) : planning actuel
      jour     (str)  : le jour à chercher
      creneaux (list) : liste des créneaux

    Retourne :
      str  : le créneau libre trouvé
      None : si aucun n'est libre
    """
    for créneau in creneaux:
        if créneau_est_libre(
            planning, jour, créneau
        ):
            return créneau

    return None


# ═════════════════════════════════════════
# ÉTAPE 4 — ALGORITHME PRINCIPAL
# ═════════════════════════════════════════

def assigner_matieres(
    matieres,
    heure_debut=HEURE_DEBUT_DEFAUT,
    heure_fin=HEURE_FIN_DEFAUT
):
    """
    Algorithme principal d'assignation.
    Assigne chaque matière à un jour
    et un créneau horaire.

    Paramètres :
      matieres    : liste de matières
      heure_debut : heure de début (défaut 9)
      heure_fin   : heure de fin   (défaut 15)

    Retourne :
      planning      (dict) : planning rempli
      credit_jour   (dict) : crédits par jour
      non_assignées (list) : matières
                             non placées
    """

    # ── Initialisation ────────────────────
    planning, credit_jour, creneaux = (
        initialiser_planning(
            heure_debut, heure_fin
        )
    )
    non_assignées = []

    # ── Tri par priorité ──────────────────
    matieres_triées = trier_matieres_par_priorite(
        matieres
    )

    print("\n Assignation des matières...")
    print("-" * 40)

    # ── Assignation ───────────────────────
    for matiere in matieres_triées:

        # Récupérer la couleur
        if isinstance(matiere, dict):
            couleur = matiere["couleur"]
            nom     = matiere["nom"]
            credit  = matiere["credit"]
        else:
            couleur = matiere.type.couleur
            nom     = matiere.nom
            credit  = matiere.credit

        assignée = False

        for jour in JOURS_DISPONIBLES:

            nouveau_total = (
                credit_jour[jour] + credit
            )

            # Vérifier limite haute R₁
            if nouveau_total > 5.0:
                continue

            # Chercher un créneau libre
            créneau = trouver_créneau_libre(
                planning, jour, creneaux
            )

            if créneau is not None:

                # Construire l'étiquette
                # avec la couleur
                etiquette = (
                    f"{nom} [{couleur}]"
                )

                # Assigner
                planning[jour][créneau] = (
                    etiquette
                )
                credit_jour[jour] += credit
                assignée = True

                print(
                    f"   {nom:25s}"
                    f" → {jour:10s}"
                    f" {créneau}"
                    f" [{couleur}]"
                )
                break

        if not assignée:
            non_assignées.append(nom)
            print(f"    {nom} → non assignée")

    # ── Vérification finale R₁ ────────────
    print("\n Vérification R₁...")
    for jour in JOURS_DISPONIBLES:
        total = credit_jour[jour]
        if total == 0:
            continue
        if total < 3.0:
            print(
                f"    {jour} : {total}h "
                f"< 3h (R₁ non respectée)"
            )
        else:
            print(
                f"   {jour} : {total}h"
            )

    return planning, credit_jour, non_assignées


# ═════════════════════════════════════════
# AFFICHAGE DU PLANNING
# ═════════════════════════════════════════

def afficher_planning(planning, credit_jour):
    """
    Affiche le planning généré
    de façon lisible et colorée.
    """
    print("\n" + "=" * 50)
    print("      EMPLOI DU TEMPS GÉNÉRÉ")
    print("=" * 50)

    for jour in JOURS_DISPONIBLES:
        total = credit_jour[jour]

        if total == 0:
            continue

        statut = "OK" if valider_credit_journalier(
            total
        ) else "  R₁ non respectée"

        print(
            f"\n {jour.upper()}"
            f" — {total}h {statut}"
        )
        print("-" * 40)

        for créneau, matiere in (
            planning[jour].items()
        ):
            if matiere is not None:
                print(
                    f"  {créneau} : {matiere}"
                )

    print("\n" + "=" * 50)
    print("  LÉGENDE :")
    print("  [bleu]  = Matière transversale")
    print("  [jaune] = Matière anticipée")
    print("  [noir]  = Cours standard")
    print("  [rouge] = TP")
    print("=" * 50)


# ═════════════════════════════════════════
# TEST RAPIDE AVEC LA BD
# ═════════════════════════════════════════

if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from config import DATABASE_URL

    print(" Lancement de l'algorithme...")
    print("=" * 50)

    engine  = create_engine(DATABASE_URL)
    session = Session(engine)

    try:
        matieres = (
            session
            .query(Matiere)
            .filter_by(semestre_id=1)
            .all()
        )

        if not matieres:
            print(" Aucune matière en BD.")
            print("   Lance python seed.py")
        else:
            print(
                f"→ {len(matieres)} matières"
                f" récupérées depuis la BD"
            )

            planning, credits, non_ass = (
                assigner_matieres(matieres)
            )

            afficher_planning(
                planning, credits
            )

            if non_ass:
                print(
                    f"\n  Matières non assignées :"
                    f" {non_ass}"
                )
            else:
                print(
                    "\n Toutes les matières"
                    " ont été assignées !"
                )

    finally:
        session.close()