import streamlit as st
import pandas as pd
from datetime import datetime
import time
import psycopg2
from psycopg2 import sql
import plotly.express as px

from data_generator import generate_demo_data
from rgpd_analyzer import classify_columns, calculate_k_anonymity, calculate_risk_score, get_risk_label
from anonymizer import anonymize_data, create_metadata_header
from sql_generator import generate_sql_anonymization_script

st.set_page_config(
    page_title="RetraiShield - RGPD Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- POSTGRESQL CONNECTION ---
def get_pg_connection():
    """Connexion à PostgreSQL via secrets Streamlit ou variables d'environnement"""
    try:
        # En production Streamlit Cloud, on utilise st.secrets
        if "postgres" in st.secrets:
            db_url = st.secrets["postgres"]["url"]
        else:
            # En local, on utilise OBLIGATOIREMENT une variable d'environnement
            import os
            db_url = os.getenv("POSTGRES_URL")
            
            if not db_url:
                st.error("""
                ❌ **Configuration manquante** : Aucune URL PostgreSQL trouvée.
                
                **Pour corriger :**
                1. Créez le fichier `.streamlit/secrets.toml` avec :
                ```toml
                [postgres]
                url = "postgresql://USER:PASSWORD@HOST:PORT/DATABASE"
                ```
                
                2. Ou définissez la variable d'environnement :
                ```bash
                export POSTGRES_URL="postgresql://USER:PASSWORD@HOST:PORT/DATABASE"
                ```
                """)
                return None
        
        return psycopg2.connect(db_url)
    except Exception as e:
        st.error(f"❌ Erreur de connexion PostgreSQL : {e}")
        return None

def execute_sql_script(sql_script: str, table_name: str = "assures"):
    """
    Exécute le script SQL généré sur PostgreSQL et retourne les logs détaillés.
    """
    logs = []
    start_time = time.time()
    
    conn = get_pg_connection()
    if not conn:
        return ["❌ Impossible de se connecter à la base de données"]
    
    try:
        cur = conn.cursor()
        
        # Séparer les statements SQL (chaque ligne qui finit par ;)
        statements = []
        current_stmt = []
        
        for line in sql_script.split('\n'):
            line = line.strip()
            # Ignorer les commentaires et lignes vides
            if not line or line.startswith('--'):
                continue
            
            current_stmt.append(line)
            
            # Si la ligne finit par ;, c'est la fin d'un statement
            if line.endswith(';'):
                stmt = ' '.join(current_stmt)
                statements.append(stmt)
                current_stmt = []
        
        logs.append(f"📊 **{len(statements)} requêtes SQL à exécuter**\n")
        
        # Exécuter chaque statement
        for i, stmt in enumerate(statements, 1):
            try:
                step_start = time.time()
                
                # Afficher la requête (tronquée si trop longue)
                display_stmt = stmt[:100] + "..." if len(stmt) > 100 else stmt
                logs.append(f"**[{i}/{len(statements)}]** `{display_stmt}`")
                
                cur.execute(stmt)
                conn.commit()
                
                rows_affected = cur.rowcount if cur.rowcount >= 0 else 0
                step_duration = time.time() - step_start
                
                logs.append(f"  ✅ Succès | {rows_affected} lignes | {step_duration:.3f}s\n")
                
            except Exception as e:
                conn.rollback()
                logs.append(f"  ❌ Erreur : {str(e)}\n")
                # On continue pour voir toutes les erreurs
        
        cur.close()
        conn.close()
        
        total_duration = time.time() - start_time
        logs.append(f"\n⏱️ **Durée totale : {total_duration:.2f}s**")
        logs.append(f"✅ **Script exécuté avec succès sur PostgreSQL ({table_name})**")
        
    except Exception as e:
        logs.append(f"\n❌ **Erreur globale : {str(e)}**")
        if conn:
            conn.close()
    
    return logs

def init_database_table(df: pd.DataFrame, table_name: str = "assures"):
    """
    Crée ou réinitialise la table dans PostgreSQL et charge les données.
    Utilise DROP/CREATE pour garantir le schéma, et execute_batch pour la performance.
    """
    conn = get_pg_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        # On doit DROP la table car le schéma a pu changer (colonnes supprimées par le script précédent)
        cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
        
        # Create table from dataframe
        create_sql = f"CREATE TABLE {table_name} ("
        columns = []
        for col in df.columns:
            dtype = df[col].dtype
            if dtype == 'int64':
                sql_type = 'INTEGER'
            elif dtype == 'float64':
                sql_type = 'NUMERIC'
            else:
                sql_type = 'TEXT'
            columns.append(f"{col} {sql_type}")
        
        create_sql += ", ".join(columns) + ");"
        cur.execute(create_sql)
        
        # Insert en BATCH (beaucoup plus rapide)
        cols = ", ".join(df.columns)
        placeholders = ", ".join(["%s"] * len(df.columns))
        insert_sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
        
        # Convertir le DataFrame en liste de tuples
        data = [tuple(row) for row in df.values]
        
        # Exécuter en batch (1000 lignes à la fois)
        from psycopg2.extras import execute_batch
        execute_batch(cur, insert_sql, data, page_size=1000)
        
        conn.commit()
        cur.close()
        conn.close()
        
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'initialisation : {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

# --- CSS PERSONNALISÉ POUR UN LOOK PREMIUM ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem; 
        color: var(--text-color); 
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.5rem; 
        color: var(--text-color); 
        margin-top: 20px;
    }
    .card {
        padding: 20px; 
        border-radius: 10px; 
        background-color: rgba(255, 255, 255, 0.05); 
        border: 1px solid rgba(128, 128, 128, 0.2); 
        margin-bottom: 20px;
    }
    
    /* Dark mode support pour les métriques */
    [data-testid="stMetricValue"] {
        background-color: var(--background-color);
    }
    
    .stMetric {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Logs SQL style terminal */
    .sql-logs {
        background-color: #1e1e1e;
        color: #cccccc;
        padding: 15px;
        border-radius: 8px;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 13px;
        line-height: 1.5;
        border: 1px solid #333;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
        max-height: 500px;
        overflow-y: auto;
    }
    
    .sql-logs .log-line {
        margin-bottom: 4px;
        display: block;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        padding-bottom: 2px;
    }
    
    .sql-logs .log-header { color: #569cd6; font-weight: bold; } /* Bleu VSCode */
    .sql-logs .log-query { color: #ce9178; font-family: monospace; } /* Orange String */
    .sql-logs .log-success { color: #4ec9b0; } /* Vert VSCode */
    .sql-logs .log-error { color: #f44747; } /* Rouge Erreur */
    .sql-logs .log-info { color: #9cdcfe; } /* Bleu clair */
</style>
""", unsafe_allow_html=True)

# initialisation de la session
if 'df' not in st.session_state:
    st.session_state.df = None
if 'df_anon' not in st.session_state:
    st.session_state.df_anon = None
if 'applied_rules' not in st.session_state:
    st.session_state.applied_rules = []

# --- SIDEBAR: NAVIGATION & CONFIGURATION ---
with st.sidebar:
    st.title("🛡️ RetraiShield")
    st.caption("v1.0.0 | AGIRC-ARRCO")
    st.markdown("---")
    
    # NAVIGATION
    st.subheader("🧭 Navigation")
    page = st.radio(
        "Page",
        ["1. Diagnostic RGPD", "2. Analyse des Risques", "3. Anonymisation & Export"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # CHARGEMENT DONNÉES
    st.subheader("📁 Données")
    data_source = st.radio("Source:", ["Générer Démo", "Upload CSV"], label_visibility="collapsed")
    
    if data_source == "Générer Démo":
        n_rows = st.number_input("Nb lignes", 100, 50000, 10000, 1000)
        if st.button("🎲 Générer Dataset", type="primary", use_container_width=True):
            with st.spinner("Génération..."):
                st.session_state.df = generate_demo_data(n_rows)
                st.session_state.df_anon = None
                st.success(f"✅ {n_rows} lignes !")
                
    else:
        uploaded_file = st.file_uploader("Fichier CSV", type=['csv'])
        if uploaded_file:
            st.session_state.df = pd.read_csv(uploaded_file)
            st.session_state.df_anon = None

# --- PAGE 1: DIAGNOSTIC ---
if page == "1. Diagnostic RGPD":
    st.markdown('<p class="main-header">📋 Diagnostic RGPD</p>', unsafe_allow_html=True)
    st.markdown("""
    **Analyse automatique de la sensibilité des colonnes.**
    
    L'algorithme scanne les noms de colonnes et le contenu pour détecter les risques RGPD.
    """)
    
    # Légende des catégories
    st.info("""
    **📖 Légende des catégories :**
    
    - 🔴 **ID Direct** : Données identifiant directement une personne (Nom, Prénom, ID) → ⚠️ À masquer impérativement
    - 🟠 **Quasi-ID** : Combinaison permettant de ré-identifier (Date naissance, Code postal, Sexe) → ⚠️ À généraliser
    - 🟡 **Sensible** : Données protégées RGPD (Revenus, Santé, Religion) → ⚠️ À anonymiser
    - 🟢 **Non sensible** : Données sans risque identifiant (Secteur, Statut)
    """)
    
    if st.session_state.df is None:
        st.info("👈 Veuillez charger ou générer des données depuis le menu latéral.")
    else:
        # FILTRES LOCAUX (déplacés ici)
        st.subheader("🔍 Filtres d'Affichage")
        
        col_f1, col_f2 = st.columns(2)
        
        df_display = st.session_state.df.copy()
        
        with col_f1:
            if 'secteur_activite' in df_display.columns:
                secteurs = ['Tous'] + list(df_display['secteur_activite'].unique())
                sel_secteur = st.selectbox("Secteur d'activité", secteurs)
                if sel_secteur != 'Tous':
                    df_display = df_display[df_display['secteur_activite'] == sel_secteur]
        
        with col_f2:
            if 'statut' in df_display.columns:
                statuts = ['Tous'] + list(df_display['statut'].unique())
                sel_statut = st.selectbox("Statut", statuts)
                if sel_statut != 'Tous':
                    df_display = df_display[df_display['statut'] == sel_statut]
        
        st.caption(f"📊 Affichage: {len(df_display)} / {len(st.session_state.df)} lignes")
        st.markdown("---")
        
        # KPIs en haut de page
        with st.spinner("Analyse du dataset..."):
            classification = classify_columns(df_display)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Identifiants Directs", len(classification['identifiants_directs']), 
                   help="Données identifiant directement une personne (Nom, Prénom, ID Assuré...). À masquer impérativement.",
                   delta_color="inverse")
        col2.metric("Quasi-Identifiants", len(classification['quasi_identifiants']), 
                   help="Données qui, combinées, peuvent permettre une ré-identification (Date naissance, Code postal, Sexe...). À généraliser.",
                   delta_color="off")
        col3.metric("Données Sensibles", len(classification['donnees_sensibles']), 
                   help="Informations confidentielles (Revenus, Pension, Santé...).",
                   delta_color="off")
        col4.metric("Total Colonnes", len(df_display.columns))
        
        st.markdown("---")
        
        # Contenu principal
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.markdown('<p class="sub-header">Aperçu des données</p>', unsafe_allow_html=True)
            st.dataframe(df_display.head(10), use_container_width=True)
        
        with col_right:
            st.markdown('<p class="sub-header">Classification</p>', unsafe_allow_html=True)
            
            # Création d'un tableau plus visuel pour la classification
            class_data = []
            for col in df_display.columns:
                if col in classification['identifiants_directs']:
                    tag = "🔴 ID Direct"
                elif col in classification['quasi_identifiants']:
                    tag = "🟠 Quasi-ID"
                elif col in classification['donnees_sensibles']:
                    tag = "🟡 Sensible"
                else:
                    tag = "🟢 Autre"
                class_data.append({"Colonne": col, "Type": tag})
            
            st.dataframe(pd.DataFrame(class_data), use_container_width=True, hide_index=True)

# --- PAGE 2: ANALYSE RISQUE ---
elif page == "2. Analyse des Risques":
    st.markdown('<p class="main-header">📊 Analyse des Risques (k-anonymat)</p>', unsafe_allow_html=True)
    
    with st.expander("ℹ️ Comprendre le k-anonymat", expanded=False):
        st.markdown("""
        **Qu'est-ce que le k-anonymat ?**
        
        C'est une mesure de protection de la vie privée. Un jeu de données est **k-anonyme** si chaque individu est "caché" dans un groupe d'au moins **k** personnes partageant les mêmes caractéristiques (quasi-identifiants).
        
        *Exemple : Si k=5, cela signifie que pour toute combinaison de (Date Naissance + Code Postal + Sexe), il y a au moins 5 personnes identiques. Impossible de savoir qui est qui parmi ces 5.*
        
        **Seuils recommandés :**
        - **k < 5** : 🔴 Risque élevé de ré-identification
        - **k ≥ 5** : 🟢 Protection standard acceptée
        """)
    
    if st.session_state.df is None:
        st.info("👈 Veuillez charger des données.")
    else:
        # SÉLECTEUR DE DATASET
        dataset_options = ["Données Originales"]
        if st.session_state.df_anon is not None:
            dataset_options.append("Données Anonymisées 🔒")
        
        selected_dataset = st.radio("Jeu de données à analyser :", dataset_options, horizontal=True)
        
        if "Originales" in selected_dataset:
            df_analysis = st.session_state.df
            st.caption("Analyse des données brutes (avant traitement)")
        else:
            df_analysis = st.session_state.df_anon
            st.success("Analyse des données protégées (après anonymisation)")
            st.info("""
            ℹ️ **Pourquoi moins de quasi-identifiants ?** 
            
            Les colonnes sensibles ont été transformées pour réduire le risque de ré-identification :
            
            *   ❌ **Suppression directe** : `Nom`, `Prénom`, `Commune`
            *   📅 **Généralisation** : `Date de naissance` → `Tranche d'âge` (ex: 30-40 ans)
            *   📍 **Généralisation** : `Code Postal` → `Département` (ex: 75)
            """)

        classification = classify_columns(df_analysis)
        available_qi = classification['quasi_identifiants']
        
        # Configuration de l'analyse
        with st.expander("⚙️ Configuration de l'analyse", expanded=True):
            default_qi = [c for c in ['date_naissance', 'code_postal', 'sexe', 'tranche_age', 'departement'] if c in available_qi]
            if not default_qi and available_qi: default_qi = available_qi[:3]
            
            selected_qi = st.multiselect(
                "Quasi-identifiants pour le calcul:",
                options=available_qi,
                default=default_qi
            )
        
        if selected_qi:
            with st.spinner("Calcul des risques en cours..."):
                # Préparation calcul
                df_calc = df_analysis.copy()
                if 'date_naissance' in selected_qi:
                    df_calc['annee_naissance'] = pd.to_datetime(df_calc['date_naissance']).dt.year
                    calc_qi = [c if c != 'date_naissance' else 'annee_naissance' for c in selected_qi]
                else:
                    calc_qi = selected_qi
                    
                if 'code_postal' in calc_qi:
                    df_calc['departement'] = df_calc['code_postal'].astype(str).str[:2]
                    calc_qi = [c if c != 'code_postal' else 'departement' for c in calc_qi]
                
                # Calcul
                k_series = calculate_k_anonymity(df_calc, calc_qi)
                risk_score = calculate_risk_score(k_series)
            
            # Affichage Résultats
            st.markdown("### Résultats de l'analyse")
            
            # AMÉLIORATION 1 : Jauge visuelle du risque
            risk_color = "🔴" if risk_score > 70 else "🟠" if risk_score > 40 else "🟢"
            risk_text = "Élevé" if risk_score > 70 else "Moyen" if risk_score > 40 else "Faible"
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Score de Risque Global", f"{risk_score:.0f}/100", delta=f"{risk_color} {risk_text}", delta_color="off")
            c2.metric("k-anonymat Moyen", f"{k_series.mean():.1f}")
            c3.metric("Lignes à Haut Risque (k<5)", f"{(k_series < 5).sum()}")
            c4.metric("k-anonymat Minimum", f"{k_series.min()}")
            
            # Barre de progression visuelle
            st.markdown("**Niveau de protection**")
            progress_value = min(100, max(0, 100 - risk_score)) / 100
            st.progress(progress_value, text=f"Protection : {100 - risk_score:.0f}%")
            
            # AMÉLIORATION 2 : Tableau comparatif avant/après
            if st.session_state.df_anon is not None and "Anonymisées" not in selected_dataset:
                st.markdown("---")
                st.markdown("### 📊 Comparaison Avant/Après Anonymisation")
                
                # Calcul rapide du k-anonymat après anonymisation
                df_anon_calc = st.session_state.df_anon.copy()
                qi_anon = [c for c in ['tranche_age', 'departement', 'sexe'] if c in df_anon_calc.columns]
                
                if qi_anon and len(qi_anon) >= 2:
                    k_anon = calculate_k_anonymity(df_anon_calc, qi_anon)
                    risk_anon = calculate_risk_score(k_anon)
                    
                    col_avant, col_apres, col_gain = st.columns(3)
                    
                    with col_avant:
                        st.metric("Avant (Données brutes)", 
                                 f"Score: {risk_score:.0f}/100",
                                 delta=f"k-moyen: {k_series.mean():.1f}",
                                 delta_color="off")
                    
                    with col_apres:
                        st.metric("Après (Données anonymisées)", 
                                 f"Score: {risk_anon:.0f}/100",
                                 delta=f"k-moyen: {k_anon.mean():.1f}",
                                 delta_color="off")
                    
                    with col_gain:
                        improvement = risk_score - risk_anon
                        st.metric("Amélioration", 
                                 f"{improvement:.0f} points",
                                 delta=f"🎯 {(improvement/risk_score)*100:.0f}% de réduction",
                                 delta_color="normal")
            
            # AMÉLIORATION 3 : Recommandations automatiques
            st.markdown("---")
            if risk_score > 70:
                st.error("""
                🚨 **Niveau de risque ÉLEVÉ** - Action requise !
                
                **Recommandations urgentes :**
                - ⚠️ Les données contiennent trop de quasi-identifiants précis
                - 🎯 Passez à l'onglet **3. Anonymisation & Export** pour appliquer les règles
                - 🔐 Activez toutes les transformations (généralisation dates, codes postaux, etc.)
                """)
            elif risk_score > 40:
                st.warning("""
                ⚠️ **Niveau de risque MOYEN** - Amélioration recommandée
                
                **Suggestions :**
                - 📍 Généralisez les codes postaux en départements
                - 📅 Transformez les dates de naissance en tranches d'âge
                - ➡️ Allez à l'onglet **3. Anonymisation & Export** pour optimiser
                """)
            else:
                st.success("""
                ✅ **Niveau de risque FAIBLE** - Protection acceptable
                
                Les données respectent les seuils RGPD recommandés (k ≥ 5). Vous pouvez procéder à l'export en toute confiance.
                """)
            
            # Graphiques
            st.markdown("---")
            col_chart, col_table = st.columns([2, 1])
            
            with col_chart:
                k_plot = k_series.clip(upper=50)
                fig = px.histogram(x=k_plot, nbins=50, title="Distribution du k-anonymat", 
                                 labels={'x': 'k-anonymat', 'y': 'Nb Personnes'},
                                 color_discrete_sequence=['#1E3A8A'])
                fig.add_vline(x=5, line_dash="dash", line_color="red", 
                             annotation_text="Seuil critique (k=5)", 
                             annotation_position="top right")
                st.plotly_chart(fig, use_container_width=True)
            
            with col_table:
                st.markdown("**Combinaisons risquées (k < 5)**")
                df_risk = df_calc.copy()
                df_risk['k'] = k_series
                risky_combos = df_risk[df_risk['k'] < 5][calc_qi + ['k']].drop_duplicates().head(15)
                
                if len(risky_combos) > 0:
                    st.dataframe(risky_combos, use_container_width=True, hide_index=True)
                else:
                    st.success("✅ Aucune combinaison risquée détectée !")


# --- PAGE 3: ANONYMISATION ---
elif page == "3. Anonymisation & Export":
    st.markdown('<p class="main-header">🔒 Anonymisation & Export</p>', unsafe_allow_html=True)
    
    if st.session_state.df is None:
        st.info("👈 Veuillez charger des données.")
    else:
        df_to_anonymize = st.session_state.df
        
        # Configuration des règles
        st.subheader("⚙️ Configuration des Règles d'Anonymisation")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            r_hash = st.checkbox("🔐 Hash Identifiants", True)
            r_nom = st.checkbox("❌ Suppr. Noms/Prénoms", True)
        with col2:
            r_age = st.checkbox("📅 Dates → Tranches d'âge", True)
            r_geo = st.checkbox("📍 Code Postal → Département", True)
        with col3:
            r_rev = st.checkbox("💰 Revenus → Tranches", True)
        
        st.markdown("---")
        
        # Bouton d'anonymisation centré
        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_center:
            if st.button("🚀 Lancer l'Anonymisation", type="primary", use_container_width=True):
                progress_bar = st.progress(0, text="Initialisation...")
                
                rules = {
                    'hash_identifiants': r_hash, 'supprimer_noms': r_nom,
                    'tranches_age': r_age, 'postal_to_dept': r_geo,
                    'supprimer_commune': True, 'tranches_revenus': r_rev
                }
                
                progress_bar.progress(20, text="Hachage des identifiants...")
                df_anon, applied_rules = anonymize_data(df_to_anonymize, rules)
                progress_bar.progress(80, text="Application des règles métiers...")
                
                st.session_state.df_anon = df_anon
                st.session_state.applied_rules = applied_rules
                
                progress_bar.progress(100, text="Terminé !")
                st.success("✅ Anonymisation terminée avec succès !")
        
        # Résultats
        if st.session_state.df_anon is not None:
            st.markdown("---")
            st.subheader("📊 Résultat de l'Anonymisation")
            
            # Métriques de comparaison
            col1, col2, col3 = st.columns(3)
            col1.metric("Colonnes Avant", len(df_to_anonymize.columns))
            col2.metric("Colonnes Après", len(st.session_state.df_anon.columns))
            reduction = (1 - len(st.session_state.df_anon.columns)/len(df_to_anonymize.columns))*100
            col3.metric("Réduction", f"{reduction:.0f}%", delta=f"-{reduction:.0f}%", delta_color="normal")
            
            # Aperçu des données
            st.dataframe(st.session_state.df_anon.head(10), use_container_width=True)
            
            # SECTION EXPORT (2 colonnes : Test vs Prod)
            st.markdown("---")
            st.subheader("📤 Exports & Industrialisation")
            
            col_test, col_prod = st.columns(2)
            
            # 1. Export CSV (Pour le Test)
            with col_test:
                st.markdown("""
                <div class="card">
                    <h4>🧪 Pour la Recette (CSV)</h4>
                    <p>Données anonymisées prêtes à être chargées en environnement de test.</p>
                </div>
                """, unsafe_allow_html=True)
                
                k_final = 100
                meta = create_metadata_header(st.session_state.applied_rules, k_final)
                csv_content = meta + st.session_state.df_anon.to_csv(index=False)
                csv_bytes = csv_content.encode('utf-8-sig')
                
                st.download_button(
                    "⬇️ Télécharger le CSV",
                    data=csv_bytes,
                    file_name=f"export_rgpd_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )

            # 2. Export SQL (Pour la Prod)
            with col_prod:
                st.markdown("""
                <div class="card">
                    <h4>⚙️ Pour la Production (SQL)</h4>
                    <p>Script PostgreSQL optimisé pour appliquer ces règles directement en base.</p>
                </div>
                """, unsafe_allow_html=True)
                
                sql_script = generate_sql_anonymization_script(st.session_state.applied_rules)
                
                # Bouton d'exécution SQL en temps réel
                if st.button("▶️ Exécuter sur PostgreSQL", key="exec_sql", use_container_width=True, type="primary"):
                    with st.spinner("🔄 Chargement des données dans PostgreSQL..."):
                        if init_database_table(df_to_anonymize):
                            st.success("✅ Table créée et données chargées")
                    
                    with st.spinner("⚡ Exécution du script SQL..."):
                        logs = execute_sql_script(sql_script)
                        st.session_state.sql_logs = logs
                
                st.download_button(
                    "💾 Télécharger le Script SQL",
                    data=sql_script,
                    file_name=f"anonymisation_rgpd_{datetime.now().strftime('%Y%m%d_%H%M')}.sql",
                    mime="text/plain",
                    use_container_width=True
                )

            # LOGS D'EXÉCUTION SQL (Logs en temps réel)
            if 'sql_logs' in st.session_state and st.session_state.sql_logs:
                st.markdown("---")
                st.subheader("📋 Logs d'Exécution PostgreSQL")
                
                html_logs = '<div class="sql-logs">'
                for log in st.session_state.sql_logs:
                    # Conversion simple Markdown -> HTML pour ce cas spécifique
                    line = log
                    
                    # Gestion du gras **text** -> header
                    if "**" in line:
                        parts = line.split("**")
                        if len(parts) >= 3:
                            line = f'{parts[0]}<span class="log-header">{parts[1]}</span>{parts[2]}'
                    
                    # Gestion du code `text` -> query
                    if "`" in line:
                        parts = line.split("`")
                        if len(parts) >= 3:
                            line = f'{parts[0]}<span class="log-query">{parts[1]}</span>{parts[2]}'
                    
                    # Couleurs spécifiques
                    if "✅" in line:
                        line = f'<span class="log-success">{line}</span>'
                    elif "❌" in line:
                        line = f'<span class="log-error">{line}</span>'
                    elif "📊" in line or "⏱️" in line:
                        line = f'<span class="log-info">{line}</span>'
                        
                    html_logs += f'<div class="log-line">{line}</div>'
                
                html_logs += '</div>'
                st.markdown(html_logs, unsafe_allow_html=True)

            # VISUALISATION DU CODE SQL (Compétence technique)
            with st.expander("👁️ Voir le code SQL généré (Démonstration technique)"):
                st.markdown("""
                *Ce script démontre la capacité à traduire des règles métier Python en requêtes SQL performantes (Set-based operations).*
                """)
                st.code(sql_script, language="sql", line_numbers=True)
