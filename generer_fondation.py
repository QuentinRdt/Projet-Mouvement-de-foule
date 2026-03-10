import h3

# 1. Tes coordonnées (issues de identifiant.py)
mairie = (48.3906, -4.4852)
strasbourg = (48.4063, -4.4647)

# 2. Résolution (tu utilises la 15)
RESOLUTION = 15

print("Génération de la trace de la rue...")

# On crée une ligne de cellules entre les deux points
# line_size=2 permet de donner un peu de largeur à la rue
path = h3.grid_path_cells(
    h3.latlng_to_cell(mairie[0], mairie[1], RESOLUTION),
    h3.latlng_to_cell(strasbourg[0], strasbourg[1], RESOLUTION)
)

# On élargit un peu pour couvrir les trottoirs (rayon de 2 ou 3 cellules)
all_cells = set()
for cell in path:
    neighbors = h3.grid_disk(cell, 3) 
    all_cells.update(neighbors)

# 3. Sauvegarde en CSV
import pandas as pd
df = pd.DataFrame(list(all_cells), columns=['h3_id'])
df.to_csv('h3.csv', index=False, header=False)

print(f"Succès ! {len(df)} cellules enregistrées dans 'h3.csv'.")