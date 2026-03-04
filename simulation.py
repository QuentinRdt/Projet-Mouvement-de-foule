'''import json
import collections
import h3

# --- 1. CHARGEMENT DES DONNÉES ---
print("Chargement des données...")
with open('data_simulation_finale.json', 'r') as f:
    data = json.load(f)
    walkable = data["walkable"] # Liste des cellules où on peut marcher

with open('graphe_voisinage.json', 'r') as f:
    graphe = json.load(f)

# --- 2. FONCTION POUR TROUVER LA CELLULE LA PLUS PROCHE ---
def trouver_plus_proche(cible_lat_lng, liste_cellules):
    plus_proche = None
    dist_min = float('inf')
    for cell in liste_cellules:
        lat, lng = h3.cell_to_latlng(cell)
        d = h3.great_circle_distance(cible_lat_lng, (lat, lng), unit='m')
        if d < dist_min:
            dist_min = d
            plus_proche = cell
    return plus_proche

# Coordonnées cibles
coord_mairie = (48.3906, -4.4852)
coord_strasbourg = (48.4063, -4.4647)

print("Recherche des cellules correspondantes dans votre fichier...")
START_NODE = trouver_plus_proche(coord_mairie, walkable)
END_NODE = trouver_plus_proche(coord_strasbourg, walkable)

print(f"Nouveau Départ détecté : {START_NODE}")
print(f"Nouvelle Arrivée détectée : {END_NODE}")

# --- 3. ALGORITHME DE RECHERCHE DE CHEMIN (BFS) ---
def trouver_chemin(graphe, depart, arrivee):
    queue = collections.deque([(depart, [depart])])
    visite = {depart}
    while queue:
        (vertex, path) = queue.popleft()
        for neighbor in graphe.get(vertex, []):
            if neighbor == arrivee:
                return path + [arrivee]
            if neighbor not in visite:
                visite.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None

# --- 4. EXÉCUTION ---
print("Calcul de l'itinéraire...")
chemin_final = trouver_chemin(graphe, START_NODE, END_NODE)

if chemin_final:
    print(f"✅ SUCCÈS ! Chemin trouvé : {len(chemin_final)} pas.")
    with open('chemin_agent_1.json', 'w') as f:
        json.dump(chemin_final, f)
else:
    print("❌ Toujours aucun chemin. Le réseau est probablement coupé par des obstacles.")'''

import json
import pandas as pd
import datetime

# --- 1. CONFIGURATION ---
NB_AGENTS = 50
INTERVALLE_DEPART = 10  # Un nouvel agent part toutes les 10 secondes
VITESSE_PAS = 1         # Chaque hexagone (pas) prend 1 seconde (env. 1.5m/s)

# --- 2. CHARGEMENT DU TRAJET ---
try:
    with open('chemin_agent_1.json', 'r') as f:
        trajet_unique = json.load(f)
    print(f"Trajet chargé : {len(trajet_unique)} pas.")
except FileNotFoundError:
    print("Erreur : Le fichier 'chemin_agent_1.json' est introuvable.")
    exit()

# --- 3. GÉNÉRATION DE LA FOULE ---
print(f"Génération de {NB_AGENTS} agents en cours...")
donnees_simulation = []

# Heure de référence pour la simulation (Aujourd'hui à 08:00:00)
base_time = datetime.datetime(2023, 10, 27, 8, 0, 0)

for agent_id in range(NB_AGENTS):
    # Calcul du moment où cet agent commence à marcher
    temps_depart_agent = agent_id * INTERVALLE_DEPART
    
    for i, h3_id in enumerate(trajet_unique):
        # Calcul du temps exact pour chaque pas de cet agent
        temps_actuel = base_time + datetime.timedelta(seconds=temps_depart_agent + (i * VITESSE_PAS))
        
        donnees_simulation.append({
            "timestamp": temps_actuel.strftime('%Y-%m-%d %H:%M:%S'),
            "agent_id": f"Agent_{agent_id:02d}",
            "h3_id": h3_id,
            "vitesse": "1.5m/s"
        })

# --- 4. EXPORTATION ---
df = pd.DataFrame(donnees_simulation)
df.to_csv('simulation_foule_jaurès.csv', index=False)

print(f"✅ Simulation terminée !")
print(f"Fichier créé : 'simulation_foule_jaurès.csv' ({len(df)} lignes)")