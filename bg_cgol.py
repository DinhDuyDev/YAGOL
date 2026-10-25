import settings
import random
import cell
import ruleset

class BGCGol:
    w = settings.HCELLS
    h = settings.VCELLS
    matrix: list[list[cell.Cell]] = [[cell.Cell(j, i) for i in range(settings.HCELLS)] for j in range(settings.VCELLS)]
    def setup():
        for i in range(settings.VCELLS):
            for j in range(settings.HCELLS):
                BGCGol.matrix[i][j].life_state = random.choice([0, 1])
    def next():
        nextStates = [[BGCGol.matrix[i][j].life_state for j in range(settings.HCELLS)] for i in range(settings.VCELLS)]
        for i in range(settings.VCELLS):
            for j in range(settings.HCELLS):
                neighborCount = ruleset.getNeighbors(BGCGol.matrix, i, j)[0]
                if neighborCount < 2 or neighborCount > 3: nextStates[i][j] = False
                if neighborCount == 3 and not BGCGol.matrix[i][j].life_state: nextStates[i][j] = True

        for i in range(settings.VCELLS): 
            for j in range(settings.HCELLS): 
                BGCGol.matrix[i][j].life_state = nextStates[i][j]