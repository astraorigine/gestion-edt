# seed.py
# ─────────────────────────────────────────
# Données de test pour la BD
# Projet : Gestion EDT — Méthode XP
# Itération 1 — GEDT-02
# ─────────────────────────────────────────
# Ce fichier insère des données réalistes
# pour pouvoir tester les algorithmes
# ─────────────────────────────────────────

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import (
    Base, Parcours, Semestre,
    TypeMatiere, Matiere,
    Enseignant
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
        # ─────────────────────────────────
        print("-> Insertion des parcours...")
        parcours_ig = Parcours(
            nom   ="Informatique ",
            niveau="Licence 2"
        )
    
        session.add(parcours_ig)
        session.flush()


        # ─────────────────────────────────
        # 2. SEMESTRES
        # ─────────────────────────────────
        print("-> Insertion des semestres...")
        semestre_1 = Semestre(
            numero     =1,
            parcours_id=parcours_ig.id
        )
        
        semestre_3 = Semestre(
            numero     =3,
            parcours_id=parcours_ig.id
        )
        semestre_4 = Semestre(
            numero     =4,
            parcours_id=parcours_ig.id
        )
        session.add_all([semestre_1, semestre_3, semestre_4])
        session.flush()

        # ─────────────────────────────────
        # 3. TYPES DE MATIÈRES (colorimétrie)
        # ─────────────────────────────────
        print("-> Insertion des types de matières...")
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
        session.add_all([
            type_bleu, type_rouge, type_jaune
        ])
        session.flush()

        # ─────────────────────────────────
        # 4. MATIÈRES
        # Règle : crédit = nb heures/semaine
        # ─────────────────────────────────
        print("-> Insertion des matières...")
        matieres = [
            Matiere(
                nom        ="Algorithmique",
                credit     =2.0,
                semestre_id=semestre_3.id,
                type_id    =type_bleu.id
            ),
            Matiere(
                nom        ="Base de données",
                credit     =2.0,
                semestre_id=semestre_3.id,
                type_id    =type_rouge.id
            ),
            Matiere(
                nom        ="Programmation Web",
                credit     =2.0,
                semestre_id=semestre_3.id,
                type_id    =type_rouge.id
            ),
            Matiere(
                nom        ="Systèmes d'information",
                credit     =1.5,
                semestre_id=semestre_3.id,
                type_id    =type_bleu.id
            ),
            Matiere(
                nom        ="Mathématiques",
                credit     =1.5,
                semestre_id=semestre_3.id,
                type_id    =type_jaune.id
            ),
            Matiere(
                nom        ="Réseaux",
                credit     =2.0,
                semestre_id=semestre_4.id,
                type_id    =type_rouge.id
            ),
            Matiere(nom="Algèbre 1", credit=2.0, semestre_id=semestre_3.id, type_id=type_bleu.id),
            Matiere(nom="TEA", credit=2.0, semestre_id=semestre_3.id, type_id=type_bleu.id),
            Matiere(nom="Web et réseau", credit=2.0, semestre_id=semestre_1.id, type_id=type_bleu.id),
            Matiere(nom="Analyse 1", credit=2.0, semestre_id=semestre_1.id, type_id=type_bleu.id),
            Matiere(nom="Société et culture", credit=2.0, semestre_id=semestre_1.id, type_id=type_bleu.id),
            Matiere(nom="Electricité", credit=2.0, semestre_id=semestre_1.id, type_id=type_bleu.id),
            Matiere(nom="Géométrie 1", credit=2.0, semestre_id=semestre_1.id, type_id=type_bleu.id),
            Matiere(nom="Comptabilité", credit=2.0, semestre_id=semestre_1.id, type_id=type_bleu.id),
            Matiere(nom="Techniques de management", credit=2.0, semestre_id=semestre_1.id, type_id=type_bleu.id),
            Matiere(nom="TEF", credit=2.0, semestre_id=semestre_1.id, type_id=type_bleu.id),
            Matiere(nom="Chimie", credit=2.0, semestre_id=semestre_1.id, type_id=type_bleu.id),
            Matiere(nom="Probabilité et Statistiques", credit=2.0, semestre_id=semestre_1.id, type_id=type_bleu.id),
            Matiere(nom="Logique de programmation", credit=2.0, semestre_id=semestre_1.id, type_id=type_bleu.id),
            Matiere(nom="Mécanique", credit=2.0, semestre_id=semestre_1.id, type_id=type_bleu.id),
            Matiere(nom="Optique", credit=2.0, semestre_id=semestre_1.id, type_id=type_bleu.id),
            Matiere(nom="Pollution", credit=2.0, semestre_id=semestre_1.id, type_id=type_bleu.id),
        ]
        session.add_all(matieres)
        session.flush()

        # ─────────────────────────────────
        # 5. ENSEIGNANTS
        # ─────────────────────────────────
        print("-> Insertion des enseignants...")
        enseignants = [
            Enseignant(
                nom   ="Nguesso",
                prenom="Albert",
                grade ="Maître de conférences"
            ),
            Enseignant(
                nom   ="Moukala",
                prenom="Sophie",
                grade ="Professeur"
            ),
            Enseignant(
                nom   ="Itoua",
                prenom="Patrick",
                grade ="Assistant"
            ),
            Enseignant( nom="BATANGOUNA", prenom="", grade="Docteur"),
            Enseignant( nom="BENAZO", prenom="V. S.", grade="Docteur"),
            Enseignant( nom="EPOUNDA", prenom="M.", grade="Professeur"),
            Enseignant( nom="MONGONDZA", prenom="", grade="Monsieur"),
            Enseignant( nom="MAVOUNGOU", prenom="", grade="Docteur"),
            Enseignant( nom="EKIAYE", prenom="ELENGA", grade="Docteur"),
            Enseignant( nom="MALONGA", prenom="MATANOU", grade="Docteur"),
            Enseignant( nom="M'BAYA", prenom="Texance", grade="Docteur"),
            Enseignant( nom="SAH", prenom="", grade="Docteur"),
            Enseignant( nom="ZABAKANI", prenom="", grade="Monsieur"),
            Enseignant( nom="MIAKAYIZILA", prenom="", grade="Docteur"),
            Enseignant( nom="KENDE", prenom="", grade="Docteur"),
            Enseignant( nom="MIZELE", prenom="KITOTI", grade="Docteur"),
            Enseignant( nom="MFOUTOU", prenom="MOUKALA", grade="Monsieur"),
            Enseignant( nom="MANKOU", prenom="BAKALA", grade="Docteur"),
            Enseignant( nom="GAMPIKA", prenom="", grade="Docteur"),
            Enseignant( nom="MABIALA", prenom="LOUBILOU", grade="Docteur"),
        ]
        session.add_all(enseignants)

        # ─────────────────────────────────
        # Enregistre tout en BD
        # ─────────────────────────────────
        session.commit()
        print("\n Toutes les données insérées !")
        print(f"   -> 1 parcours")
        print(f"   -> 2 semestres")
        print(f"   -> 3 types de matières")
        print(f"   -> {len(matieres)} matières")
        print(f"   -> {len(enseignants)} enseignants")

    except Exception as e:
        session.rollback()
        # rollback = annule tout si erreur
        print(f" Erreur : {e}")
    finally:
        session.close()


if __name__ == "__main__":
    print(" Insertion des données de test...")
    print("=" * 40)
    inserer_donnees()
    print("=" * 40)