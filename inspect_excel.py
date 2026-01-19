
import pandas as pd
import os

files = ["Affectation ULIS-ETABLISSEMENTS.xlsx", "Temporaire_pour_carte_ULIS.xlsx"]

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

for f in files:
    print(f"--- {f} ---")
    try:
        df = pd.read_excel(f)
        print("Columns List:")
        for c in df.columns:
            print(f"  - {c}")
        print("\nStructure Check:")
        if not df.empty:
            row = df.iloc[0]
            # Print a few key values to verify mapping
            print(f"  Sample UAI: {row.get('UAI', 'N/A')}")
            print(f"  Sample Nom: {row.get('Nom', row.get('Dénomination principale', 'N/A'))}")
    except Exception as e:
        print(f"Error reading {f}: {e}")
    print("\n" + "="*30 + "\n")
