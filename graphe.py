import pandas as pd
import json
import h3

# 1. Chargement de ta base de données H3 (extraite de ton fichier h3.csv nettoyé)
df = pd.read_csv('h3.csv') 

# On ne garde que les cellules "Libres" (couleur_val == 0) pour créer le passage
cellules_libres = df[df['couleur_val'] == 0]['h3_id'].tolist()

# 2. Construction du Graphe d'Adjacence
# Un graphe est un dictionnaire : { 'cellule_A': ['voisin_1', 'voisin_2'], ... }
graphe = {}

for cell in cellules_libres:
    # h3.grid_disk(cell, 1) renvoie la cellule + ses 6 voisins directs
    # C'est la fonction mathématique de base de la grille hexagonale
    voisins_potentiels = h3.grid_disk(cell, 1)
    
    # On ne garde que les voisins qui existent réellement dans nos zones "Libres"
    voisins_valides = [v for v in voisins_potentiels if v in cellules_libres and v != cell]
    
    # On enregistre la connexion dans notre structure de données
    graphe[cell] = voisins_valides

# 3. Sauvegarde pour la simulation
with open('graphe_voisinage.json', 'w') as f:
    json.dump(graphe, f)

print(f"Graphe généré : {len(graphe)} nœuds connectés.")
