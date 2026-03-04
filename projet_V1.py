import h3
import osmnx as ox
import pandas as pd
import json

# --- 1. CONFIGURATION ---
RESOLUTION = 15
ADRESSE = "Rue Jean Jaurès, Brest, France"
# Rayon de recherche pour couvrir de la Mairie à Strasbourg
DISTANCE_VUE = 1200 
# Seuil de proximité pour marquer un obstacle (en mètres)
SEUIL_OBSTACLE = 2.5 

print("=== DÉMARRAGE DU TRAITEMENT DES DONNÉES ===")

# --- 2. CHARGEMENT DE TA GRILLE H3 ---
# On charge ton fichier h3.csv
try:
    df_user = pd.read_csv('h3.csv', header=None, names=['h3_id'])
    df_user['h3_id'] = df_user['h3_id'].str.strip() # Nettoyage des espaces
    user_cells = list(df_user['h3_id'])
    print(f"[1/4] {len(user_cells)} cellules chargées depuis 'h3.csv'.")
except FileNotFoundError:
    print("Erreur : Le fichier 'h3.csv' est introuvable dans le dossier.")
    exit()

# --- 3. RÉCUPÉRATION DES OBSTACLES (OSM) ---
print("[2/4] Téléchargement des obstacles réels (Brest - Rue Jean Jaurès)...")
tags_obstacles = {
    'amenity': ['bench', 'shelter', 'waste_basket', 'parking_ticket_machine'],
    'natural': ['tree'],
    'highway': ['bus_stop', 'lighting', 'street_lamp'],
    'railway': ['tram_stop'],
    'man_made': ['pole', 'utility_pole', 'mast', 'advertising']
}

try:
    # On télécharge les points d'intérêt (POIs)
    pois = ox.features_from_address(ADRESSE, tags=tags_obstacles, dist=DISTANCE_VUE)
    # On extrait les coordonnées (lat, lng) des centres de chaque obstacle
    obstacle_coords = []
    for _, row in pois.iterrows():
        point = row.geometry.centroid
        obstacle_coords.append((point.y, point.x))
    print(f"      {len(obstacle_coords)} objets trouvés sur OpenStreetMap.")
except Exception as e:
    print(f"Attention : Erreur lors du téléchargement OSM : {e}")
    obstacle_coords = []

# --- 4. IDENTIFICATION DES CELLULES OBSTACLES (PROXIMITÉ) ---
print(f"[3/4] Scan de proximité (Seuil: {SEUIL_OBSTACLE}m)...")
obstacles_identifies = set()

for h3_id in user_cells:
    lat, lng = h3.cell_to_latlng(h3_id)
    
    # Pour chaque cellule, on regarde si un obstacle OSM est proche
    for obs_lat, obs_lng in obstacle_coords:
        # Distance de grand cercle entre le centre de l'hexagone et l'objet
        dist = h3.great_circle_distance((lat, lng), (obs_lat, obs_lng), unit='m')
        
        if dist <= SEUIL_OBSTACLE:
            obstacles_identifies.add(h3_id)
            break # On a trouvé un obstacle pour cette cellule, on passe à la suivante

final_walkable = [c for c in user_cells if c not in obstacles_identifies]

print(f"      Résultat : {len(final_walkable)} libres / {len(obstacles_identifies)} obstacles.")

# --- 5. EXPORTATION DES FICHIERS ---
print("[4/4] Génération des fichiers de sortie...")

# A. Le fichier JSON pour le futur moteur de simulation
data_simu = {
    "walkable": list(final_walkable),
    "obstacles": list(obstacles_identifies)
}
with open('data_simulation_finale.json', 'w') as f:
    json.dump(data_simu, f)

# B. Le fichier CSV pour Kepler.gl (0=Vert, 1=Rouge)
df_visu = []
for c in final_walkable:
    df_visu.append({"h3_id": c, "couleur_val": 0, "type": "Libre"})
for c in obstacles_identifies:
    df_visu.append({"h3_id": c, "couleur_val": 1, "type": "Obstacle"})

pd.DataFrame(df_visu).to_csv('visu_kepler_jaurès.csv', index=False)

print("\n=== TOUT EST PRÊT ! ===")
print("- 'data_simulation_finale.json' (Pour le code de mouvement)")
print("- 'visu_kepler_jaurès.csv' (À importer dans Kepler.gl)")