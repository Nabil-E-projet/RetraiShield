# 🛡️ RetraiShield - Plateforme d'Anonymisation RGPD

**Démonstration complète d'anonymisation de données personnelles conforme RGPD.**

Application interactive permettant de :
- Diagnostiquer automatiquement les données sensibles
- Analyser les risques de ré-identification (k-anonymat)
- Appliquer des règles d'anonymisation
- **Exécuter des scripts SQL en temps réel** sur PostgreSQL cloud (Render)

**🔗 Démo en ligne :** [retrai-shield.streamlit.app](https://retrai-shield.streamlit.app/)

---

## Installation

### Prérequis
- Python 3.10+
- PostgreSQL (cloud recommandé : Render, Supabase, Neon)

### Installation rapide

```bash
pip install -r requirements.txt
```

### Configuration PostgreSQL

**Option 1 : Base cloud (Recommandé)**

1. Créez un compte gratuit sur [Render.com](https://render.com)
2. Créez une base PostgreSQL
3. Récupérez l'URL de connexion

**Option 2 : Docker local**

```bash
docker run -d \
  -e POSTGRES_USER=retraishield_user \
  -e POSTGRES_PASSWORD=localpassword \
  -e POSTGRES_DB=retraishield \
  -p 5432:5432 \
  postgres:15-alpine
```

### Configuration de l'application

Créez un fichier `.streamlit/secrets.toml` avec vos identifiants :

```toml
[postgres]
url = "postgresql://USER:PASSWORD@HOST:PORT/DATABASE"
```

### Lancement

```bash
python -m streamlit run app.py
```

L'application s'ouvre automatiquement sur `http://localhost:8501`

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
- Score de risque global (sur 100) avec recommandations automatiques
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

**Double Export :**
1. **🧪 Pour la Recette (CSV)** : Fichier anonymisé avec métadonnées
2. **⚙️ Pour la Production (SQL)** : 
   - **Exécution en temps réel** sur PostgreSQL cloud (Render)
   - Logs d'exécution détaillés (requête par requête, durée, lignes affectées)
   - Script téléchargeable (DDL/DML production-ready)
   - Démonstration de compétences SQL avancées (MD5, AGE, CASE WHEN, transactions)

---

## Technologies

| Composant | Technologie |
|-----------|-------------|
| **Frontend** | Streamlit |
| **Données** | Pandas, Faker |
| **Visualisation** | Plotly |
| **Base de données** | PostgreSQL (Render) |
| **Déploiement** | Docker, Streamlit Cloud |

---

## Structure du Projet

```
RetraiShield/
├── app.py                  # Application Streamlit (3 onglets)
├── data_generator.py       # Génération données démo (Faker)
├── rgpd_analyzer.py        # Classification colonnes + k-anonymat
├── anonymizer.py           # Règles d'anonymisation
├── sql_generator.py        # Génération scripts PostgreSQL
├── requirements.txt        # Dépendances Python
├── Dockerfile              # Image Docker
├── docker-compose.yml      # Orchestration (optionnel)
└── README.md
```

---

## Workflow Utilisateur

1. **Charger les données** : Upload CSV ou génération de données de démo (10k lignes)
2. **Diagnostic RGPD** : Identifier les colonnes sensibles et leur classification
3. **Analyser le risque** : Calculer le k-anonymat sur les quasi-identifiants
4. **Anonymiser** : Appliquer les règles et comparer avant/après
5. **Vérifier** : Retourner à l'analyse pour valider la réduction du risque
6. **Exporter** : Télécharger le CSV anonymisé ou exécuter le SQL sur PostgreSQL

---

## Déploiement

### Streamlit Cloud (Production)

L'application est déployée sur : **https://retrai-shield.streamlit.app/**

### Docker Local

```bash
# Construction de l'image
docker build -t retraishield .

# Lancement du conteneur
docker run -p 8501:8501 retraishield
```

---

## Compétences Démontrées

Ce projet illustre concrètement :
- 🗄️ **SQL/PostgreSQL** : Génération et exécution de scripts DDL/DML en temps réel
- 🐧 **Linux** : Containerisation Docker, déploiement cloud
- 🔒 **RGPD** : Détection automatique, k-anonymat, règles d'anonymisation conformes
- 📊 **Gestion de JDD** : Extraction, optimisation, sauvegarde, anonymisation de volumétries importantes
- 🚀 **Autonomie** : Projet conçu et déployé en production en moins de 24h
