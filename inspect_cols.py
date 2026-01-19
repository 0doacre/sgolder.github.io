
import pandas as pd

FILE = "Affectation ULIS-ETABLISSEMENTS.xlsx"

try:
    df = pd.read_excel(FILE)
    print("Columns:", df.columns.tolist())
    
    if 'Dispositif spécifique' in df.columns:
        print("\nUnique Specialized Devices:")
        print(df['Dispositif spécifique'].unique())
    
    # Check for Address candidates
    address_candidates = [c for c in df.columns if 'ADRESSE' in c.upper() or 'RUE' in c.upper() or 'CPOSTAL' in c.upper() or 'COMMUNE' in c.upper()]
    print("\nAddress Candidates:", address_candidates)
    
except Exception as e:
    print(e)
