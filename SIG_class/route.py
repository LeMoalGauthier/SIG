from SIG_class.config import NB_LIEUX


class Route :
    def __init__(self, ordre_init=None, nb_lieux=NB_LIEUX):
        from SIG_class import random
        if ordre_init is not None and ordre_init[0] == ordre_init[-1]: 
            self.ordre = ordre_init[:] 
        else: 
            lieux = random.sample(range(1, nb_lieux), nb_lieux - 1) 
            self.ordre = [0] + lieux + [0] 
    
    def __repr__(self):
        return "->".join(map(str, self.ordre))
