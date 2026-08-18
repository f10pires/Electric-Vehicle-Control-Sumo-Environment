import numpy as np

class BIN :
    def __init__(self,id: str, pos: float, edge: str, area: float, occupation : float, capacity: float, time: float, population: int):

        # -----------------------------
        # Identification and location
        # -----------------------------
        self.id = id
        self.edge = edge
        self.pos = pos
        self.area = area

        # -----------------------------
        # Waste characteristics
        # -----------------------------
        self.population = population
        self.occupation = occupation
        self.capacity = capacity

        # -----------------------------
        # Simulation
        # -----------------------------
        self.time = time
        return
    
    def update(self, time, sigma) :

        self.occupation = self.occupation + (self.generation*sigma)

        return
    
    def generation_rate(self, time):
        frequency = (2 * np.pi) / 86400

        return self.population * np.sin(frequency * time)
    
    
    pass