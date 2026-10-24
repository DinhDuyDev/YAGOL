# @description: CELLDEF

# @section: IMPORTS
import utility

MAX_BIOWEIGHT = 255
MIN_BIOWEIGHT = 0

# @section: CELLDEF
class Cell:
    def __init__(self, x: int, y: int):
        self.x, self.y = x, y
        self.life_state = False
        self.bio_weights = [0] * 3

    def normalize_bioweights(self):
        self.bio_weights = utility.normalize(self.bio_weights)
    
    def cap_bioweight(self):
        self.bio_weights = [utility.clamp(val, 0, 255) for val in self.bio_weights]