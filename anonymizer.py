import pandas as pd
import hashlib
from datetime import datetime

def anonymize_data(df, rules):
    """Applique les règles d'anonymisation sur le dataframe"""
    
    df_anon = df.copy()
    applied_rules = []
    
    # règle 1: hash SHA256 pour les identifiants directs
    if rules.get('hash_identifiants', True):
        if 'id_assure' in df_anon.columns:
            df_anon['id_assure'] = df_anon['id_assure'].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16])
            applied_rules.append("Identifiants → Hash SHA256")
    
    # règle 2: suppression nom/prénom
    if rules.get('supprimer_noms', True):
        for col in ['nom', 'prenom']:
            if col in df_anon.columns:
                df_anon = df_anon.drop(columns=[col])
        applied_rules.append("Nom/Prénom → Supprimés")
    
    # règle 3: date de naissance → tranche d'âge
    if rules.get('tranches_age', True) and 'date_naissance' in df_anon.columns:
        df_anon['tranche_age'] = df_anon['date_naissance'].apply(date_to_age_range)
        df_anon = df_anon.drop(columns=['date_naissance'])
        applied_rules.append("Date naissance → Tranche d'âge")
    
    # règle 4: code postal → département
    if rules.get('postal_to_dept', True) and 'code_postal' in df_anon.columns:
        df_anon['departement'] = df_anon['code_postal'].apply(lambda x: str(x)[:2] if pd.notna(x) else None)
        df_anon = df_anon.drop(columns=['code_postal'])
        applied_rules.append("Code postal → Département")
    
    # règle 5: suppression commune
    if rules.get('supprimer_commune', True) and 'commune' in df_anon.columns:
        df_anon = df_anon.drop(columns=['commune'])
        applied_rules.append("Commune → Supprimée")
    
    # règle 6: revenus → tranches
    if rules.get('tranches_revenus', True):
        if 'revenu_annuel_brut' in df_anon.columns:
            df_anon['tranche_revenu'] = df_anon['revenu_annuel_brut'].apply(revenu_to_range)
            df_anon = df_anon.drop(columns=['revenu_annuel_brut'])
            applied_rules.append("Revenu → Tranches")
        
        if 'montant_pension_mensuelle' in df_anon.columns:
            df_anon['tranche_pension'] = df_anon['montant_pension_mensuelle'].apply(pension_to_range)
            df_anon = df_anon.drop(columns=['montant_pension_mensuelle'])
            applied_rules.append("Pension → Tranches")
    
    return df_anon, applied_rules

def date_to_age_range(date_str):
    """Convertit une date de naissance en tranche d'âge"""
    try:
        birth_date = pd.to_datetime(date_str)
        age = (datetime.now() - birth_date).days // 365
        
        if age < 30:
            return "< 30 ans"
        elif age < 40:
            return "30-40 ans"
        elif age < 50:
            return "40-50 ans"
        elif age < 60:
            return "50-60 ans"
        elif age < 70:
            return "60-70 ans"
        elif age < 80:
            return "70-80 ans"
        else:
            return "80+ ans"
    except:
        return "Inconnu"

def revenu_to_range(revenu):
    """Convertit un revenu en tranche"""
    if pd.isna(revenu):
        return "Inconnu"
    
    if revenu < 20000:
        return "< 20k"
    elif revenu < 30000:
        return "20k-30k"
    elif revenu < 40000:
        return "30k-40k"
    elif revenu < 50000:
        return "40k-50k"
    elif revenu < 60000:
        return "50k-60k"
    elif revenu < 80000:
        return "60k-80k"
    elif revenu < 100000:
        return "80k-100k"
    else:
        return "100k+"

def pension_to_range(pension):
    """Convertit une pension en tranche"""
    if pd.isna(pension):
        return "Inconnu"
    
    if pension < 1000:
        return "< 1000€"
    elif pension < 1500:
        return "1000-1500€"
    elif pension < 2000:
        return "1500-2000€"
    elif pension < 2500:
        return "2000-2500€"
    elif pension < 3000:
        return "2500-3000€"
    else:
        return "3000€+"

def create_metadata_header(applied_rules, k_anonymity_final):
    """Crée un header de métadonnées pour le CSV exporté"""
    
    metadata = f"""# RGPD Data Qualification Platform - Export
# Date d'export: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Règles appliquées: {', '.join(applied_rules)}
# k-anonymat final moyen: {k_anonymity_final:.1f}
#
"""
    return metadata
