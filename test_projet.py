import h3
import osmnx as ox
import json
import pandas as pd
import warnings

# On désactive les alertes de géométrie pour plus de clarté
warnings.filterwarnings("ignore")

# --- 1. CONFIGURATION ---
RESOLUTION = 15
POINT_DEPART  = "Hôtel de Ville, Brest, France"
ADRESSE = "Rue Jean Jaurès, Brest, France"
DISTANCE_VUE = 1200  # Distance pour couvrir de Liberté à Strasbourg
LARGEUR_RUE = 0.00015 # Environ 15-18 mètres de large

print("=== DÉMARRAGE DE L'EXTRACTION GÉOGRAPHIQUE ===")

# --- 2. RÉCUPÉRATION DU RÉSEAU ET DES BÂTIMENTS ---
print("[1/3] Téléchargement du réseau routier et des bâtiments...")
G = ox.graph_from_address(POINT_DEPART, dist=DISTANCE_VUE, network_type='walk')
nodes, edges = ox.graph_to_gdfs(G)

# Filtrage de la rue Jean Jaurès uniquement
jaures_edges = edges[edges['name'].str.contains('Jaurès', na=False)]
# Création de la surface de la rue (le ruban)
street_geometry = jaures_edges.geometry.buffer(LARGEUR_RUE).union_all()

# --- 3. SOUSTRACTION DES BÂTIMENTS (ZONES INTERDITES) ---
print("[2/3] Nettoyage de la zone (retrait des bâtiments)...")
buildings = ox.features_from_address(POINT_DEPART, tags={'building': True}, dist=DISTANCE_VUE)
building_union = buildings.geometry.union_all()
walkable_surface = street_geometry.difference(building_union)

# Conversion de la surface en cellules H3
from shapely.geometry import Point

# --- 3. GÉNÉRATION DES CELLULES H3 AVEC FILTRE DE PRÉCISION ---
all_cells_raw = set()
if walkable_surface.geom_type == 'Polygon':
    polys = [walkable_surface]
else:
    polys = list(walkable_surface.geoms)

for poly in polys:
    coords = [(c[1], c[0]) for c in list(poly.exterior.coords)]
    h3_poly = h3.LatLngPoly(coords)
    # On récupère toutes les cellules potentielles
    potential_cells = h3.polygon_to_cells(h3_poly, RESOLUTION)
    
    for cell in potential_cells:
        # TEST DE PRÉCISION : On vérifie si le centre de l'hexagone est DANS la rue
        lat, lng = h3.cell_to_latlng(cell)
        point_centre = Point(lng, lat) # Attention : Point prend (x, y) donc (lng, lat)
        
        if walkable_surface.contains(point_centre):
            all_cells_raw.add(cell)

all_cells = all_cells_raw

# --- 4. IDENTIFICATION DU MOBILIER URBAIN (OBSTACLES) ---
print("[3/3] Détection du mobilier urbain (arbres, bancs, arrêts)...")
tags_obstacles = {
    'amenity': ['bench', 'shelter', 'waste_basket'],
    'natural': ['tree'],
    'highway': ['bus_stop', 'lighting'],
    'railway': ['tram_stop'],
    'man_made': ['pole']
}

final_walkable = all_cells.copy()
street_obstacles = set()

try:
    pois = ox.features_from_address(ADRESSE, tags=tags_obstacles, dist=DISTANCE_VUE)
    for _, row in pois.iterrows():
        point = row.geometry.centroid
        h_cell = h3.latlng_to_cell(point.y, point.x, RESOLUTION)
        # Si l'obstacle tombe sur une de nos cellules, on le bascule en obstacle
        if h_cell in final_walkable:
            final_walkable.remove(h_cell)
            street_obstacles.add(h_cell)
except:
    print("Info : Aucun mobilier spécifique trouvé dans cette zone.")

print(f"--- RÉSULTAT : {len(final_walkable)} cellules libres / {len(street_obstacles)} obstacles ---")

# --- 5. EXPORTATION DES DONNÉES ---
print("=== GÉNÉRATION DES FICHIERS DE SORTIE ===")

# A. Sauvegarde JSON (pour ton futur moteur de simulation)
with open('data_simulation_jaures.json', 'w') as f:
    json.dump({
        "walkable": list(final_walkable),
        "obstacles": list(street_obstacles)
    }, f)

# B. Sauvegarde CSV (pour Kepler.gl ou H3 Tutorial)
df_visu = []
for c in final_walkable: df_visu.append({"h3_id": c, "couleur_val": 0, "type": "Libre"})
for c in street_obstacles: df_visu.append({"h3_id": c, "couleur_val": 1, "type": "Obstacle"})
pd.DataFrame(df_visu).to_csv('visu_jaures_couleurs.csv', index=False)

print("=============================================")
print("SUCCÈS ! Fichiers créés :")
print("- data_simulation_jaures.json")
print("- visu_jaures_couleurs.csv")
print("=============================================")