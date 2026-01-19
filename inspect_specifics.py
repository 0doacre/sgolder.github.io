
import pandas as pd

file_path = "Affectation ULIS-ETABLISSEMENTS.xlsx"

try:
    df = pd.read_excel(file_path)
    print(f"--- Inspecting {file_path} ---")
    
    print("\nUnique values in 'Dispositif spécifique':")
    if 'Dispositif spécifique' in df.columns:
        print(df['Dispositif spécifique'].unique())
        print(df['Dispositif spécifique'].value_counts(dropna=False))
    else:
        print("'Dispositif spécifique' column not found.")

    print("\nInspecting 'ULIS' column (Sample):")
    if 'ULIS' in df.columns:
        print(df['ULIS'].head(10))
        # Check if it looks like a count or a name
    else:
        print("'ULIS' column not found.")

    print("\nInspecting 'Capacité d\'accueil' (Distribution of 0):")
    if "Capacité d'accueil" in df.columns:
        print(df["Capacité d'accueil"].value_counts().sort_index().head())
    
except Exception as e:
    print(f"Error: {e}")
