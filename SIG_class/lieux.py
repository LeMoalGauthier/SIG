class Lieux:
    def __init__(self, id_lieu, x, y):
        self.id_lieu = id_lieu 
        self.x = x 
        self.y = y
    
    def __repr__(self):
        return f"{self.id_lieu}: ({self.x}, {self.y})"

    # Fonction de calcul de la distance (euclidienne) entre 2 lieux 
    def calcul_dist(self, a, b):
        from SIG_class import np
        return np.linalg.norm([self.x - a, self.y - b])