import h3

# 1. Coordonnées approximatives
mairie_coords = (48.3906, -4.4852)      # Devant la Mairie
strasbourg_coords = (48.4063, -4.4647)  # Place de Strasbourg

# 2. Trouver les IDs H3 correspondants (Résolution 15)
id_mairie = h3.latlng_to_cell(mairie_coords[0], mairie_coords[1], 15)
id_strasbourg = h3.latlng_to_cell(strasbourg_coords[0], strasbourg_coords[1], 15)

print(f"ID H3 Départ (Mairie) : {id_mairie}")
print(f"ID H3 Arrivée (Strasbourg) : {id_strasbourg}")