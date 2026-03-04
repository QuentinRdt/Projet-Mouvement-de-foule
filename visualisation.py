import pandas as pd
import json

# Charger le chemin calculé
with open('chemin_agent_1.json', 'r') as f:
    chemin = json.load(f)

# Créer une liste de dictionnaires pour le CSV
df_chemin = []
for i, h3_id in enumerate(chemin):
    df_chemin.append({
        "h3_id": h3_id,
        "ordre": i,          # Permet de voir la progression du trajet
        "type": "Trajet"
    })

# Sauvegarder
pd.DataFrame(df_chemin).to_csv('visualisation_chemin.csv', index=False)
print("Fichier 'visualisation_chemin.csv' créé pour Kepler.gl !")