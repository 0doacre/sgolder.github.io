
import pandas as pd
import json
import os

# Configuration
FILES = {
    "geo": "Temporaire_pour_carte_ULIS.xlsx",
    "details": "Affectation ULIS-ETABLISSEMENTS.xlsx"
}
OUTPUT_FILE = "data_ulis.js"

def clean_uai(series):
    return series.astype(str).str.strip().str.upper()

def get_degree(row):
    # Priority to Geo file 'Degré' if available and valid
    if pd.notnull(row.get('Degré_geo')):
        return row['Degré_geo']
    
    # Fallback to 'Type' from Details file
    tipo = str(row.get('Type', '')).upper().strip()
    if tipo in ['EEPU', 'EMPU', 'EPPU', 'ECOLE', 'ELEM']:
        return "1er degré"
    elif tipo in ['CLG', 'LPO', 'LYC', 'EREA', 'LP', 'LGT']:
        return "2nd degré"
    
    return "Indéterminé"

def main():
    print("Loading Excel files...")
    try:
        df_geo = pd.read_excel(FILES["geo"])
        df_details = pd.read_excel(FILES["details"])
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    print("Cleaning data...")
    # Normalize UAI for joining
    df_geo['UAI'] = clean_uai(df_geo['UAI'])
    df_details['UAI'] = clean_uai(df_details['UAI'])

    # Rename geo columns to avoid collision during merge or for clarity
    df_geo = df_geo.rename(columns={
        'Degré': 'Degré_geo',
        'Circonscription': 'Circo_geo',
        'PAS.1.Latitude': 'lat', 
        'PAS.1.Longitude': 'lng'
    })

    # Merge
    merged = pd.merge(df_details, df_geo[['UAI', 'lat', 'lng', 'Degré_geo', 'Circo_geo']], on='UAI', how='left')

    print(f"Total records after merge: {len(merged)}")

    data_list = []
    skipped_zero_ulis = 0
    missing_coords_count = 0

    for _, row in merged.iterrows():
        # FILTER 1: Skip if 0 ULIS / Inactive
        # Logic: If 'ULIS' is False AND 'Capacité d'accueil' is 0 or NaN, we skip.
        # Based on inspection: 'ULIS' col is boolean. 'Capacité d'accueil' has 0s.
        is_ulis_active = row.get('ULIS') == True or (pd.notnull(row.get("Capacité d'accueil")) and float(row.get("Capacité d'accueil")) > 0)
        
        if not is_ulis_active:
            skipped_zero_ulis += 1
            continue

        # FILTER 2: Specialized Devices (DAR, UEEA, etc.)
        # 'Dispositif spécifique' col has values like 'DAR', 'TSA', 'TDL'.
        spec_device = str(row.get('Dispositif spécifique', 'nan')).strip()
        is_special = spec_device.upper() not in ['NAN', 'NONE', '']
        
        # Determine strict Degree/Category
        # If specialized, we might want to override degree or just add a flag?
        # User asked for "new color/filter". So we can treat it as a distinct "degre" value for the frontend.
        final_degre = get_degree(row)
        if is_special:
            final_degre = f"Dispositif Spécialisé ({spec_device})"

        # Validate coordinates
        has_coords = pd.notnull(row['lat']) and pd.notnull(row['lng'])
        
        if not has_coords:
            missing_coords_count += 1
            print(f"WARNING: No coordinates for {row['UAI']} - {row.get('Dénomination principale', 'Unknown')}")
            continue

        # Robust coordinate parsing (User request: handle commas)
        try:
            lat = float(str(row['lat']).replace(',', '.'))
            lng = float(str(row['lng']).replace(',', '.'))
        except ValueError:
            print(f"WARNING: Invalid coordinates for {row['UAI']}: {row['lat']}, {row['lng']}")
            continue

        item = {
            "uai": row['UAI'],
            "nom": str(row.get('Dénomination principale', '')).strip() + " " + str(row.get('Dénomination complémentaire', '')).strip(),
            "ville": str(row.get('Ville', '')).strip(),
            "adresse": str(row.get('Adresse', '')).strip(),
            "degre": final_degre, 
            "spec_type": spec_device if is_special else "",
            "circo": str(row.get('Circonscription', row.get('Circo_geo', ''))).strip(),
            "lat": lat,
            "lng": lng,
            "coordo": str(row.get('Coordonnateur ULIS', 'Non renseigné')),
            "capa": int(row["Capacité d'accueil"]) if pd.notnull(row.get("Capacité d'accueil")) else 0,
            "erseh": str(row.get('ERSEH', 'Non renseigné'))
        }
        
        # Cleanup "nan" strings that might appear from empty pandas cells converted to str
        for k, v in item.items():
            if v == "nan" or v == "nan nan":
                item[k] = ""
        
        data_list.append(item)

    print(f"Stats: {len(data_list)} valid items exported. {missing_coords_count} items missing coordinates.")

    # Write JS file
    js_content = f"const dataUlis = {json.dumps(data_list, ensure_ascii=False, indent=2)};"
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(js_content)
    
    print(f"Successfully wrote {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
