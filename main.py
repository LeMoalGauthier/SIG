from SIG_class import *
from SIG_class.config import NB_LIEUX

def main():
    # Tests pour la classe Lieux
    lieu1 = Lieux("lieu_0", 2, 3)
    # Calcul de distance euclidienne
    dist = lieu1.calcul_dist(5, 7)
    print(f"Distance : {dist}")

    # Tests pour la classe Graph
    graph1 = Graph()
    graph2 = Graph()
    
    # Génération de lieux aléatoires
    graph1.generer_lieux_aleatoires()
    lieu1 = graph1.liste_lieux[0]
    lieu2 = graph1.liste_lieux[1]
    print(f"Lieu généré : {lieu1.id_lieu}, {lieu1.x}, {lieu1.y}")
    print(f"Lieu généré : {lieu2.id_lieu}, {lieu2.x}, {lieu2.y}")

    # Lecture de la liste des coordonnées des lieux depuis un fichier CSV
    graph2.charger_graph(f'C:\ISEN\M2\SIG_git\SIG\Data\graph_{NB_LIEUX}.csv')
    print(f"Liste des lieux générés : {graph2.liste_lieux[0].id_lieu}, {graph2.liste_lieux[0].x}, {graph2.liste_lieux[0].y}")
    print(f"Liste des lieux générés : {graph2.liste_lieux[1].id_lieu}, {graph2.liste_lieux[1].x}, {graph2.liste_lieux[1].y}")
    
    # Calcul d'une matrice de distance
    graph2.calcul_matrice_cout_od()
    print(f"Matrice de coût : {graph2.matrice_od}")
    
    # Plus proche voisin
    ppv_2 = graph2.plus_proche_voisin(2)
    print(f"Plus proche voisin du lieu 2 : {ppv_2}")
    
    # Calcul de la distance totale de la route
    dist = graph2.calcul_distance_route()
    print(f"Distance de la route : {dist}")

    # Tests pour la classe Affichage
    affichage1 = Affichage(graph2.liste_lieux, "Meilleure route")
    affichage2 = Affichage(graph2.liste_lieux, "Deuxieme meilleure route")

    # Stockage des meilleures routes uniques
    routes_uniques = set()
    for point_de_depart in range(NB_LIEUX):
        lieux_visites = {point_de_depart}  # On commence au point 0
        ordre_route = [point_de_depart]
        distance_totale = 0
        lieu_actuel = point_de_depart  # Point de départ

        while len(lieux_visites) < NB_LIEUX:
            voisin_proche = None
            min_distance = float('inf')

            # Chercher le plus proche voisin non encore visité
            for i in range(NB_LIEUX):
                if i not in lieux_visites and 0 < graph2.matrice_od[lieu_actuel][i] < min_distance:
                    voisin_proche = i
                    min_distance = graph2.matrice_od[lieu_actuel][i]

            if voisin_proche is not None:
                ordre_route.append(voisin_proche)
                lieux_visites.add(voisin_proche)
                distance_totale += min_distance
                lieu_actuel = voisin_proche

        # Retour au point de départ
        distance_totale += graph2.matrice_od[lieu_actuel][point_de_depart]
        ordre_route.append(point_de_depart)

        # Eviter d'enregistrer la même route en aller-retour
        route_tuple = tuple(ordre_route)
        reverse_route_tuple = tuple(reversed(ordre_route))

        if reverse_route_tuple not in routes_uniques:
            routes_uniques.add(route_tuple)

    # Tri des routes par distance
    meilleures_routes = sorted(routes_uniques, key=lambda x: sum(graph2.matrice_od[x[i]][x[i+1]] for i in range(len(x)-1)))

    # Sélection des deux plus petites routes distinctes
    if len(meilleures_routes) >= 2:
        meilleure_route = meilleures_routes[0]
        seconde_meilleure_route = meilleures_routes[1]
    else:
        print("Impossible de trouver deux routes distinctes.")
        return
    
    # Afficher les distances totales des routes
    distance_meilleure = sum(graph2.matrice_od[meilleure_route[i]][meilleure_route[i+1]] for i in range(len(meilleure_route)-1))
    distance_seconde_meilleure = sum(graph2.matrice_od[seconde_meilleure_route[i]][seconde_meilleure_route[i+1]] for i in range(len(seconde_meilleure_route)-1))

    affichage1.mettre_a_jour_iteration(distance_meilleure, list(meilleure_route))
    affichage2.mettre_a_jour_iteration(distance_seconde_meilleure, list(seconde_meilleure_route))

        # Afficher les deux routes sur la fenêtre
    affichage1.dessiner_lieux(lieu_depart=meilleure_route[0])  # Passer l'ID du lieu de départ
    affichage2.dessiner_lieux(lieu_depart=seconde_meilleure_route[0])  # Passer l'ID du lieu de départ
    
    # Afficher les deux routes sur la fenêtre
    affichage1.dessiner_meilleure_route()
    affichage2.dessiner_meilleure_route()

    # Afficher les distances totales des routes
    print(f"Distance de la meilleure route : {sum(graph2.matrice_od[meilleure_route[i]][meilleure_route[i+1]] for i in range(len(meilleure_route)-1)):.2f}")
    print(f"Distance de la seconde meilleure route : {sum(graph2.matrice_od[seconde_meilleure_route[i]][seconde_meilleure_route[i+1]] for i in range(len(seconde_meilleure_route)-1)):.2f}")
    
    print(f"Lieux visités : {meilleure_route}")
    print(f"Lieux visités : {seconde_meilleure_route}")

    affichage1.root.mainloop()
    affichage2.root.mainloop()

# Appeler la fonction main pour exécuter les tests
if __name__ == "__main__":
    main()
