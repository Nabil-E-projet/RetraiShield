# RetraiShield - RGPD Data Qualification Platform

## Contexte

Outil de qualification et d'anonymisation de données pour AGIRC-ARRCO. RetraiShield se positionne dans la chaîne de traitement entre l'extraction de données et le chargement dans les environnements de test/recette.

Flux de traitement:
```
Production → Extraction (OPTIM*) → RetraiShield → Test/Recette
```

**Note:** OPTIM est l'outil d'extraction utilisé chez AGIRC-ARRCO. RetraiShield démontre la capacité à travailler avec des données extraites (CSV ou SQL) et à les qualifier avant chargement.

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

```bash
streamlit run app.py
```

L'application s'ouvre automatiquement dans votre navigateur à `http://localhost:8501`

## Fonctionnalités

### Onglet 1: Diagnostic RGPD
- Navigation latérale "Workflow"
- Filtres globaux (Secteur, Statut) pour analyse ciblée
- KPIs et indicateurs clés en haut de page
- Classification automatique des colonnes

### Onglet 2: Mesure du risque (k-anonymat)
- Calcul du k-anonymat sur quasi-identifiants sélectionnés
- Détection des personnes à haut risque (k < 5)
- Distribution graphique du k-anonymat
- Score de risque global

### Onglet 3: Anonymisation & Export
- Application de règles d'anonymisation paramétrables
- Comparaison avant/après anonymisation
- Export CSV avec métadonnées

## Structure du projet

```
RetraiShield/
├── app.py                  # Application Streamlit principale
├── data_generator.py       # Génération de données de démo
├── rgpd_analyzer.py        # Analyse RGPD et k-anonymat
├── anonymizer.py           # Règles d'anonymisation
├── requirements.txt        # Dépendances
└── README.md
```

## Technologies

- **Python / Streamlit** (Interface)
- **Pandas** (Manipulation de données)
- **SQL** (Simulation d'extraction)
- **Docker** (Conteneurisation Linux)
- **Faker** (Génération de données)

## Déploiement

### Option 1: Streamlit Cloud
1. Pusher sur GitHub
2. Connecter à share.streamlit.io

### Option 2: Docker (Linux)
Idéal pour déploiement sur serveur sécurisé AGIRC-ARRCO.

```bash
# Construction de l'image
docker build -t retraishield .

# Lancement du conteneur
docker run -p 8501:8501 retraishield
```

---

Note: IBM InfoSphere Optim est l'outil standard d'extraction et de masquage de données de production. RetraiShield complète cette chaîne en ajoutant une couche de qualification et de contrôle RGPD.
# RetraiShield
