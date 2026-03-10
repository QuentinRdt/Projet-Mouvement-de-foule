import json
import random
import collections
import pandas as pd
import datetime

# --- CONFIGURATION ---
NB_AGENTS = 50          # Nombre total de piétons
INTERVALLE_DEPART = 10  # Un agent entre dans la rue toutes les 10 secondes (Headway)

# --- CHARGEMENT DU MONDE ---
with open('graphe_voisinage.json', 'r') as f:
    graphe = json.load(f)

# Coordonnées cibles (Mairie -> Strasbourg)
START_NODE = "8f18716e462d499" 
END_NODE = "8f18716e486350c"

# --- ALGORITHME DE PATHFINDING (BFS) ---
def calculer_trajet(graphe, depart, arrivee):
    # 'deque' est une file optimisée pour le FIFO (First In, First Out)
    # On stocke (cellule_actuelle, chemin_parcouru_jusque_la)
    queue = collections.deque([(depart, [depart])])
    visite = {depart} # Set pour éviter de repasser sur la même cellule (boucle)

    while queue:
        # On extrait le premier élément (Parcours en Largeur)
        (actuel, chemin) = queue.popleft()
        
        # Récupération des voisins et MÉLANGE ALÉATOIRE
        # C'est ce qui permet aux agents de ne pas tous se suivre (diversité)
        voisins = graphe.get(actuel, [])
        random.shuffle(voisins) 

        for voisin in voisins:
            if voisin == arrivee:
                return chemin + [voisin] # Destination atteinte !
            
            if voisin not in visite:
                visite.add(voisin)
                queue.append((voisin, chemin + [voisin]))
    return None

# --- GÉNÉRATION DE LA POPULATION ---
resultats = []
start_time = datetime.datetime(2026, 3, 9, 8, 0, 0) # Simulation à 8h du matin

for i in range(NB_AGENTS):
    chemin = calculer_trajet(graphe, START_NODE, END_NODE)
    
    if chemin:
        depart_agent = i * INTERVALLE_DEPART
        for seconde, h3_id in enumerate(chemin):
            # On calcule l'heure exacte de l'agent à cette position
            instant = start_time + datetime.timedelta(seconds=depart_agent + seconde)
            
            resultats.append({
                "timestamp": instant.strftime('%Y-%m-%d %H:%M:%S'),
                "agent_id": f"Agent_{i:02d}",
                "h3_id": h3_id
            })

# --- EXPORT POUR KEPLER.GL ---
pd.DataFrame(resultats).to_csv('simulation_foule_finale.csv', index=False)
print("Simulation terminée : simulation_foule_finale.csv prêt.")
