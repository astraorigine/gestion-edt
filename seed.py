# seed.py
# ─────────────────────────────────────────
# Données de test — Version enrichie
# Projet : Gestion EDT — Méthode XP
# Itération 1 — GEDT-02
# ─────────────────────────────────────────

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import (
    Base, Parcours, Semestre,
    TypeMatiere, Matiere, Enseignant,
    EnseignantMatiere              
)
from config import DATABASE_URL


def inserer_donnees():
    engine = create_engine(DATABASE_URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session = Session(engine)

    try:

        # ─────────────────────────────────
        # 1. PARCOURS
        # parcours pour tester les
        # matières transversales (bleues)
        # ─────────────────────────────────
        print(" Insertion des parcours...")

        parcours_ig = Parcours(
            nom   ="Informatique de Gestion",
            niveau="Licence 2"
        )
        parcours_bd = Parcours(
            nom   ="Big Data et Analyse de Données",
            niveau="Licence 2"
        )
        parcours_gl = Parcours(
            nom   ="Génie Logiciel",
            niveau="Licence 2"
        )

        parcours_list = [
            parcours_ig,
            parcours_bd,
            parcours_gl
        ]
        session.add_all(parcours_list)
        session.flush()
        print(f"  {len(parcours_list)} parcours créés")

        # ─────────────────────────────────
        # 2. SEMESTRES
        # Chaque parcours a ses semestres
        # On crée S1 et S3 pour chacun
        # ─────────────────────────────────
        print(" Insertion des semestres...")

        # Semestres — Informatique de Gestion
        s1_ig = Semestre(
            numero     =1,
            parcours_id=parcours_ig.id
        )
        s3_ig = Semestre(
            numero     =3,
            parcours_id=parcours_ig.id
        )

        # Semestres — Big Data
        s1_bd = Semestre(
            numero     =1,
            parcours_id=parcours_bd.id
        )
        s3_bd = Semestre(
            numero     =3,
            parcours_id=parcours_bd.id
        )

        # Semestres — Génie Logiciel
        s1_gl = Semestre(
            numero     =1,
            parcours_id=parcours_gl.id
        )
        s3_gl = Semestre(
            numero     =3,
            parcours_id=parcours_gl.id
        )

        semestres_list = [
            s1_ig, s3_ig,
            s1_bd, s3_bd,
            s1_gl, s3_gl
        ]
        session.add_all(semestres_list)
        session.flush()
        print(f"   {len(semestres_list)} semestres créés")

        # ─────────────────────────────────
        # 3. TYPES DE MATIÈRES
        # ─────────────────────────────────
        print("Insertion des types...")

        type_bleu  = TypeMatiere(
            libelle="Transversale",
            couleur="bleu"
        )
        type_rouge = TypeMatiere(
            libelle="TP",
            couleur="rouge"
        )
        type_jaune = TypeMatiere(
            libelle="Anticipée",
            couleur="jaune"
        )
        type_noir  = TypeMatiere(
            libelle="Cours standard",
            couleur="noir"
        )
        typeMatiere_list = [
            type_bleu, type_rouge,
            type_jaune, type_noir
        ]
        session.add_all(typeMatiere_list)
        session.flush()
        print(f"   {len(typeMatiere_list)} types créés")

        # ─────────────────────────────────
        # 4. MATIÈRES
        #
        # BLEU = transversale
        #    même matière pour tous
        #     les parcours du semestre
        #   même jour, même créneau
        #
        # JAUNE = anticipée
        #    examen déjà passé
        #    figure sur l'ET quand même
        #
        # NOIR = cours standard
        #    pas de contrainte spéciale
        #
        # ROUGE = TP
        #    le plus flexible
        # ─────────────────────────────────
        print(" Insertion des matières...")

        matieres = [

            # ══ SEMESTRE 1 ══════════════
            # Matières communes (bleues)
            # aux 3 parcours en S1
            # ────────────────────────────

            # Transversales S1 — IG
            Matiere(nom="Analyse 1",
                    credit=2.0,
                    semestre_id=s1_ig.id,
                    type_id=type_bleu.id),
            Matiere(nom="Algèbre 1",
                    credit=2.0,
                    semestre_id=s1_ig.id,
                    type_id=type_bleu.id),
            Matiere(nom="Logique de prog.",
                    credit=2.0,
                    semestre_id=s1_ig.id,
                    type_id=type_bleu.id),
            Matiere(nom="Web et Réseaux",
                    credit=2.0,
                    semestre_id=s1_ig.id,
                    type_id=type_bleu.id),
            Matiere(nom="Société et Culture",
                    credit=2.0,
                    semestre_id=s1_ig.id,
                    type_id=type_bleu.id),

            # Cours standard S1 — IG
            Matiere(nom="TEF",
                    credit=2.0,
                    semestre_id=s1_ig.id,
                    type_id=type_noir.id),
            Matiere(nom="Comptabilité",
                    credit=2.0,
                    semestre_id=s1_ig.id,
                    type_id=type_noir.id),

            # TP S1 — IG
            Matiere(nom="TP Informatique",
                    credit=2.0,
                    semestre_id=s1_ig.id,
                    type_id=type_rouge.id),

            # Anticipée S1 — IG
            Matiere(nom="Chimie",
                    credit=2.0,
                    semestre_id=s1_ig.id,
                    type_id=type_jaune.id),

            # ────────────────────────────
            # Transversales S1 — Big Data
            Matiere(nom="Analyse 1",
                    credit=2.0,
                    semestre_id=s1_bd.id,
                    type_id=type_bleu.id),
            Matiere(nom="Algèbre 1",
                    credit=2.0,
                    semestre_id=s1_bd.id,
                    type_id=type_bleu.id),
            Matiere(nom="Probabilités",
                    credit=2.0,
                    semestre_id=s1_bd.id,
                    type_id=type_bleu.id),
            Matiere(nom="Web et Réseaux",
                    credit=2.0,
                    semestre_id=s1_bd.id,
                    type_id=type_bleu.id),

            # Cours standard S1 — Big Data
            Matiere(nom="Techniques de Mgmt",
                    credit=2.0,
                    semestre_id=s1_bd.id,
                    type_id=type_noir.id),
            Matiere(nom="TEF",
                    credit=2.0,
                    semestre_id=s1_bd.id,
                    type_id=type_noir.id),

            # TP S1 — Big Data
            Matiere(nom="TP Statistiques",
                    credit=2.0,
                    semestre_id=s1_bd.id,
                    type_id=type_rouge.id),

            # ────────────────────────────
            # Transversales S1 — Génie Log.
            Matiere(nom="Analyse 1",
                    credit=2.0,
                    semestre_id=s1_gl.id,
                    type_id=type_bleu.id),
            Matiere(nom="Algèbre 1",
                    credit=2.0,
                    semestre_id=s1_gl.id,
                    type_id=type_bleu.id),
            Matiere(nom="Logique de prog.",
                    credit=2.0,
                    semestre_id=s1_gl.id,
                    type_id=type_bleu.id),

            # Cours standard S1 — Génie Log.
            Matiere(nom="Génie Mécanique",
                    credit=2.0,
                    semestre_id=s1_gl.id,
                    type_id=type_noir.id),
            Matiere(nom="Physique",
                    credit=2.0,
                    semestre_id=s1_gl.id,
                    type_id=type_noir.id),

            # Anticipée S1 — Génie Log.
            Matiere(nom="Électricité",
                    credit=2.0,
                    semestre_id=s1_gl.id,
                    type_id=type_jaune.id),

            # TP S1 — Génie Log.
            Matiere(nom="TP Programmation",
                    credit=2.0,
                    semestre_id=s1_gl.id,
                    type_id=type_rouge.id),

            # ══ SEMESTRE 3 ══════════════
            # ────────────────────────────
            # Transversales S3 — IG
            Matiere(nom="Algorithmique",
                    credit=2.0,
                    semestre_id=s3_ig.id,
                    type_id=type_bleu.id),
            Matiere(nom="Systèmes d'info.",
                    credit=1.5,
                    semestre_id=s3_ig.id,
                    type_id=type_bleu.id),

            # Cours standard S3 — IG
            Matiere(nom="Gestion de projet",
                    credit=1.5,
                    semestre_id=s3_ig.id,
                    type_id=type_noir.id),
            Matiere(nom="Communication",
                    credit=1.5,
                    semestre_id=s3_ig.id,
                    type_id=type_noir.id),

            # Anticipée S3 — IG
            Matiere(nom="Mathématiques",
                    credit=1.5,
                    semestre_id=s3_ig.id,
                    type_id=type_jaune.id),

            # TP S3 — IG
            Matiere(nom="Base de données",
                    credit=2.0,
                    semestre_id=s3_ig.id,
                    type_id=type_rouge.id),
            Matiere(nom="Programmation Web",
                    credit=2.0,
                    semestre_id=s3_ig.id,
                    type_id=type_rouge.id),

            # ────────────────────────────
            # Transversales S3 — Big Data
            Matiere(nom="Algorithmique",
                    credit=2.0,
                    semestre_id=s3_bd.id,
                    type_id=type_bleu.id),
            Matiere(nom="Machine Learning",
                    credit=2.0,
                    semestre_id=s3_bd.id,
                    type_id=type_bleu.id),

            # Cours standard S3 — Big Data
            Matiere(nom="Data Visualisation",
                    credit=1.5,
                    semestre_id=s3_bd.id,
                    type_id=type_noir.id),

            # Anticipée S3 — Big Data
            Matiere(nom="Probabilités avancées",
                    credit=1.5,
                    semestre_id=s3_bd.id,
                    type_id=type_jaune.id),

            # TP S3 — Big Data
            Matiere(nom="TP Python Data",
                    credit=2.0,
                    semestre_id=s3_bd.id,
                    type_id=type_rouge.id),

            # ────────────────────────────
            # Transversales S3 — Génie Log.
            Matiere(nom="Algorithmique",
                    credit=2.0,
                    semestre_id=s3_gl.id,
                    type_id=type_bleu.id),
            Matiere(nom="Architecture logicielle",
                    credit=2.0,
                    semestre_id=s3_gl.id,
                    type_id=type_bleu.id),

            # Cours standard S3 — Génie Log.
            Matiere(nom="Gestion de projet",
                    credit=1.5,
                    semestre_id=s3_gl.id,
                    type_id=type_noir.id),

            # Anticipée S3 — Génie Log.
            Matiere(nom="UML avancé",
                    credit=1.5,
                    semestre_id=s3_gl.id,
                    type_id=type_jaune.id),

            # TP S3 — Génie Log.
            Matiere(nom="TP Développement",
                    credit=2.0,
                    semestre_id=s3_gl.id,
                    type_id=type_rouge.id),
        ]

        session.add_all(matieres)
        session.flush()
        print(f"   {len(matieres)} matières créées")

        # ─────────────────────────────────
        # 5. ENSEIGNANTS
        # ─────────────────────────────────
        print("→ Insertion des enseignants...")

        enseignants = [
            Enseignant(nom="BATANGOUNA",
                       prenom="",
                       grade="Docteur"),
            Enseignant(nom="BENAZO",
                       prenom="V.S.",
                       grade="Docteur"),
            Enseignant(nom="EPOUNDA",
                       prenom="M.",
                       grade="Professeur"),
            Enseignant(nom="MONGONDZA",
                       prenom="",
                       grade="Monsieur"),
            Enseignant(nom="MAVOUNGOU",
                       prenom="",
                       grade="Docteur"),
            Enseignant(nom="EKIAYE",
                       prenom="ELENGA",
                       grade="Docteur"),
            Enseignant(nom="MALONGA",
                       prenom="MATANOU",
                       grade="Docteur"),
            Enseignant(nom="M'BAYA",
                       prenom="Texance",
                       grade="Docteur"),
            Enseignant(nom="SAH",
                       prenom="",
                       grade="Docteur"),
            Enseignant(nom="ZABAKANI",
                       prenom="",
                       grade="Monsieur"),
            Enseignant(nom="MIAKAYIZILA",
                       prenom="",
                       grade="Docteur"),
            Enseignant(nom="KENDE",
                       prenom="",
                       grade="Docteur"),
            Enseignant(nom="MIZELE",
                       prenom="KITOTI",
                       grade="Docteur"),
            Enseignant(nom="MFOUTOU",
                       prenom="MOUKALA",
                       grade="Monsieur"),
            Enseignant(nom="MANKOU",
                       prenom="BAKALA",
                       grade="Docteur"),
            Enseignant(nom="GAMPIKA",
                       prenom="",
                       grade="Docteur"),
            Enseignant(nom="MABIALA",
                       prenom="LOUBILOU",
                       grade="Docteur"),
        ]

        session.add_all(enseignants)
        session.flush()
        print(f"  {len(enseignants)} enseignants créés")

        # ─────────────────────────────────
        # 6. AFFECTATIONS ENSEIGNANT ↔ MATIÈRE
        # On associe chaque enseignant
        # à ses matières
        # ─────────────────────────────────
        print("→ Affectation enseignants...")

        # Construire un index pour retrouver facilement par nom
        idx_ens = {
            e.nom: e for e in enseignants
        }
        idx_mat = {
            m.nom: m for m in matieres
        }

        affectations_data = [
            # (nom_enseignant, nom_matiere)
            ("BATANGOUNA", "Algorithmique"),
            ("BATANGOUNA", "Logique de prog."),
            ("BENAZO",     "Base de données"),
            ("BENAZO",     "Programmation Web"),
            ("EPOUNDA",    "Analyse 1"),
            ("EPOUNDA",    "Mathématiques"),
            ("MONGONDZA",  "Gestion de projet"),
            ("MONGONDZA",  "Communication"),
            ("MAVOUNGOU",  "Systèmes d'info."),
            ("MAVOUNGOU",  "Machine Learning"),
            ("EKIAYE",     "TEF"),
            ("EKIAYE",     "Société et Culture"),
            ("MALONGA",    "Algèbre 1"),
            ("MALONGA",    "Architecture logicielle"),
            ("M'BAYA",     "Web et Réseaux"),
            ("M'BAYA",     "Web et Réseaux"),
            ("SAH",        "TP Python Data"),
            ("SAH",        "TP Informatique"),
            ("ZABAKANI",   "TP Statistiques"),
            ("ZABAKANI",   "TP Programmation"),
            ("MIAKAYIZILA","Data Visualisation"),
            ("KENDE",      "Probabilités"),
            ("KENDE",      "Probabilités avancées"),
            ("MIZELE",     "Comptabilité"),
            ("MFOUTOU",    "Techniques de Mgmt"),
            ("MANKOU",     "Génie Mécanique"),
            ("MANKOU",     "Physique"),
            ("GAMPIKA",    "UML avancé"),
            ("GAMPIKA",    "TP Développement"),
            ("MABIALA",    "Électricité"),
            ("MABIALA",    "Chimie"),
        ]

        affectations = []
        nb_ok  = 0
        nb_ko  = 0

        for nom_ens, nom_mat in affectations_data:
            ens = idx_ens.get(nom_ens)
            mat = idx_mat.get(nom_mat)

            if not ens:
                print(
                    f"    Enseignant introuvable "
                    f": {nom_ens}"
                )
                nb_ko += 1
                continue

            if not mat:
                print(
                    f"    Matière introuvable "
                    f": {nom_mat}"
                )
                nb_ko += 1
                continue

            affectations.append(
                EnseignantMatiere(
                    enseignant_id=ens.id,
                    matiere_id   =mat.id
                )
            )
            nb_ok += 1

        session.add_all(affectations)
        print(
            f"   {nb_ok} affectations créées"
        )
        if nb_ko > 0:
            print(
                f"   {nb_ko} affectations "
                f"non trouvées"
            )
        session.commit()

        print(f"\n Toutes les données insérées !")
        print(f"   ->{len(parcours_list)} parcours "
              f"(IG, Big Data, Génie Logiciel)")
        print(f"   -> {len(semestres_list)} semestres "
              f"(S1 et S3 pour chaque parcours)")
        print(f"   -> {len(typeMatiere_list)} types de matières")
        print(f"   → {len(matieres)} matières")
        print(f"   → {len(enseignants)} enseignants")

    except Exception as e:
        session.rollback()
        print(f" Erreur : {e}")
    finally:
        session.close()


if __name__ == "__main__":
    print(" Insertion des données de test...")
    print("=" * 45)
    inserer_donnees()
    print("=" * 45)