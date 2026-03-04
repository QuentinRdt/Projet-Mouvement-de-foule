import h3
import json

# --- 1. CHARGEMENT DES DONNÉES ---
try:
    with open('data_simulation_finale.json', 'r') as f:
        data = json.load(f)
        walkable_cells = set(data["walkable"]) # On utilise un set pour la rapidité
        print(f"Chargement de {len(walkable_cells)} cellules marchables.")
except FileNotFoundError:
    print("Erreur : Le fichier 'data_simulation_finale.json' est introuvable.")
    exit()

# --- 2. CRÉATION DU GRAPHE ---
print("Génération du graphe de voisinage...")
graphe = {}

for cell in walkable_cells:
    # On récupère les 6 voisins théoriques de la cellule
    neighbors = h3.grid_disk(cell, 1) # grid_disk avec rayon 1 donne la cellule + ses voisins
    
    valid_neighbors = []
    for n in neighbors:
        # On ne garde le voisin que si :
        # 1. C'est une cellule différente de la cellule actuelle
        # 2. Elle fait partie de notre liste de cellules "libres"
        if n != cell and n in walkable_cells:
            valid_neighbors.append(n)
    
    # On enregistre les connexions pour cette cellule
    graphe[cell] = valid_neighbors

# --- 3. SAUVEGARDE ---
with open('graphe_voisinage.json', 'w') as f:
    json.dump(graphe, f)

print(f"Succès ! Graphe généré avec {len(graphe)} nœuds.")
print("Fichier créé : 'graphe_voisinage.json'")