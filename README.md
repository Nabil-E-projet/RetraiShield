
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
   - Script téléchargeable (DDL/DML production-ready)
   - Démonstration de compétences SQL avancées (MD5, AGE, CASE WHEN, transactions)

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
├── app.py                  # Application Streamlit (3 onglets)
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


Le projet démontre la capacité à :
- Manipuler des datasets sensibles (retraite, finance)
- Implémenter des algorithmes de protection de la vie privée (k-anonymat)
- Générer du SQL production-ready pour PostgreSQL
- Déployer des applications data sur le cloud et en conteneurs
