# app/algorithmes.py
# ─────────────────────────────────────────
# Algorithme d'assignation des matières
# Projet : Gestion EDT — Méthode XP
# Itération 2 — GEDT-03
# ─────────────────────────────────────────
import sys
import os
sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
))
from datetime import date, timedelta
from app.models import (
    Enseignant, Matiere, Semestre, Parcours,
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
            d = date(int(annee), int(mois), int(jour))

            if d < date.today():
                print(
                    " La date ne peut pas être "
                    "dans le passé."
                )
                continue

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
    R₁ : Somme crédits/jour ≥ 3 et ≤ 6
    """
    return 3.0 <= total_credits <= 6.0


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

            if nouveau_total > 6.0:

                if credit_jour[date_str] == 0.0:
                    pass  # on continue l'assignation
                else:
                    continue  # jour trop chargé

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

                # APRÈS — pause seulement si le créneau
                #          suivant a une matière
                if idx == 0 and max_mat >= 2:
                    # Vérifier que la séance 2 existe
                    if (len(creneaux) > 1
                            and creneaux[1] is not None):
                        c2_debut = horaires[1][0]
                        print(
                            f"     Pause 1h    "
                            f"({fin} → {c2_debut})"
                        )
                elif idx == 1 and max_mat == 3:
                    # Vérifier que la séance 3 existe
                    if (len(creneaux) > 2
                            and creneaux[2] is not None):
                        c3_debut = horaires[2][0]
                        print(
                            f"     Pause 45min "
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
# SAUVEGARDE EN BASE DE DONNÉES
# ═════════════════════════════════════════

def sauvegarder_en_bd(
    session,
    planning,
    matieres,
    parcours_id,
    semestre_id,
    type_session,
    date_debut
):
    """
    Sauvegarde le planning généré
    dans les tables EmploiDuTemps
    et Seance de PostgreSQL.

    Paramètres :
      session      : session SQLAlchemy
      planning     : dict du planning
      matieres     : liste objets Matiere
      parcours_id  : int
      semestre_id  : int
      type_session : "ordinaire" ou
                     "rattrapage"
      date_debut   : date Python

    Retourne :
      edt : objet EmploiDuTemps créé
    """
    from datetime import time as dt_time

    # ── 1. Créer l'EmploiDuTemps ──────────
    edt = EmploiDuTemps(
        session     =type_session,
        date_debut  =date_debut,
        parcours_id =parcours_id,
        semestre_id =semestre_id
    )
    session.add(edt)
    session.flush()
    # flush() pour récupérer edt.id

    print(
        f"\n Sauvegarde en BD..."
        f" (EmploiDuTemps id={edt.id})"
    )

    # ── Construire un index matières ──────
    # Pour retrouver une matière par son nom
    index_matieres = {
        m.nom: m for m in matieres
    }

    # ── 2. Créer les Séances ──────────────
    nb_seances = 0

    for date_str, jour_info in planning.items():
        creneaux = jour_info["creneaux"]
        horaires = jour_info["horaires"]
        nom_jour = jour_info["nom_jour"]

        for idx, matiere_etiquette in enumerate(
            creneaux
        ):
            if matiere_etiquette is None:
                continue

            # Extraire le nom de la matière
            # "Algorithmique [bleu]" → "Algorithmique"
            nom_matiere = matiere_etiquette.split(
                " ["
            )[0]

            # Retrouver l'objet Matiere
            matiere_obj = index_matieres.get(
                nom_matiere
            )
            if not matiere_obj:
                print(
                    f"   Matière introuvable "
                    f": {nom_matiere}"
                )
                continue

            # Convertir heure en objet time
            # "09h00" → time(9, 0)
            heure_str = horaires[idx][0]
            h = int(heure_str[:2])
            m = int(heure_str[3:5])
            heure_obj = dt_time(h, m)

            # Créer la séance
            # enseignant_id = None pour l'instant
            # (sera rempli par GEDT-04)
            seance = Seance(
                jour              =nom_jour,
                heure_debut       =heure_obj,
                duree             =2,
                matiere_id        =matiere_obj.id,
                enseignant_id     =1,
                emploi_du_temps_id=edt.id
            )
            session.add(seance)
            nb_seances += 1

    # ── 3. Commit final ───────────────────
    session.commit()

    print(
        f"   {nb_seances} séances "
        f"sauvegardées en BD"
    )

    return edt

# ═════════════════════════════════════════
# GEDT-04 — ASSIGNATION DES ENSEIGNANTS
# ═════════════════════════════════════════

def assigner_enseignants(
    session,
    emploi_du_temps_id
):
    """
    Assigne automatiquement chaque enseignant
    à sa séance selon la table
    enseignant_matiere.

    Pour chaque séance de l'ET :
      1. On trouve la matière
      2. On cherche l'enseignant affecté
         à cette matière dans
         enseignant_matiere
      3. On vérifie qu'il n'a pas
         de conflit horaire ce jour-là
      4. On l'assigne à la séance

    Paramètres :
      session            : SQLAlchemy session
      emploi_du_temps_id : int

    Retourne :
      nb_assignées  (int) : séances assignées
      nb_conflits   (int) : conflits détectés
      conflits      (list): détail des conflits
    """
    from app.models import EnseignantMatiere

    # ── Récupérer toutes les séances de l'ET
    seances = session.query(Seance).filter_by(
        emploi_du_temps_id=emploi_du_temps_id
    ).all()

    if not seances:
        print(" Aucune séance trouvée pour cet ET.")
        return 0, 0, []

    print(
        f"\n Assignation des enseignants..."
        f" ({len(seances)} séances)"
    )
    print("-" * 50)

    nb_assignées = 0
    nb_conflits  = 0
    conflits     = []

    # ── Construire un registre des
    #    créneaux déjà occupés par enseignant
    # Structure :
    # {enseignant_id: [(jour, heure_debut)]}
    emploi_enseignant = {}

    for seance in seances:

        # ── 1. Trouver l'enseignant
        #       pour cette matière
        affectation = session.query(
            EnseignantMatiere
        ).filter_by(
            matiere_id=seance.matiere_id
        ).first()

        if not affectation:
            print(
                f"    Aucun enseignant affecté "
                f"à la matière id="
                f"{seance.matiere_id}"
            )
            nb_conflits += 1
            conflits.append({
                "type"   : "non_affecté",
                "seance" : seance.id,
                "matiere": seance.matiere_id
            })
            continue

        ens_id = affectation.enseignant_id

        # ── 2. Vérifier conflit horaire
        if ens_id not in emploi_enseignant:
            emploi_enseignant[ens_id] = []

        creneau_actuel = (
            seance.jour,
            seance.heure_debut
        )

        if creneau_actuel in emploi_enseignant[ens_id]:
            # CONFLIT : enseignant déjà occupé
            # On cherche un remplaçant
            remplacant = _trouver_remplacant(
                session,
                seance.matiere_id,
                creneau_actuel,
                emploi_enseignant
            )

            if remplacant:
                ens_id = remplacant.id
                print(
                    f"   Conflit résolu : "
                    f"remplaçant trouvé "
                    f"pour séance {seance.id}"
                )
            else:
                print(
                    f"   Conflit non résolu : "
                    f"séance {seance.id} — "
                    f"aucun remplaçant disponible"
                )
                nb_conflits += 1
                conflits.append({
                    "type"      : "conflit",
                    "seance"    : seance.id,
                    "enseignant": ens_id,
                    "jour"      : seance.jour,
                    "heure"     : str(seance.heure_debut)
                })
                continue

        # ── 3. Assigner l'enseignant
        seance.enseignant_id = ens_id
        emploi_enseignant[ens_id].append(
            creneau_actuel
        )
        nb_assignées += 1

        # Récupérer le nom pour l'affichage
        ens_obj = session.query(
            Enseignant
        ).filter_by(id=ens_id).first()

        matiere_obj = session.query(
            Matiere
        ).filter_by(id=seance.matiere_id).first()

        print(
            f"   {matiere_obj.nom:30s}"
            f" → {ens_obj.grade} "
            f"{ens_obj.nom}"
            f" ({seance.jour})"
        )

    # ── 4. Commit
    session.commit()

    print(
        f"\n Résultat assignation :"
        f"\n   {nb_assignées} séances assignées"
        f"\n   {nb_conflits} conflits"
    )

    return nb_assignées, nb_conflits, conflits


def _trouver_remplacant(
    session,
    matiere_id,
    creneau_actuel,
    emploi_enseignant
):
    """
    Cherche un autre enseignant
    pouvant remplacer sur cette matière
    sans conflit horaire.

    Retourne :
      Enseignant disponible ou None
    """
    from app.models import EnseignantMatiere

    # Tous les enseignants pour cette matière
    toutes_affectations = session.query(
        EnseignantMatiere
    ).filter_by(
        matiere_id=matiere_id
    ).all()

    for affectation in toutes_affectations:
        ens_id = affectation.enseignant_id

        creneaux_ens = emploi_enseignant.get(
            ens_id, []
        )

        # Cet enseignant est-il libre ?
        if creneau_actuel not in creneaux_ens:
            return session.query(
                Enseignant
            ).filter_by(id=ens_id).first()

    return None





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

        # 8. Sauvegarder en BD
        reponse = input(
            "\n→ Sauvegarder en BD ? (o/n) : "
        ).strip().lower()

        if reponse == "o":
            edt = sauvegarder_en_bd(
                session     =session,
                planning    =planning,
                matieres    =matieres,
                parcours_id =parcours.id,
                semestre_id =semestre.id,
                type_session=type_session,
                date_debut  =date_debut
            )
            print(
                f"\n Emploi du temps "
                f"sauvegardé ! (id={edt.id})"
            )
        else:
            print(
                "\n  Non sauvegardé. "
                "L'ET existe seulement "
                "en mémoire."
            )
        # 9. Assigner les enseignants (GEDT-04)
        if reponse == "o":
            print(
                "\n→ Lancement de l'assignation"
                " des enseignants..."
            )
            nb_ok, nb_conf, conflits = (
                assigner_enseignants(
                    session,
                    edt.id
                )
            )

            if nb_conf > 0:
                print(
                    f"\n  {nb_conf} conflit(s) "
                    f"détecté(s) :"
                )
                for c in conflits:
                    print(f"   → {c}")

        # 10. Résumé
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