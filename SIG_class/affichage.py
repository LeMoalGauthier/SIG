class Affichage:
    def __init__(self, liste_lieux, nom_groupe):
        from SIG_class import tk
        from SIG_class.config import LARGEUR, HAUTEUR
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
        self.deuxieme_meilleure_distance = float('inf')
        self.deuxieme_meilleure_route = None

        # Bind des touches pour les fonctionnalités
        self.root.bind("<Escape>", self.quitter_programme)
        self.root.bind("<space>", self.afficher_routes_et_matrice)

        # Dessiner les lieux sur le canvas
        self.dessiner_lieux()
        
    def dessiner_meilleure_route(self):
        """Dessine les deux meilleures routes trouvées sous forme de lignes pointillées."""
        # Effacer les routes précédentes
        self.canvas.delete("route")

        # Dessiner la meilleure route
        if self.meilleure_route and len(self.meilleure_route) == len(set(self.meilleure_route)):
            points = [(self.liste_lieux[i].x, self.liste_lieux[i].y) for i in self.meilleure_route]
            for i in range(len(points) - 1):
                self.canvas.create_line(points[i], points[i + 1], fill="blue", dash=(5, 2), tags="route")
            for idx, lieu_id in enumerate(self.meilleure_route):
                lieu = self.liste_lieux[lieu_id]
                self.canvas.create_text(lieu.x, lieu.y - 30, text=str(idx), fill="black", font=("Arial", 10, "bold"))

        # Dessiner la deuxième meilleure route
        if self.deuxieme_meilleure_route and len(self.deuxieme_meilleure_route) == len(set(self.deuxieme_meilleure_route)):
            points = [(self.liste_lieux[i].x, self.liste_lieux[i].y) for i in self.deuxieme_meilleure_route]
            for i in range(len(points) - 1):
                self.canvas.create_line(points[i], points[i + 1], fill="red", dash=(5, 2), tags="route")
            for idx, lieu_id in enumerate(self.deuxieme_meilleure_route):
                lieu = self.liste_lieux[lieu_id]
                self.canvas.create_text(lieu.x, lieu.y - 30, text=str(idx), fill="black", font=("Arial", 10, "bold"))

    def mettre_a_jour_iteration(self, distance_trouvee, route):
        """Met à jour les meilleures routes si de nouvelles distances plus courtes sont trouvées."""
        from SIG_class import tk
        from SIG_class.config import NB_LIEUX
        self.nb_iterations = NB_LIEUX

        # Vérifie que tous les lieux sont visités une seule fois avant de revenir au point de départ
        if len(route) == len(set(route)) + 1 and route[0] == route[-1]:
            if distance_trouvee < self.meilleure_distance:
                self.deuxieme_meilleure_distance = self.meilleure_distance
                self.deuxieme_meilleure_route = self.meilleure_route
                self.meilleure_distance = distance_trouvee
                self.meilleure_route = route[:-1]  # Exclut le retour au point de départ pour l'affichage
            elif distance_trouvee < self.deuxieme_meilleure_distance:
                self.deuxieme_meilleure_distance = distance_trouvee
                self.deuxieme_meilleure_route = route[:-1]

            # Dessiner les deux meilleures routes
            self.dessiner_meilleure_route()

        # Mettre à jour les informations affichées
        self.info_zone.delete("1.0", tk.END)
        self.info_zone.insert(tk.END, f"Nombre d'itérations : {self.nb_iterations}\n")
        self.info_zone.insert(tk.END, f"Meilleure distance trouvée : {self.meilleure_distance:.2f}\n")

    def dessiner_lieux(self, lieu_depart=None):
        """Dessine les lieux sous forme de cercles avec leurs identifiants."""
        rayon = 20  # Rayon des cercles
        for lieu in self.liste_lieux:
            x, y = lieu.x, lieu.y
            couleur = "blue"  # Couleur par défaut
            if lieu.id_lieu == lieu_depart:  # Si c'est le lieu de départ
                couleur = "red"  # Couleur du lieu de départ

            self.canvas.create_oval(x - rayon, y - rayon, x + rayon, y + rayon, fill=couleur)
            self.canvas.create_text(x, y, text=str(lieu.id_lieu), fill="white", font=("Arial", 10, "bold"))

    def afficher_routes_et_matrice(self, event=None):
        """Affiche les N meilleures routes et la matrice des coûts."""
        from SIG_class import tk
        self.info_zone.insert(tk.END, "Affichage des meilleures routes et de la matrice des coûts...\n")

    def quitter_programme(self, event=None):
        """Ferme la fenêtre Tkinter et quitte le programme."""
        self.root.destroy()