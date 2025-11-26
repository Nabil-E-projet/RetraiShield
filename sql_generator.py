from datetime import datetime

def generate_sql_anonymization_script(applied_rules):
    """Génère un script SQL PostgreSQL pour appliquer les règles d'anonymisation"""
    
    script = "-- Script d'anonymisation RGPD pour PostgreSQL\n"
    script += "-- Généré par RetraiShield\n"
    script += f"-- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    script += "-- ATTENTION: Exécuter ce script dans une transaction pour pouvoir rollback si nécessaire\n"
    script += "BEGIN;\n\n"
    
    # Identifiants → Hash
    if any("Hash" in rule for rule in applied_rules):
        script += "-- Anonymisation des identifiants directs par hachage MD5\n"
        script += "UPDATE assures SET\n"
        script += "    id_assure = MD5(id_assure::text);\n\n"
    
    # Suppression nom/prénom
    if any("Nom" in rule or "Prénom" in rule for rule in applied_rules):
        script += "-- Suppression des noms et prénoms\n"
        script += "ALTER TABLE assures \n"
        script += "    DROP COLUMN nom,\n"
        script += "    DROP COLUMN prenom;\n\n"
    
    # Date → Tranche d'âge
    if any("Date" in rule or "âge" in rule for rule in applied_rules):
        script += "-- Transformation date de naissance en tranche d'âge\n"
        script += "ALTER TABLE assures ADD COLUMN tranche_age VARCHAR(20);\n\n"
        script += "UPDATE assures SET tranche_age = \n"
        script += "    CASE \n"
        script += "        WHEN EXTRACT(YEAR FROM AGE(date_naissance)) < 30 THEN '< 30 ans'\n"
        script += "        WHEN EXTRACT(YEAR FROM AGE(date_naissance)) < 40 THEN '30-40 ans'\n"
        script += "        WHEN EXTRACT(YEAR FROM AGE(date_naissance)) < 50 THEN '40-50 ans'\n"
        script += "        WHEN EXTRACT(YEAR FROM AGE(date_naissance)) < 60 THEN '50-60 ans'\n"
        script += "        WHEN EXTRACT(YEAR FROM AGE(date_naissance)) < 70 THEN '60-70 ans'\n"
        script += "        WHEN EXTRACT(YEAR FROM AGE(date_naissance)) < 80 THEN '70-80 ans'\n"
        script += "        ELSE '80+ ans'\n"
        script += "    END;\n\n"
        script += "ALTER TABLE assures DROP COLUMN date_naissance;\n\n"
    
    # Code postal → Département
    if any("postal" in rule or "Département" in rule for rule in applied_rules):
        script += "-- Transformation code postal en département\n"
        script += "ALTER TABLE assures ADD COLUMN departement VARCHAR(2);\n\n"
        script += "UPDATE assures SET departement = SUBSTRING(code_postal FROM 1 FOR 2);\n\n"
        script += "ALTER TABLE assures DROP COLUMN code_postal;\n\n"
    
    # Suppression commune
    if any("Commune" in rule for rule in applied_rules):
        script += "-- Suppression de la commune\n"
        script += "ALTER TABLE assures DROP COLUMN commune;\n\n"
    
    # Revenus → Tranches
    if any("Revenu" in rule or "Pension" in rule for rule in applied_rules):
        script += "-- Transformation revenus en tranches\n"
        script += "ALTER TABLE assures ADD COLUMN tranche_revenu VARCHAR(20);\n\n"
        script += "UPDATE assures SET tranche_revenu = \n"
        script += "    CASE \n"
        script += "        WHEN revenu_annuel_brut < 20000 THEN '< 20k'\n"
        script += "        WHEN revenu_annuel_brut < 30000 THEN '20k-30k'\n"
        script += "        WHEN revenu_annuel_brut < 40000 THEN '30k-40k'\n"
        script += "        WHEN revenu_annuel_brut < 50000 THEN '40k-50k'\n"
        script += "        WHEN revenu_annuel_brut < 60000 THEN '50k-60k'\n"
        script += "        WHEN revenu_annuel_brut < 80000 THEN '60k-80k'\n"
        script += "        WHEN revenu_annuel_brut < 100000 THEN '80k-100k'\n"
        script += "        ELSE '100k+'\n"
        script += "    END;\n\n"
        script += "ALTER TABLE assures DROP COLUMN revenu_annuel_brut;\n\n"
        
        script += "ALTER TABLE assures ADD COLUMN tranche_pension VARCHAR(20);\n\n"
        script += "UPDATE assures SET tranche_pension = \n"
        script += "    CASE \n"
        script += "        WHEN montant_pension_mensuelle < 1000 THEN '< 1000€'\n"
        script += "        WHEN montant_pension_mensuelle < 1500 THEN '1000-1500€'\n"
        script += "        WHEN montant_pension_mensuelle < 2000 THEN '1500-2000€'\n"
        script += "        WHEN montant_pension_mensuelle < 2500 THEN '2000-2500€'\n"
        script += "        WHEN montant_pension_mensuelle < 3000 THEN '2500-3000€'\n"
        script += "        ELSE '3000€+'\n"
        script += "    END;\n\n"
        script += "ALTER TABLE assures DROP COLUMN montant_pension_mensuelle;\n\n"
    
    script += "-- FIN DU SCRIPT\n"
    script += "-- Vérifier les résultats avant de faire:\n"
    script += "COMMIT;\n"
    script += "-- En cas d'erreur: ROLLBACK;\n"
    
    return script
