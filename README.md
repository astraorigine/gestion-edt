#  Gestion des Emplois du Temps(gestion-edt)
**Projet Fédéré — Licence II — UDSN**
Informatisation de la gestion des  emplois du temps-Méthode XP 

##  Description
Système d'informatisation de la gestion
des emplois du temps des sessions ordinaires
et de rattrapage.

**Méthode :** XP (eXtreme Programming)
**Auteur :** Team Astra
**Année :** 2025 – 2026

---

##  Stack Technique

| Composant | Technologie |
|-----------|-------------|
| Langage   | Python 3.10+ |
| Base de données | PostgreSQL 16 |
| ORM | SQLAlchemy |
| Interface | Flask (à venir) |
| Versioning | Git + GitHub |
| Gestion projet | Jira (XP) |

---

##  Installation

### Prérequis
- Python 3.10+
- PostgreSQL 16
- Git

### Étapes

```bash
# 1. Cloner le projet
git clone https://github.com/astraorigine/gestion-edt.git
cd gestion-edt

# 2. Créer l'environnement virtuel
python -m venv env

# 3. Activer l'environnement
# Windows :
env\Scripts\activate
# Mac/Linux :
source env/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Créer la base de données
psql -U postgres -c "CREATE DATABASE gestion_edt;"

# 6. Insérer les données de test
python seed.py
```

---

##  Structure du Projet
gestion-edt/
├── app/
│   ├── init.py
│   ├── models.py          : Tables BD
│   └── algorithmes.py     : Algorithmes
├── tests/
│   ├── test_models.py     : Tests BD
│   ├── test_algorithmes.py: Tests algo
│   └── test_enseignants.py: Tests GEDT-04
├── config.py              : Connexion BD
├── seed.py                : Données de test
├── requirements.txt
└── README.md

---

## Lancer les Tests

```bash
# Tests base de données
python -m tests.test_models

# Tests algorithme
python -m tests.test_algorithmes

# Tests enseignants
python -m tests.test_enseignants
```

---

##  Utilisation

```bash
# Lancer l'algorithme de génération
python -m app.algorithmes
```

L'algorithme demande :
1. Le parcours (ex : Informatique de Gestion)
2. Le semestre (ex : Semestre 3)
3. Le type de session (Ordinaire / Rattrapage)
4. La date de début (JJ/MM/AAAA)
5. Les jours exceptionnels (optionnel)

---

##  Règles Métier

| Règle | Description |
|-------|-------------|
| R₁ | Somme crédits/jour ≥ 3 et ≤ 5 |
| R₂ | Priorité : Bleu→Jaune→Noir→Rouge |
| R₃ | Durée séance = 2h exactement |

### Colorimétrie
- 🔵 **Bleu** = Matière transversale
- 🟡 **Jaune** = Matière anticipée
- ⚫ **Noir** = Cours standard
- 🔴 **Rouge** = TP

---

##  Avancement XP

| Itération | Stories | Statut |
|-----------|---------|--------|
| 1 — Base de données | GEDT-01, GEDT-02 |  Terminée |
| 2 — Algorithmes | GEDT-03, GEDT-04 |  Terminée |
| 3 — Gestion ET | GEDT-05, GEDT-06, GEDT-07 |  À venir |
| 4 — Interface | GEDT-08 |  À venir |