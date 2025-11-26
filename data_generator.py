import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker('fr_FR')

def generate_demo_data(n_rows=10000):
    """Génère un dataset de démo pour AGIRC-ARRCO"""
    
    data = []
    
    for i in range(n_rows):
        # dates de naissance réalistes pour des retraités (60-90 ans)
        age = random.randint(60, 90)
        date_naissance = datetime.now() - timedelta(days=age*365 + random.randint(0, 365))
        
        # on calcule la date de liquidation (entre 60 et 67 ans généralement)
        age_liquidation = random.randint(60, 67)
        date_liquidation = date_naissance + timedelta(days=age_liquidation*365)
        
        sexe = random.choice(['M', 'F'])
        secteur = random.choice(['Public', 'Privé', 'Indépendant', 'Agricole'])
        
        # revenus cohérents avec le secteur
        if secteur == 'Public':
            revenu = random.randint(25000, 80000)
        elif secteur == 'Privé':
            revenu = random.randint(20000, 150000)
        elif secteur == 'Indépendant':
            revenu = random.randint(15000, 120000)
        else:  # Agricole
            revenu = random.randint(15000, 60000)
        
        # pension proportionnelle au revenu
        montant_pension = int(revenu * random.uniform(0.4, 0.7) / 12)
        
        row = {
            'id_assure': f"ASS{i+1:06d}",
            'nom': fake.last_name(),
            'prenom': fake.first_name(),
            'date_naissance': date_naissance.strftime('%Y-%m-%d'),
            'sexe': sexe,
            'code_postal': fake.postcode(),
            'commune': fake.city(),
            'revenu_annuel_brut': revenu,
            'montant_pension_mensuelle': montant_pension,
            'nb_trimestres_valides': random.randint(100, 180),
            'statut': random.choice(['Retraité', 'En liquidation', 'Actif cotisant']),
            'secteur_activite': secteur,
            'date_liquidation': date_liquidation.strftime('%Y-%m-%d'),
            'type_regime': random.choice(['AGIRC', 'ARRCO', 'AGIRC-ARRCO'])
        }
        data.append(row)
    
    return pd.DataFrame(data)
