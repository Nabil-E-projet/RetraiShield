# RetraiShield

Plateforme de qualification et d'anonymisation RGPD pour données sensibles AGIRC-ARRCO.

**🔗 Démo en ligne :** [retrai-shield.streamlit.app](https://retrai-shield.streamlit.app/)

---

## Contexte

RetraiShield se positionne dans le workflow de gestion des données de test chez AGIRC-ARRCO, entre l'extraction des données de production et leur chargement dans les environnements de recette.

```
Production → Extraction (OPTIM) → RetraiShield → Test/Recette
```

**Objectifs :**
- Qualifier automatiquement les risques RGPD des données extraites
- Mesurer le niveau d'anonymat (k-anonymité) avant chargement
- Appliquer des règles d'anonymisation paramétrables
- Générer des scripts SQL pour anonymisation directe en base

---

## Installation

### Prérequis
- Python 3.10+
- pip

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Lancement local

```bash
streamlit run app.py
```

L'application s'ouvre automatiquement à `http://localhost:8501`

---

## Fonctionnalités

### 1. Diagnostic RGPD

Analyse automatique de la sensibilité des colonnes avec classification en 4 catégories :
- **Identifiants directs** (Nom, Prénom, ID)
- **Quasi-identifiants** (Date naissance, Code postal, Sexe)
- **Données sensibles** (Revenus, Pension)
- **Données non sensibles**

**Filtres d'affichage** : Secteur d'activité, Statut (pour cibler l'analyse)

### 2. Analyse des Risques (k-anonymat)

Calcul du k-anonymat pour mesurer le risque de ré-identification :
- Sélection des quasi-identifiants à analyser
- Score de risque global (sur 100)
- Détection des personnes à haut risque (k < 5)
- Distribution graphique interactive
- **Mode comparatif** : Analyse avant/après anonymisation

### 3. Anonymisation & Export

Application de règles d'anonymisation paramétrables :
- Hash SHA256 des identifiants
- Suppression des noms/prénoms/commune
- Transformation dates → tranches d'âge
- Généralisation code postal → département
- Discrétisation revenus/pensions → tranches

**Export CSV** avec métadonnées (règles appliquées, date, k-anonymat final)

### 4. Script SQL PostgreSQL

Génération automatique de scripts SQL pour appliquer les mêmes règles d'anonymisation **directement en base de données** :
- DDL/DML production-ready (transactions, rollback)
- Fonctions PostgreSQL avancées (MD5, AGE, SUBSTRING, CASE WHEN)
- Téléchargement du script avec documentation intégrée
- Métriques sur le script généré (lignes SQL, opérations)

---

## Technologies

| Composant | Technologie |
|-----------|-------------|
| **Frontend** | Streamlit |
| **Données** | Pandas, Faker |
| **Visualisation** | Plotly |
| **SQL** | PostgreSQL (scripts générés) |
| **Déploiement** | Docker, Streamlit Cloud |

---

## Structure du Projet

```
RetraiShield/
├── app.py                  # Application Streamlit (4 onglets)
├── data_generator.py       # Génération données démo (Faker)
├── rgpd_analyzer.py        # Classification colonnes + k-anonymat
├── anonymizer.py           # Règles d'anonymisation
├── sql_generator.py        # Génération scripts PostgreSQL
├── requirements.txt        # Dépendances Python
├── Dockerfile              # Image Docker pour déploiement Linux
└── README.md
```

---

## Déploiement

### Streamlit Cloud (Production)

L'application est déployée sur : **https://retrai-shield.streamlit.app/**

Pour déployer votre propre instance :
1. Pusher le code sur GitHub
2. Connecter le repo à [share.streamlit.io](https://share.streamlit.io)
3. Sélectionner `app.py` comme point d'entrée

### Docker (Serveur interne)

Pour un déploiement sur infrastructure AGIRC-ARRCO :

```bash
# Construction de l'image
docker build -t retraishield .

# Lancement du conteneur
docker run -p 8501:8501 retraishield
```

L'application sera accessible sur `http://localhost:8501`

---

## Workflow Utilisateur

1. **Charger les données** : Upload CSV ou génération de données de démo (10k lignes)
2. **Diagnostic RGPD** : Identifier les colonnes sensibles et leur classification
3. **Analyser le risque** : Calculer le k-anonymat sur les quasi-identifiants
4. **Anonymiser** : Appliquer les règles et comparer avant/après
5. **Vérifier** : Retourner à l'analyse pour valider la réduction du risque
6. **Exporter** : Télécharger le CSV anonymisé et/ou le script SQL

---

## Note Technique

**IBM InfoSphere Optim** est l'outil standard d'extraction et de masquage de données chez AGIRC-ARRCO. RetraiShield complète cette chaîne en ajoutant une couche de **qualification RGPD** et de **contrôle qualité** avant chargement dans les environnements de test.

Le projet démontre la capacité à :
- Manipuler des datasets sensibles (retraite, finance)
- Implémenter des algorithmes de protection de la vie privée (k-anonymat)
- Générer du SQL production-ready pour PostgreSQL
- Déployer des applications data sur le cloud et en conteneurs
