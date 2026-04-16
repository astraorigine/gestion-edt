# app/models.py
# ─────────────────────────────────────────
# Modèles de la base de données
# Projet : Gestion EDT — Méthode XP
# Itération 1 — GEDT-01
# ─────────────────────────────────────────

from sqlalchemy import (
    Column, Integer, String,
    Float, ForeignKey, Enum, Time, Date
)
from sqlalchemy.orm import (
    declarative_base, relationship
)
from sqlalchemy import create_engine
import sys, os
sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
))
from config import DATABASE_URL

Base = declarative_base()


# ─────────────────────────────────────────
# TABLE : Parcours
# Ex : Licence 2 Informatique de Gestion
# ─────────────────────────────────────────
class Parcours(Base):
    __tablename__ = "parcours"

    id     = Column(Integer, primary_key=True,
                    autoincrement=True)
    nom    = Column(String(100), nullable=False)
    niveau = Column(String(50),  nullable=False)

    semestres = relationship(
        "Semestre", back_populates="parcours"
    )

    def __repr__(self):
        return f"<Parcours {self.nom} — {self.niveau}>"


# ─────────────────────────────────────────
# TABLE : Semestre(1,2,3,4,5,6)
# ─────────────────────────────────────────
class Semestre(Base):
    __tablename__ = "semestre"

    id          = Column(Integer, primary_key=True,
                         autoincrement=True)
    numero      = Column(Integer, nullable=False)
    parcours_id = Column(Integer,
                         ForeignKey("parcours.id"),
                         nullable=False)

    parcours  = relationship(
        "Parcours", back_populates="semestres"
    )
    matieres  = relationship(
        "Matiere", back_populates="semestre"
    )

    def __repr__(self):
        return f"<Semestre {self.numero}>"


# ─────────────────────────────────────────
# TABLE : TypeMatiere
# Colorimétrie :
#   bleu  = matière transversale
#   rouge = TP
#   jaune = matière anticipée
# ─────────────────────────────────────────
class TypeMatiere(Base):
    __tablename__ = "type_matiere"

    id      = Column(Integer, primary_key=True,
                     autoincrement=True)
    libelle = Column(String(50),  nullable=False)
    couleur = Column(
        Enum("bleu", "rouge", "jaune","noir",
             name="couleur_enum"),
        nullable=False
    )

    matieres = relationship(
        "Matiere", back_populates="type"
    )

    def __repr__(self):
        return f"<TypeMatiere {self.libelle} — {self.couleur}>"


# ─────────────────────────────────────────
# TABLE : Matiere
# credit = nb heures hebdomadaires
# Règle : somme crédits/jour > 2 et ≤ 5
# ─────────────────────────────────────────
class Matiere(Base):
    __tablename__ = "matiere"

    id          = Column(Integer, primary_key=True,
                         autoincrement=True)
    nom         = Column(String(100), nullable=False)
    credit      = Column(Float,       nullable=False)
    semestre_id = Column(Integer,
                         ForeignKey("semestre.id"),
                         nullable=False)
    type_id     = Column(Integer,
                         ForeignKey("type_matiere.id"),
                         nullable=False)

    semestre = relationship(
        "Semestre", back_populates="matieres"
    )
    type     = relationship(
        "TypeMatiere", back_populates="matieres"
    )

    def __repr__(self):
        return f"<Matiere {self.nom} — {self.credit}h>"


# ─────────────────────────────────────────
# TABLE : Enseignant
# ─────────────────────────────────────────
class Enseignant(Base):
    __tablename__ = "enseignant"

    id     = Column(Integer, primary_key=True,
                    autoincrement=True)
    nom    = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    grade  = Column(String(50))

    def __repr__(self):
        return f"<Enseignant {self.nom} {self.prenom}>"
    

# ─────────────────────────────────────────
# TABLE : EnseignantMatiere
# ─────────────────────────────────────────
"""
 Lien entre enseignant et matière(s)
 Un enseignant peut enseigner plusieurs matières, une matière peut être enseignée
 par plusieurs enseignants
"""
class EnseignantMatiere(Base):
    __tablename__ = "enseignant_matiere"

    id            = Column(
        Integer, primary_key=True,
        autoincrement=True
    )
    enseignant_id = Column(
        Integer,
        ForeignKey("enseignant.id"),
        nullable=False
    )
    matiere_id    = Column(
        Integer,
        ForeignKey("matiere.id"),
        nullable=False
    )

    enseignant = relationship("Enseignant")
    matiere    = relationship("Matiere")

    def __repr__(self):
        return (
            f"<EnseignantMatiere "
            f"ens={self.enseignant_id} "
            f"mat={self.matiere_id}>"
        )


# ─────────────────────────────────────────
# TABLE : EmploiDuTemps
# session : "ordinaire" ou "rattrapage"
# ─────────────────────────────────────────
class EmploiDuTemps(Base):
    __tablename__ = "emploi_du_temps"

    id               = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    session          = Column(
        Enum("ordinaire", "rattrapage",
             name="session_enum"),
        nullable=False
    )
    date_debut       = Column(
        Date,
        nullable=False
    )
    parcours_id      = Column(
        Integer,
        ForeignKey("parcours.id"),
        nullable=False
    )
    semestre_id      = Column(
        Integer,
        ForeignKey("semestre.id"),
        nullable=False
    )

    # ── Champs nécessaires pour le GEDT-05 ───────────────────
    publie           = Column(
        Integer,
        default=0,
        nullable=False
    )
    # 0 = non publié, 1 = publié

    date_publication = Column(
        Date,
        nullable=True
    )
    # None tant que non publié

    archive          = Column(
        Integer,
        default=0,
        nullable=False
    )
    # 0 = actif, 1 = archivé

    seances = relationship(
        "Seance",
        back_populates="emploi_du_temps"
    )

    def __repr__(self):
        statut = (
            "publié"  if self.publie  == 1
            else "brouillon"
        )
        return (
            f"<EmploiDuTemps "
            f"{self.session} — {statut}>"
        )

# ─────────────────────────────────────────
# TABLE : Seance
# ─────────────────────────────────────────
class Seance(Base):
    __tablename__ = "seance"

    id                = Column(Integer,
                                primary_key=True,
                                autoincrement=True)
    jour              = Column(String(20),
                                nullable=False)
    heure_debut       = Column(Time, nullable=False)
    duree             = Column(Integer,
                                default=2,
                                nullable=False)
    # duree = toujours 2h (règle projet)

    matiere_id        = Column(Integer,
                                ForeignKey("matiere.id"),
                                nullable=False)
    enseignant_id     = Column(Integer,
                                ForeignKey("enseignant.id"),
                                nullable=False)
    emploi_du_temps_id= Column(Integer,
                                ForeignKey(
                                "emploi_du_temps.id"),
                                nullable=False)

    emploi_du_temps = relationship(
        "EmploiDuTemps", back_populates="seances"
    )

    def __repr__(self):
        return (f"<Seance {self.jour} "
                f"{self.heure_debut} — "
                f"{self.duree}h>")


# ─────────────────────────────────────────
# CRÉATION DES TABLES
# ─────────────────────────────────────────
def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print(" Toutes les tables créées !")
    return engine


if __name__ == "__main__":
    init_db()