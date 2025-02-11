import numpy as np
import random
import time
import pandas as pd
import tkinter as tk
import csv

LARGEUR = 800
HAUTEUR = 600
NB_LIEUX = 5 # Seulement {5, 20 ou 200}

class Lieux:
    def __init__(self, id_lieu, x, y):
        self.id_lieu = id_lieu 
        self.x = x 
        self.y = y
    
    def __repr__(self):
        return f"{self.id_lieu}: ({self.x}, {self.y})"

    # Fonction de calcul de la distance (euclidienne) entre 2 lieux 
    def calcul_dist(self, a, b):
        return np.linalg.norm([self.x - a, self.y - b])

class Graph: 
    def __init__(self): 
        self.liste_lieux = []
        self.matrice_od = None 
        self.route = Route()
    
    # Fonction de génération aléatoire de lieux 
    def generer_lieux_aleatoires(self):
        self.liste_lieux = [Lieux(i, round(random.uniform(0, LARGEUR), 7), round(random.uniform(0, HAUTEUR), 7)) for i in range(NB_LIEUX)]
    
    # Méthode de lecture dans un fichier CSV de la liste des coordonnées des lieux 
    def charger_graph(self, fichier_csv):
        with open(fichier_csv, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader) 
            i = 0 # Ajout d'un id pour chaque lieu 
            for row in reader:
                x, y = float(row[0]), float(row[1])
                self.liste_lieux.append(Lieux(i, x, y))
                i+=1 
        global NB_LIEUX
        NB_LIEUX = i 

    # Fonction de calcul d'une matrice de distances entre chaque lieu du graphe
    def calcul_matrice_cout_od(self): 
        n = len(self.liste_lieux)
        self.matrice_od = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i != j:
                    self.matrice_od[i][j] = self.liste_lieux[i].calcul_dist(self.liste_lieux[j].x, self.liste_lieux[j].y)

    # Fonction de renvoie du plus proche voisin d'un lieu  
    def plus_proche_voisin(self, id_lieu): 
        if self.matrice_od is None:
            raise ValueError("La matrice des distances n'a pas encore été calculée.")
        distances = self.matrice_od[id_lieu] 
        distances[id_lieu] = np.inf  # On ignore la distance à soi-même
        return np.argmin(distances)
    
    # Fonction de calcul de la distance totale de la route
    def calcul_distance_route(self): 
        distance_totale = 0

        if not self.liste_lieux:
            raise ValueError("La liste des lieux est vide.")
        if self.matrice_od is None:
            self.calcul_matrice_cout_od()

        n = len(self.liste_lieux)
        visite = set()
        self.route.ordre = [0]  # Commence au premier lieu
        visite.add(0)
        distance_totale = 0

        lieu_actuel = 0  # Index du lieu actuel
        
        for _ in range(n - 1):
            voisin_proche = self.plus_proche_voisin(lieu_actuel)
            if voisin_proche in visite:
                continue  # Éviter de revisiter un lieu

            self.route.ordre.append(voisin_proche)
            visite.add(voisin_proche)
            
            # Calculer la distance et l'ajouter au total
            distance_totale += self.matrice_od[lieu_actuel][voisin_proche]
            
            # Mise à jour du lieu actuel
            lieu_actuel = voisin_proche

        # Retour au point de départ pour fermer la boucle (optionnel)
        distance_totale += self.matrice_od[lieu_actuel][0]
        self.route.ordre.append(0)

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
    def __init__(self, liste_lieux, nom_groupe):
        self.liste_lieux = liste_lieux
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
        self.root.bind("<space>", self.afficher_routes_et_matrice)

        # Dessiner les lieux sur le canvas
        self.dessiner_lieux()
        
    def dessiner_meilleure_route(self):
        """Dessine la meilleure route trouvée sous forme d'une ligne pointillée."""
        if self.meilleure_route and len(self.meilleure_route) == len(set(self.meilleure_route)):  # Vérifie que tous les lieux sont uniques
            self.canvas.delete("route")  # Supprime la route précédente
            points = [(self.liste_lieux[i].x, self.liste_lieux[i].y) for i in self.meilleure_route]

            # Dessiner une ligne pointillée entre chaque lieu
            for i in range(len(points) - 1):
                self.canvas.create_line(points[i], points[i + 1], fill="blue", dash=(5, 2), tags="route")
            
            # Afficher l'ordre de visite des lieux
            for idx, lieu_id in enumerate(self.meilleure_route):
                lieu = self.liste_lieux[lieu_id]
                self.canvas.create_text(lieu.x, lieu.y - 30, text=str(idx), fill="black", font=("Arial", 10, "bold"))

    def mettre_a_jour_iteration(self, distance_trouvee, route):
        """Met à jour la meilleure route si une nouvelle distance plus courte est trouvée."""
        self.nb_iterations += 1

        # Vérifie que tous les lieux sont visités une seule fois avant de revenir au point de départ
        if len(route) == len(set(route)) + 1 and route[0] == route[-1]:  
            if distance_trouvee < self.meilleure_distance:
                self.meilleure_distance = distance_trouvee
                self.meilleure_route = route[:-1]  # Exclut le retour au point de départ pour l'affichage
                self.dessiner_meilleure_route()

        # Mettre à jour les informations affichées
        self.info_zone.delete("1.0", tk.END)
        self.info_zone.insert(tk.END, f"Nombre d'itérations : {self.nb_iterations}\n")
        self.info_zone.insert(tk.END, f"Meilleure distance trouvée : {self.meilleure_distance:.2f}\n")

    def dessiner_lieux(self):
        """Dessine les lieux sous forme de cercles avec leurs identifiants."""
        rayon = 20  # Rayon des cercles
        for lieu in self.liste_lieux:
            x, y = lieu.x, lieu.y
            self.canvas.create_oval(x - rayon, y - rayon, x + rayon, y + rayon, fill="blue")
            self.canvas.create_text(x, y, text=str(lieu.id_lieu), fill="white", font=("Arial", 10, "bold"))

    def afficher_routes_et_matrice(self, event=None):
        """Affiche les N meilleures routes et la matrice des coûts."""
        self.info_zone.insert(tk.END, "Affichage des meilleures routes et de la matrice des coûts...\n")

    def quitter_programme(self, event=None):
        """Ferme la fenêtre Tkinter et quitte le programme."""
        self.root.destroy()


### Tests 

## Classe Graph 
graph2 = Graph()

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
ppv_4 = graph2.plus_proche_voisin(4)
print(f"Plus proche voisin du lieu 4 : {ppv_4}")
# Calcul de la distance totale de la route
# ordre = [0, 2, 4, 3, 0]
dist = graph2.calcul_distance_route()
print(f"Distance de la route : {dist}")

## Classe Affichage 
affichage = Affichage(graph2.liste_lieux, "Groupe - H")
# affichage.root.mainloop()

point_de_depart = 4
# Simulation d'un algorithme (boucle sur le nombre de lieux)
# import random
for i in range(NB_LIEUX):
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

    affichage.mettre_a_jour_iteration(distance_totale, ordre_route)
    affichage.root.update()  # Mise à jour en temps réel

print(f"Lieux visités : {lieux_visites}")
affichage.root.mainloop()
