import numpy as np
import random
import time
import pandas as pd
import tkinter as tk
import csv

LARGEUR = 800
HAUTEUR = 600
NB_LIEUX = 5 # Seulement {5, 20 ou 200}

# ----------------------------------------------- #
#               Classes utilitaires               #
# ----------------------------------------------- #
class Lieux:
    def __init__(self, id_lieu, x, y):
        self.id_lieu = id_lieu 
        self.x = x 
        self.y = y
    
    def __repr__(self):
        return f"{self.id_lieu}: ({self.x}, {self.y})"

    def calcul_dist(self, a, b):
        """Calcul de la distance euclidienne entre deux lieux."""
        return np.linalg.norm([self.x - a, self.y - b])

class Graph: 
    def __init__(self, route): 
        self.liste_lieux = []
        self.matrice_od = None 
        self.route = route
    
    def generer_lieux_aleatoires(self):
        """Génère aléatoirement des lieux (id et coordonnées)."""
        self.liste_lieux = [Lieux(i, round(random.uniform(0, LARGEUR), 7), round(random.uniform(0, HAUTEUR), 7)) for i in range(NB_LIEUX)]
    
    def charger_graph(self, fichier_csv):
        """Lit dans un fichier CSV la liste des coordonnées de lieux."""
        with open(fichier_csv, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader) 
            i = 0 # Ajout d'un id pour chaque lieu 
            for row in reader:
                x, y = float(row[0]), float(row[1])
                self.liste_lieux.append(Lieux(i, x, y))
                i+=1 

    def calcul_matrice_cout_od(self): 
        """Calcul la matrice de distances entre chaque lieu d'un graph."""
        n = len(self.liste_lieux)
        self.matrice_od = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i != j:
                    self.matrice_od[i][j] = self.liste_lieux[i].calcul_dist(self.liste_lieux[j].x, self.liste_lieux[j].y)

    def plus_proche_voisin(self, id_lieu): 
        """Renvoie le plus proche voisin d'un lieu."""
        if self.matrice_od is None:
            raise ValueError("La matrice des distances n'a pas encore été calculée.")
        distances = self.matrice_od[id_lieu] 
        distances[id_lieu] = np.inf  # On ignore la distance à soi-même
        return np.argmin(distances)
    
    def calcul_distance_route(self): 
        """Calcul la distance totale d'une route."""
        distance_totale = 0
        # print(f"Longueur totale de la route : {len(self.route.ordre) - 1}")
        # print(f"Route : {self.route.ordre}")
        # print(f"Liste de lieux : {self.liste_lieux}")
        for i in range(len(self.route.ordre) - 1):  # Itération sur l'ordre de la route
            # Accéder aux lieux selon les indices
            # print(f"indice lieu_actuel: {i}")
            lieu_actuel = self.liste_lieux[self.route.ordre[i]]
            # print(f"lieu_actuel: {lieu_actuel}")
            try:
                # print(f"indice lieu_suivant: {i+1}")
                lieu_suivant = self.liste_lieux[self.route.ordre[i + 1]]
                # print(f"lieu_suivant: {lieu_suivant}")
            except IndexError:
                print(f"Erreur : l'index {self.route.ordre[i + 1]} dépasse la taille de la liste des lieux ({len(self.liste_lieux)})")
                return
            
            distance = lieu_actuel.calcul_dist(lieu_suivant.x, lieu_suivant.y)
            distance_totale += distance
        return distance_totale
            

class Route :
    def __init__(self, ordre_init=None, nb_lieux=NB_LIEUX):
        if ordre_init is not None and ordre_init[0] == ordre_init[-1]: 
            self.ordre = ordre_init[:] 
        else: 
            lieux = random.sample(range(1, nb_lieux), nb_lieux - 1) 
            self.ordre = [0] + lieux + [0] 
    
    def __repr__(self):
        return "->".join(map(str, self.ordre))


class Affichage:
    def __init__(self, liste_lieux, nom_groupe, N_meilleures_routes=5):
        self.liste_lieux = liste_lieux
        self.N_meilleures_routes = N_meilleures_routes  # Nombre de meilleures routes à afficher
        self.meilleures_routes = []  # Liste pour stocker les meilleures routes
        self.root = tk.Tk()
        self.root.title(f"Visualisation du Graphe - {nom_groupe}")

        # Création du Canvas pour afficher les lieux
        self.canvas = tk.Canvas(self.root, width=LARGEUR, height=HAUTEUR, bg="white")
        self.canvas.pack()

        # Zone de texte pour afficher les informations
        self.info_zone = tk.Text(self.root, height=5, width=80)
        self.info_zone.pack()
        
        # Variables pour le suivi des algorithmes
        self.nb_iterations = 0
        self.meilleure_distance = float('inf')
        self.meilleure_route = None

        # Bind des touches pour les fonctionnalités
        self.root.bind("<Escape>", self.quitter_programme)
        self.root.bind("<space>", self.afficher_N_meilleures_routes)

        # Dessiner les lieux sur le canvas
        self.dessiner_lieux()
        
    def dessiner_meilleure_route(self):
        """Dessine la meilleure route trouvée sous forme d'une ligne pointillée avec des labels clairs."""
        if self.meilleure_route and len(self.meilleure_route[:-1]) == len(set(self.meilleure_route[:-1])):  # Vérifie que tous les lieux sauf le dernier sont uniques
            self.canvas.delete("route")  # Supprime la route précédente
            self.canvas.delete("num_label")  # Supprime les anciens numéros
            
            points = [(self.liste_lieux[i].x, self.liste_lieux[i].y) for i in self.meilleure_route]

            # Dessiner une ligne pointillée entre chaque lieu
            for i in range(len(points) - 1):
                self.canvas.create_line(points[i], points[i + 1], fill="blue", dash=(5, 2), tags="route")

            # Afficher l'ordre de visite des lieux
            for idx, lieu_id in enumerate(self.meilleure_route[:-1]):  # Exclure le dernier retour au départ
                lieu = self.liste_lieux[lieu_id]
                self.canvas.create_text(lieu.x, lieu.y - 30, text=str(idx), fill="black", font=("Arial", 10, "bold"), tags="num_label")

    def mettre_a_jour_iteration(self, distance_trouvee, route):
        """Met à jour la meilleure route si une nouvelle distance plus courte est trouvée."""
        self.nb_iterations += 1

        # Vérifie que tous les lieux sont visités une seule fois avant de revenir au point de départ
        if len(route[:-1]) == len(set(route[:-1])) and route[0] == route[-1]:  
            if distance_trouvee < self.meilleure_distance:
                self.meilleure_distance = distance_trouvee
                self.meilleure_route = route
                self.dessiner_meilleure_route() 

        # Ajouter la nouvelle route si la liste n'est pas encore pleine
        if len(self.meilleures_routes) < self.N_meilleures_routes:
            self.meilleures_routes.append((route, distance_trouvee))
        else:
            # La liste est pleine, on remplace la route ayant la plus grande distance si la nouvelle est plus courte
            max_distance_route_index = max(range(len(self.meilleures_routes)), key=lambda i: self.meilleures_routes[i][1])
            if distance_trouvee < self.meilleures_routes[max_distance_route_index][1]:
                self.meilleures_routes[max_distance_route_index] = (route, distance_trouvee)
                
        # Tri des meilleures routes par distance (de la plus petite à la plus grande)
        self.meilleures_routes.sort(key=lambda x: x[1])  # Trie par la deuxième valeur (distance)

        # Mettre à jour les informations affichées
        self.info_zone.delete("1.0", tk.END)
        self.info_zone.insert(tk.END, f"Nombre d'itérations : {self.nb_iterations}\n")
        self.info_zone.insert(tk.END, f"Meilleure distance trouvée : {self.meilleure_distance:.7f}\n")

    def dessiner_lieux(self):
        """Dessine les lieux sous forme de cercles avec leurs identifiants."""
        rayon = 20  # Rayon des cercles
        for lieu in self.liste_lieux:
            x, y = lieu.x, lieu.y
            self.canvas.create_oval(x - rayon, y - rayon, x + rayon, y + rayon, fill="blue")
            self.canvas.create_text(x, y, text=str(lieu.id_lieu), fill="white", font=("Arial", 10, "bold"))

    def afficher_N_meilleures_routes(self, event=None):
        """Affiche les 5 meilleures routes en gris clair et la matrice des coûts."""
        self.info_zone.delete("1.0", tk.END)  # Efface le texte précédent
        self.info_zone.insert(tk.END, f"Meilleures {self.N_meilleures_routes} Routes trouvées :\n")
            
        # Limite le nombre de routes affichées à N_meilleures_routes
        for idx, route in enumerate(self.meilleures_routes[:self.N_meilleures_routes]):
            route_text = " -> ".join(str(lieu_id) for lieu_id in route)
            self.info_zone.insert(tk.END, f"Route {idx + 1}: {route_text}\n")

    def quitter_programme(self, event=None):
        """Ferme la fenêtre Tkinter et quitte le programme."""
        self.root.destroy()


# Test Classes Unitaires 

# Test Classe lieux 
lieu1 = Lieux("lieu_0", 2, 3)
# Calcul de distance euclidienne 
dist = lieu1.calcul_dist(5, 7) 
print(f"Distance : {dist}") 

# Test Classe Graph 
route = Route() 
graph1 = Graph(route)
graph2 = Graph(route)
# Génération de lieux aléatoirement 
graph1.generer_lieux_aleatoires()
lieu1 = graph1.liste_lieux[0]
lieu2 = graph1.liste_lieux[1]
print(f"Lieu généré : {lieu1.id_lieu}, {lieu1.x}, {lieu1.y}")
print(f"Lieu généré : {lieu2.id_lieu}, {lieu2.x}, {lieu2.y}")
# Lecture de la liste des coordonnées des lieux d'un fichier CSV 
graph2.charger_graph(f'Data/graph_{NB_LIEUX}.csv')
print(f"Liste des lieux générés : {graph2.liste_lieux[0].id_lieu}, {graph2.liste_lieux[0].x}, {graph2.liste_lieux[0].y}")
print(f"Liste des lieux générés : {graph2.liste_lieux[1].id_lieu}, {graph2.liste_lieux[1].x}, {graph2.liste_lieux[1].y}")
# Calcul d'une matrice de distance
graph2.calcul_matrice_cout_od() 
print(f"Matrice de cout : {graph2.matrice_od}")
# Plus proche voisin 
ppv_2 = graph2.plus_proche_voisin(2)
print(f"Plus proche voisin du lieu 2 : {ppv_2}")
# Calcul de la distance totale de la route
dist = graph2.calcul_distance_route()
print(f"Distance de la route : {dist}")

# Test Classe Affichage 
affichage = Affichage(graph2.liste_lieux, "Groupe - H")
# Simulation d'un algorithme (boucle de 10 itérations)
for i in range(10):
    meilleure_distance = random.uniform(100, 500)  # Simule une distance
    route_ex = [1, 2, 3, 4] # Simule une route 
    meilleure_route = [0] + random.sample(route_ex, len(route_ex)) + [0]
    affichage.mettre_a_jour_iteration(meilleure_distance, meilleure_route)
affichage.root.mainloop()


# ----------------------------------------------- #
#               Algorithme Génétique              #
# ----------------------------------------------- #
class TSP_GA:
    def __init__(self, nb_lieux=NB_LIEUX):
        self.nb_lieux = nb_lieux
        self.list_route_ind = []
        self.list_adapt_route = []

    def gen_individu(self, population_size):
        self.list_route_ind = [Route(nb_lieux=self.nb_lieux) for _ in range(population_size)]
    
    def calc_adapt(self, fichier_csv=None):
        self.list_adapt_route = []
        for i in range(len(self.list_route_ind)):
            graph = Graph(self.list_route_ind[i])

            if fichier_csv == None:
                graph.generer_lieux_aleatoires()
            else: 
                graph.charger_graph(fichier_csv)

            graph.calcul_matrice_cout_od() 
            self.list_adapt_route.append(graph.calcul_distance_route())

        self.list_adapt_route = list(map(float, self.list_adapt_route))
        print(f"Distances routes des individus générés : \n {self.list_adapt_route}")
        # Normaliser l'adaptabilité (inverse de la distance pour maximiser les meilleurs)
        max_dist = max(self.list_adapt_route)
        self.list_adapt_route = [round(max_dist - d, 2) for d in self.list_adapt_route]
    
    def selection_parents(self, K):
        """Sélectionne M/2 couples de parents par tournoi"""
        M = len(self.list_route_ind)
        parents = [] 

        for _ in range(M // 2):
            # Sélectionner aléatoirement K individus
            indices_selectionnes = random.sample(range(M), K)
            
            # Trouver le meilleur individu parmi la sous-population
            meilleur_indice = max(indices_selectionnes, key=lambda i: self.list_adapt_route[i])
            parent1 = self.list_route_ind[meilleur_indice]

            # Répéter pour le deuxième parent
            indices_selectionnes = random.sample(range(M), K)
            meilleur_indice = max(indices_selectionnes, key=lambda i: self.list_adapt_route[i])
            parent2 = self.list_route_ind[meilleur_indice]

            # Ajouter le couple de parents
            parents.append((parent1, parent2))

        return parents
    
    # def crossover(self):
    #     return
    
    # def mutation(self):
    #     return

# Test Class Algo Genetique (TSP_GA)
nb_ind = 10
K = 3

# Test Génération d'individus
TSP_gen = TSP_GA()
TSP_gen.gen_individu(nb_ind)
print(f"Population d'individus générés : \n {TSP_gen.list_route_ind}")

# Test Calcul des distances totales de routes pour l'adaptabilité
TSP_gen.calc_adapt(f'C:/Users/User/OneDrive - yncréa/Documents/Cours/SIG/Data/graph_{NB_LIEUX}.csv')
print(f"Adaptabilité des individus générés : \n {TSP_gen.list_adapt_route}")

# Test Sélection des parents
parents = TSP_gen.selection_parents(K)
print(f"Couples de parents sélectionnés : \n {parents}")