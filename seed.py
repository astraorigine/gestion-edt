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
        # Chaque affectation est liée à
        # un semestre précis pour éviter
        # les conflits entre parcours
        # ─────────────────────────────────
        print("→ Affectation enseignants...")

        # Index pour retrouver facilement
        idx_ens = {
            e.nom: e for e in enseignants
        }
        idx_mat = {
            (m.nom, m.semestre_id): m
            for m in matieres
        }

        # Format :
        # (nom_enseignant, nom_matiere, semestre)
        affectations_data = [

            # ── SEMESTRE 1 — IG ──────────────
            ("BATANGOUNA", "Analyse 1",       s1_ig.id),
            ("MALONGA",    "Algèbre 1",       s1_ig.id),
            ("BATANGOUNA", "Logique de prog.",s1_ig.id),
            ("M'BAYA",     "Web et Réseaux",  s1_ig.id),
            ("EKIAYE",     "Société et Culture",s1_ig.id),
            ("EKIAYE",     "TEF",             s1_ig.id),
            ("MIZELE",     "Comptabilité",    s1_ig.id),
            ("SAH",        "TP Informatique", s1_ig.id),
            ("MABIALA",    "Chimie",          s1_ig.id),

            # ── SEMESTRE 1 — Big Data ────────
            ("BATANGOUNA", "Analyse 1",       s1_bd.id),
            ("MALONGA",    "Algèbre 1",       s1_bd.id),
            ("KENDE",      "Probabilités",    s1_bd.id),
            ("M'BAYA",     "Web et Réseaux",  s1_bd.id),
            ("MFOUTOU",    "Techniques de Mgmt",s1_bd.id),
            ("EKIAYE",     "TEF",             s1_bd.id),
            ("ZABAKANI",   "TP Statistiques", s1_bd.id),

            # ── SEMESTRE 1 — Génie Logiciel ──
            ("BATANGOUNA", "Analyse 1",       s1_gl.id),
            ("MALONGA",    "Algèbre 1",       s1_gl.id),
            ("BATANGOUNA", "Logique de prog.",s1_gl.id),
            ("MANKOU",     "Génie Mécanique", s1_gl.id),
            ("MANKOU",     "Physique",        s1_gl.id),
            ("MABIALA",    "Électricité",     s1_gl.id),
            ("ZABAKANI",   "TP Programmation",s1_gl.id),

            # ── SEMESTRE 3 — IG ──────────────
            ("BATANGOUNA", "Algorithmique",    s3_ig.id),
            ("MAVOUNGOU",  "Systèmes d'info.", s3_ig.id),
            ("MONGONDZA",  "Gestion de projet",s3_ig.id),
            ("MONGONDZA",  "Communication",    s3_ig.id),
            ("EPOUNDA",    "Mathématiques",    s3_ig.id),
            ("BENAZO",     "Base de données",  s3_ig.id),
            ("BENAZO",     "Programmation Web",s3_ig.id),

            # ── SEMESTRE 3 — Big Data ────────
            ("BATANGOUNA", "Algorithmique",    s3_bd.id),
            ("MALONGA",    "Machine Learning", s3_bd.id),
            ("MIAKAYIZILA","Data Visualisation",s3_bd.id),
            ("KENDE",      "Probabilités avancées",s3_bd.id),
            ("SAH",        "TP Python Data",   s3_bd.id),

            # ── SEMESTRE 3 — Génie Logiciel ──
            ("BATANGOUNA", "Algorithmique",      s3_gl.id),
            ("MALONGA",    "Architecture logicielle",s3_gl.id),
            ("MONGONDZA",  "Gestion de projet",  s3_gl.id),
            ("GAMPIKA",    "UML avancé",         s3_gl.id),
            ("GAMPIKA",    "TP Développement",   s3_gl.id),
        ]

        affectations = []
        nb_ok = 0
        nb_ko = 0

        for nom_ens, nom_mat, sem_id in (
            affectations_data
        ):
            ens = idx_ens.get(nom_ens)
            mat = idx_mat.get((nom_mat, sem_id))

            if not ens:
                print(
                    f"   Enseignant introuvable"
                    f" : {nom_ens}"
                )
                nb_ko += 1
                continue

            if not mat:
                print(
                    f"   Matière introuvable"
                    f" : {nom_mat} "
                    f"(sem={sem_id})"
                )
                nb_ko += 1
                continue

            affectations.append(
                EnseignantMatiere(
                    enseignant_id = ens.id,
                    matiere_id    = mat.id,
                    semestre_id   = sem_id
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
                f"ignorées"
            )


          # ─────────────────────────────────
        # 6. UTILISATEURS
        # ─────────────────────────────────
        from app.models import Utilisateur
        from app.auth import hacher_mdp

        print("→ Insertion des utilisateurs...")

        utilisateurs = [
            Utilisateur(
                nom          = "Chef de Département",
                prenom       = "",
                email        = "cd@udsn.cg",
                mot_de_passe = hacher_mdp("cd123"),
                role         = "cd"
            ),
            Utilisateur(
                nom          = "Obond",
                prenom       = "Rufina",
                email        = "etudiant@udsn.cg",
                mot_de_passe = hacher_mdp("etu123"),
                role         = "etudiant"
            ),
            Utilisateur(
                nom          = "YOCO YOCO",
                prenom       = "Prince",
                email        = "prof@udsn.cg",
                mot_de_passe = hacher_mdp("prof123"),
                role         = "enseignant"
            ),
            Utilisateur(
                nom          = "François",
                prenom       = "Bombe",
                email        = "surv@udsn.cg",
                mot_de_passe = hacher_mdp("surv123"),
                role         = "surveillant"
            ),
        ]

        session.add_all(utilisateurs)


        session.commit()

        print(f"\n Toutes les données insérées !")
        print(f"   ->{len(parcours_list)} parcours "
              f"(IG, Big Data, Génie Logiciel)")
        print(f"   -> {len(semestres_list)} semestres "
              f"(S1 et S3 pour chaque parcours)")
        print(f"   -> {len(typeMatiere_list)} types de matières")
        print(f"   → {len(matieres)} matières")
        print(f"   → {len(enseignants)} enseignants")
        print(
            f"   {len(utilisateurs)} "
            f"utilisateurs créés"
        )


      

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