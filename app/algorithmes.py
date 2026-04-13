# app/algorithmes.py
# ─────────────────────────────────────────
# Algorithme d'assignation des matières
# Projet : Gestion EDT — Méthode XP
# Itération 2 — GEDT-03
# ─────────────────────────────────────────

from datetime import date, timedelta
from models import (
    Matiere, Semestre, Parcours,
    EmploiDuTemps, Seance
)


# ═════════════════════════════════════════
# CONSTANTES
# ═════════════════════════════════════════

JOURS_SEMAINE = [
    "Lundi", "Mardi", "Mercredi",
    "Jeudi", "Vendredi", "Samedi"
]

HEURE_DEBUT_DEFAUT = 9
HEURE_FIN_DEFAUT   = 17
HEURE_PAUSE        = 13
DUREE_PAUSE_MATIN  = 60   # minutes entre séance 1 et 2
DUREE_PAUSE_3EME   = 45   # minutes avant la 3ème séance
DUREE_SEANCE       = 2    # heures


# ═════════════════════════════════════════
# ÉTAPE 0 — SÉLECTION PARCOURS / SEMESTRE
# ═════════════════════════════════════════

def selectionner_parcours_semestre(session):
    """
    Affiche les parcours et semestres
    disponibles et demande à l'utilisateur
    de choisir.

    Paramètre :
      session : session SQLAlchemy active

    Retourne :
      (parcours, semestre) choisis
      ou (None, None) si annulé
    """
    print("\n" + "=" * 50)
    print("  SÉLECTION PARCOURS / SEMESTRE")
    print("=" * 50)

    # Récupérer tous les parcours
    tous_parcours = session.query(
        Parcours
    ).all()

    if not tous_parcours:
        print(" Aucun parcours en BD.")
        print("   Lance python seed.py d'abord.")
        return None, None

    # Afficher les parcours
    print("\n Parcours disponibles :")
    for i, p in enumerate(tous_parcours, 1):
        print(f"  {i}. {p.nom} ({p.niveau})")

    # Choisir le parcours
    while True:
        try:
            choix_p = int(input(
                "\n→ Choisir le numéro du parcours : "
            ))
            if 1 <= choix_p <= len(tous_parcours):
                parcours_choisi = tous_parcours[
                    choix_p - 1
                ]
                break
            print(
                f"    Entrer un numéro "
                f"entre 1 et {len(tous_parcours)}"
            )
        except ValueError:
            print("    Entrer un nombre valide")

    # Récupérer les semestres du parcours
    semestres = session.query(Semestre).filter_by(
        parcours_id=parcours_choisi.id
    ).all()

    if not semestres:
        print(
            f" Aucun semestre pour "
            f"{parcours_choisi.nom}"
        )
        return None, None

    # Afficher les semestres
    print(
        f"\n Semestres de "
        f"{parcours_choisi.nom} :"
    )
    for i, s in enumerate(semestres, 1):
        nb = session.query(Matiere).filter_by(
            semestre_id=s.id
        ).count()
        print(
            f"  {i}. Semestre {s.numero} "
            f"({nb} matières)"
        )

    # Choisir le semestre
    while True:
        try:
            choix_s = int(input(
                "\n→ Choisir le numéro du semestre : "
            ))
            if 1 <= choix_s <= len(semestres):
                semestre_choisi = semestres[
                    choix_s - 1
                ]
                break
            print(
                f"    Entrer un numéro "
                f"entre 1 et {len(semestres)}"
            )
        except ValueError:
            print("    Entrer un nombre valide")

    print(
        f"\n Sélectionné : "
        f"{parcours_choisi.nom} — "
        f"Semestre {semestre_choisi.numero}"
    )
    return parcours_choisi, semestre_choisi


# ═════════════════════════════════════════
# ÉTAPE 0B — TYPE DE SESSION
# ═════════════════════════════════════════

def selectionner_type_session():
    """
    Demande à l'utilisateur de choisir
    le type de session.

    Retourne :
      "ordinaire" ou "rattrapage"
    """
    print("\n" + "=" * 50)
    print("  TYPE DE SESSION")
    print("=" * 50)
    print("  1. Session Ordinaire")
    print("  2. Session de Rattrapage")

    while True:
        try:
            choix = int(input(
                "\n→ Choisir le type (1 ou 2) : "
            ))
            if choix == 1:
                print(" Session : Ordinaire")
                return "ordinaire"
            elif choix == 2:
                print(" Session : Rattrapage")
                return "rattrapage"
            print("    Entrer 1 ou 2")
        except ValueError:
            print("    Entrer un nombre valide")


# ═════════════════════════════════════════
# ÉTAPE 0C — DATE DE DÉBUT
# ═════════════════════════════════════════

def selectionner_date_debut():
    """
    Demande la date de début de la session.

    Retourne :
      date Python
    """
    print("\n" + "=" * 50)
    print("  DATE DE DÉBUT DE SESSION")
    print("=" * 50)

    while True:
        try:
            saisie = input(
                "\n→ Date de début (JJ/MM/AAAA) : "
            ).strip()
            jour, mois, annee = saisie.split("/")
            d = date(
                int(annee),
                int(mois),
                int(jour)
            )
            print(f" Date de début : {d}")
            return d
        except (ValueError, TypeError):
            print(
                "    Format invalide. "
                "Exemple : 02/06/2025"
            )


# ═════════════════════════════════════════
# ÉTAPE 0D — JOURS EXCEPTIONNELS (3 épreuves)
# ═════════════════════════════════════════

def selectionner_jours_exceptionnels():
    """
    Demande quels jours peuvent
    accueillir 3 matières (cas exceptionnel).

    Retourne :
      liste de jours autorisés pour 3 matières
      ex : ["Mercredi", "Samedi"]
    """
    print("\n" + "=" * 50)
    print("  JOURS À 3 ÉPREUVES (EXCEPTIONNEL)")
    print("=" * 50)
    print(
        "  Par défaut, un jour = 2 matières max."
    )
    print(
        "  Vous pouvez autoriser 3 matières "
        "sur certains jours."
    )

    jours_choisis = []

    reponse = input(
        "\n→ Autoriser des jours à 3 épreuves ? "
        "(o/n) : "
    ).strip().lower()

    if reponse != "o":
        print(" Aucun jour exceptionnel.")
        return jours_choisis

    print("\n  Jours disponibles :")
    for i, j in enumerate(JOURS_SEMAINE, 1):
        print(f"  {i}. {j}")

    print(
        "\n  Entrer les numéros séparés par "
        "des virgules."
    )
    print("  Exemple : 3,6 pour Mercredi et Samedi")

    while True:
        try:
            saisie = input(
                "\n→ Numéros des jours : "
            ).strip()

            numeros = [
                int(n.strip())
                for n in saisie.split(",")
            ]

            jours_choisis = [
                JOURS_SEMAINE[n - 1]
                for n in numeros
                if 1 <= n <= len(JOURS_SEMAINE)
            ]

            if jours_choisis:
                print(
                    f" Jours exceptionnels : "
                    f"{', '.join(jours_choisis)}"
                )
                return jours_choisis

            print(
                "    Numéros invalides. "
                "Recommencer."
            )
        except ValueError:
            print(
                "   Format invalide. "
                "Exemple : 3,6"
            )


# ═════════════════════════════════════════
# ÉTAPE 1 — GÉNÉRATION DES CRÉNEAUX
# ═════════════════════════════════════════

def generer_creneaux(
    heure_debut=HEURE_DEBUT_DEFAUT,
    heure_fin=HEURE_FIN_DEFAUT,
    max_matieres=2
):
    """
    Génère les créneaux avec pauses.

    Cas 2 matières (normal) :
      09h-11h [pause 1h] 12h-14h

    Cas 3 matières (exceptionnel) :
      09h-11h [pause 1h] 12h-14h
              [pause 45min] 14h45-16h45

    Paramètres :
      heure_debut  : int (ex: 9)
      heure_fin    : int (ex: 17)
      max_matieres : 2 ou 3

    Retourne :
      liste de tuples (debut_str, fin_str,
                       debut_min, fin_min)
    """
    creneaux = []

    # Convertir en minutes depuis minuit
    debut_min = heure_debut * 60

    if max_matieres == 2:
        # Créneau 1
        c1_debut = debut_min
        c1_fin   = c1_debut + 120

        # Pause 1h (60 min)
        # Créneau 2
        c2_debut = c1_fin + 60
        c2_fin   = c2_debut + 120

        creneaux = [
            (
                _min_vers_heure(c1_debut),
                _min_vers_heure(c1_fin),
                c1_debut, c1_fin
            ),
            (
                _min_vers_heure(c2_debut),
                _min_vers_heure(c2_fin),
                c2_debut, c2_fin
            ),
        ]

    elif max_matieres == 3:
        # Créneau 1
        c1_debut = debut_min
        c1_fin   = c1_debut + 120

        # Pause 1h (60 min)
        # Créneau 2
        c2_debut = c1_fin + 60
        c2_fin   = c2_debut + 120

        # Pause 45 min
        # Créneau 3
        c3_debut = c2_fin + 45
        c3_fin   = c3_debut + 120

        creneaux = [
            (
                _min_vers_heure(c1_debut),
                _min_vers_heure(c1_fin),
                c1_debut, c1_fin
            ),
            (
                _min_vers_heure(c2_debut),
                _min_vers_heure(c2_fin),
                c2_debut, c2_fin
            ),
            (
                _min_vers_heure(c3_debut),
                _min_vers_heure(c3_fin),
                c3_debut, c3_fin
            ),
        ]

    return creneaux


def _min_vers_heure(minutes):
    """
    Convertit des minutes en chaîne heure.
    Ex : 540 → "09h00"
         570 → "09h30"
    """
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}h{m:02d}"


# ═════════════════════════════════════════
# ÉTAPE 2 — TRI PAR PRIORITÉ
# ═════════════════════════════════════════

def trier_matieres_par_priorite(matieres):
    """
    Trie : bleu(1) → jaune(2) → noir(3) → rouge(4)
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
# ÉTAPE 3 — VÉRIFICATIONS
# ═════════════════════════════════════════

def valider_credit_journalier(total_credits):
    """
    R₁ : Somme crédits/jour ≥ 3 et ≤ 5
    """
    return 3.0 <= total_credits <= 5.0


def créneau_est_libre(planning, date_str, idx):
    """
    Vérifie si un créneau est libre.
    Paramètres :
      planning : dict
      date_str : ex "2025-06-02"
      idx      : index du créneau (0, 1, 2)
    """
    if date_str not in planning:
        return True
    if idx >= len(planning[date_str]["creneaux"]):
        return True
    return planning[date_str]["creneaux"][idx] is None


# ═════════════════════════════════════════
# ÉTAPE 4 — ALGORITHME PRINCIPAL
# ═════════════════════════════════════════

def assigner_matieres(
    matieres,
    date_debut,
    jours_exceptionnels=None,
    heure_debut=HEURE_DEBUT_DEFAUT,
    heure_fin=HEURE_FIN_DEFAUT
):
    """
    Algorithme principal d'assignation.

    Paramètres :
      matieres           : liste de Matiere
      date_debut         : date de début
      jours_exceptionnels: jours autorisés
                           à 3 matières
      heure_debut        : int
      heure_fin          : int

    Retourne :
      planning      (dict)
      non_assignées (list)
    """
    if jours_exceptionnels is None:
        jours_exceptionnels = []

    # ── Tri par priorité ──────────────────
    matieres_triées = trier_matieres_par_priorite(
        matieres
    )

    # ── Construction du calendrier ────────
    nb_matieres     = len(matieres_triées)
    planning        = {}
    dates_ordonnées = []
    date_courante   = date_debut
    credit_jour     = {}
    nb_par_jour     = {}

    jours_generes = 0
    while jours_generes < 12:

        # ── Ignorer le dimanche ───────────
        # weekday() : 0=Lundi ... 5=Samedi
        #             6=Dimanche
        # On vérifie AVANT d'accéder
        # à JOURS_SEMAINE
        if date_courante.weekday() == 6:
            date_courante += timedelta(days=1)
            continue

        # ── Traiter le jour ───────────────
        nom_jour = JOURS_SEMAINE[
            date_courante.weekday()
        ]

        date_str = str(date_courante)
        max_mat  = (
            3 if nom_jour in jours_exceptionnels
            else 2
        )
        creneaux = generer_creneaux(
            heure_debut, heure_fin, max_mat
        )
    
        planning[date_str] = {
            "nom_jour" : nom_jour,
            "creneaux" : [None] * max_mat,
            "horaires" : creneaux,
            "max"      : max_mat
        }
        credit_jour[date_str] = 0.0
        nb_par_jour[date_str] = 0
        dates_ordonnées.append(date_str)

        jours_generes  += 1
        date_courante  += timedelta(days=1)

    # ── Assignation ───────────────────────
    non_assignées = []

    print("\n Assignation des matières...")
    print("-" * 50)

    for matiere in matieres_triées:

        if isinstance(matiere, dict):
            nom    = matiere["nom"]
            credit = matiere["credit"]
            couleur= matiere["couleur"]
        else:
            nom    = matiere.nom
            credit = matiere.credit
            couleur= matiere.type.couleur

        assignée = False

        for date_str in dates_ordonnées:
            jour_info   = planning[date_str]
            max_mat     = jour_info["max"]
            nb_actuel   = nb_par_jour[date_str]
            nouveau_total = (
                credit_jour[date_str] + credit
            )

            # Vérifier limite matières/jour
            if nb_actuel >= max_mat:
                continue

            # Vérifier limite crédit R₁
            if nouveau_total > 5.0:
                continue

            # Trouver créneau libre
            idx_libre = None
            for idx in range(max_mat):
                if créneau_est_libre(
                    planning, date_str, idx
                ):
                    idx_libre = idx
                    break

            if idx_libre is not None:
                horaire = jour_info["horaires"][idx_libre]
                etiquette = (
                    f"{nom} [{couleur}]"
                )
                planning[date_str]["creneaux"][
                    idx_libre
                ] = etiquette
                credit_jour[date_str]  += credit
                nb_par_jour[date_str]  += 1
                assignée = True

                print(
                    f"  Ok {nom:30s}"
                    f" → {jour_info['nom_jour']:10s}"
                    f" {date_str}"
                    f" {horaire[0]}-{horaire[1]}"
                    f" [{couleur}]"
                )
                break

        if not assignée:
            non_assignées.append(nom)
            print(f"   {nom} → non assignée")

    # ── Vérification R₁ ───────────────────
    print("\n Vérification R₁...")
    for date_str in dates_ordonnées:
        total = credit_jour[date_str]
        if total == 0:
            continue
        statut = (
            "Ok" if valider_credit_journalier(total)
            else " Alerte R₁: "
        )
        print(
            f"  {statut} "
            f"{planning[date_str]['nom_jour']:10s}"
            f" {date_str} : {total}h"
        )

    return planning, credit_jour, non_assignées


# ═════════════════════════════════════════
# AFFICHAGE DU PLANNING
# ═════════════════════════════════════════

def afficher_planning(
    planning,
    credit_jour,
    parcours_nom,
    semestre_num,
    type_session
):
    """
    Affiche le planning généré proprement.
    """
    print("\n" + "=" * 60)
    print(
        f"  EMPLOI DU TEMPS — {type_session.upper()}"
    )
    print(
        f"  {parcours_nom} — Semestre {semestre_num}"
    )
    print("=" * 60)

    for date_str, jour_info in planning.items():
        total = credit_jour[date_str]
        if total == 0:
            continue

        statut = (
            "Ok" if valider_credit_journalier(total)
            else "Alerte R₁: "
        )

        print(
            f"\n {jour_info['nom_jour'].upper()}"
            f" {date_str}"
            f" — {total}h {statut}"
        )
        print("-" * 50)

        creneaux  = jour_info["creneaux"]
        horaires  = jour_info["horaires"]
        max_mat   = jour_info["max"]

        for idx in range(max_mat):
            matiere = creneaux[idx]
            horaire = horaires[idx]
            debut   = horaire[0]
            fin     = horaire[1]

            if matiere is not None:
                print(
                    f"  {debut} → {fin} : "
                    f"{matiere}"
                )

                # Afficher la pause après
                if idx == 0 and max_mat >= 2:
                    c2_debut = horaires[1][0]
                    print(
                        f"    Pause 1h    "
                        f"({fin} → {c2_debut})"
                    )
                elif idx == 1 and max_mat == 3:
                    c3_debut = horaires[2][0]
                    print(
                        f"    Pause 45min "
                        f"({fin} → {c3_debut})"
                    )

    print("\n" + "=" * 60)
    print("  LÉGENDE :")
    print("  [bleu]  = Matière transversale")
    print(
        "  [jaune] = Matière anticipée "
        "(examen déjà passé)"
    )
    print("  [noir]  = Cours standard")
    print("  [rouge] = TP")
    print("=" * 60)


# ═════════════════════════════════════════
# POINT D'ENTRÉE — AVEC BD
# ═════════════════════════════════════════

if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from config import DATABASE_URL

    print("\n SYSTÈME DE GESTION DES ET")
    print("=" * 60)

    engine  = create_engine(DATABASE_URL)
    session = Session(engine)

    try:
        # 1. Choisir parcours et semestre
        parcours, semestre = (
            selectionner_parcours_semestre(session)
        )
        if not parcours:
            exit()

        # 2. Choisir le type de session
        type_session = selectionner_type_session()

        # 3. Choisir la date de début
        date_debut = selectionner_date_debut()

        # 4. Choisir les jours exceptionnels
        jours_exc = selectionner_jours_exceptionnels()

        # 5. Récupérer les matières
        matieres = (
            session
            .query(Matiere)
            .filter_by(semestre_id=semestre.id)
            .all()
        )

        if not matieres:
            print(
                f"\n Aucune matière pour "
                f"{parcours.nom} S{semestre.numero}"
            )
            exit()

        print(
            f"\n→ {len(matieres)} matières "
            f"récupérées"
        )

        # 6. Lancer l'algorithme
        planning, credits, non_ass = (
            assigner_matieres(
                matieres,
                date_debut,
                jours_exc
            )
        )

        # 7. Afficher le résultat
        afficher_planning(
            planning,
            credits,
            parcours.nom,
            semestre.numero,
            type_session
        )

        # 8. Résumé
        if non_ass:
            print(
                f"\n  Matières non assignées "
                f"({len(non_ass)}) :"
            )
            for m in non_ass:
                print(f"   → {m}")
        else:
            print(
                "\n Toutes les matières "
                "ont été assignées !"
            )

        total_jours = sum(
            1 for d, info in planning.items()
            if credits[d] > 0
        )
        print(
            f"\n Durée de la session : "
            f"{total_jours} jour(s)"
        )

    finally:
        session.close()