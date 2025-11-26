import pandas as pd
import re

def classify_columns(df):
    """Classe les colonnes en 4 catégories RGPD"""
    
    classification = {
        'identifiants_directs': [],
        'quasi_identifiants': [],
        'donnees_sensibles': [],
        'donnees_non_sensibles': []
    }
    
    for col in df.columns:
        col_lower = col.lower()
        
        # identifiants directs
        if any(keyword in col_lower for keyword in ['id', 'nom', 'prenom', 'email', 'telephone']):
            classification['identifiants_directs'].append(col)
        
        # quasi-identifiants (permettent de réidentifier par combinaison)
        elif any(keyword in col_lower for keyword in ['date_naissance', 'naissance', 'code_postal', 'postal', 'sexe', 'commune', 'ville']):
            classification['quasi_identifiants'].append(col)
        
        # données sensibles (financières, santé, etc.)
        elif any(keyword in col_lower for keyword in ['revenu', 'pension', 'montant', 'salaire', 'trimestre']):
            classification['donnees_sensibles'].append(col)
        
        # le reste = non sensible
        else:
            classification['donnees_non_sensibles'].append(col)
    
    return classification

def calculate_k_anonymity(df, quasi_identifiers):
    """Calcule le k-anonymat pour chaque ligne"""
    
    if not quasi_identifiers or len(quasi_identifiers) == 0:
        return pd.Series([len(df)] * len(df), index=df.index)
    
    # on regroupe par les quasi-identifiants et on compte
    k_values = df.groupby(quasi_identifiers).size()
    
    # on mappe le k pour chaque ligne
    df_k = df.merge(
        k_values.reset_index(name='k'),
        on=quasi_identifiers,
        how='left'
    )
    
    return df_k['k']

def calculate_risk_score(k_series):
    """Calcule un score de risque global basé sur la distribution de k"""
    
    if len(k_series) == 0:
        return 0
    
    # pourcentage de personnes avec k < 5 (haut risque)
    high_risk_pct = (k_series < 5).sum() / len(k_series) * 100
    
    # k moyen
    k_mean = k_series.mean()
    
    # score de risque sur 100 (plus c'est élevé, plus c'est risqué)
    if k_mean < 5:
        risk_score = 90 + high_risk_pct / 10
    elif k_mean < 10:
        risk_score = 70 + high_risk_pct / 5
    elif k_mean < 20:
        risk_score = 50 + high_risk_pct / 3
    else:
        risk_score = 30 + high_risk_pct / 2
    
    return min(100, risk_score)

def get_risk_label(score):
    """Retourne un label de risque en fonction du score"""
    if score >= 80:
        return "🔴 Risque élevé"
    elif score >= 60:
        return "🟠 Risque moyen"
    elif score >= 40:
        return "🟡 Risque faible"
    else:
        return "🟢 Risque très faible"
