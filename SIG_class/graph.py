class Graph: 
    def __init__(self):
        from SIG_class import Route
        self.liste_lieux = []
        self.matrice_od = None
        self.route = Route()
    
    # Fonction de génération aléatoire de lieux 
    def generer_lieux_aleatoires(self):
        from SIG_class import random, Lieux
        from SIG_class.config import LARGEUR, HAUTEUR, NB_LIEUX
        self.liste_lieux = [Lieux(i, round(random.uniform(0, LARGEUR), 7), round(random.uniform(0, HAUTEUR), 7)) for i in range(NB_LIEUX)]
    
    # Méthode de lecture dans un fichier CSV de la liste des coordonnées des lieux 
    def charger_graph(self, fichier_csv):
        from SIG_class import csv, Lieux
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
        from SIG_class import np
        n = len(self.liste_lieux)
        self.matrice_od = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i != j:
                    self.matrice_od[i][j] = self.liste_lieux[i].calcul_dist(self.liste_lieux[j].x, self.liste_lieux[j].y)

    # Fonction de renvoie du plus proche voisin d'un lieu  
    def plus_proche_voisin(self, id_lieu):
        from SIG_class import np
        if self.matrice_od is None:
            raise ValueError("La matrice des distances n'a pas encore été calculée.")
        distances = self.matrice_od[id_lieu] 
        distances[id_lieu] = np.inf  # On ignore la distance à soi-même
        return np.argmin(distances)
    
    # Fonction de calcul de la distance totale de la route
    def calcul_distance_route(self): 
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