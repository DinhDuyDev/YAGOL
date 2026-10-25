# @description: RULSET

# @section: IMPORTS
import cell
import utility
import random
import sounds


# @section: REUSABLES
neighbors = {
    (-1, -1), (0, -1), (1, -1),
    (-1, 0), (1, 0),
    (-1, 1), (0, 1), (1, 1)
}

# Basic ruleset:
# "Weight delta" = difference between cell and minimum or maximum of normalized cell -> basically the furthest distance away
# If the guess is too far off, the strength of bioweights is added, and weight delta at that position is recorded
# Weight delta dependents:
#   1. "birth" rates - the higher the weight delta, the lower the threshold for birth, the tighter the threshold for death. Conversely
#   2. "generation" rates - the higher the weight delta, the higher the generation rates - things become more hectic.
#   3. death rates - the lower the guesses, the higher the requirements for birth and maintenance
# "Touching" - when touching - will set 5x5 cell around the thing with the seeds. If the cells are alive then these cell's values will be set
# Interacting with other cells will mean taking the mean of the surrounding colors of that cell - this will be chaos
# #

class GameControl:
    initialSeed: tuple[int, int, int] = (
        random.randint(0, 255), 
        random.randint(0, 255), 
        random.randint(0, 255)
    )
    normalizedTargetSeed: tuple[int, int, int] = utility.clampSeq((
        initialSeed[0] + random.randint(-16, 16),
        initialSeed[0] + random.randint(-16, 16),
        initialSeed[0] + random.randint(-16, 16),
    ), 0, 255
    )
    timeStep = 10
    extent = 0.0

    def randomizeNormalized(playSound=True):
        GameControl.normalizedTargetSeed = utility.clampSeq((
            GameControl.normalizedTargetSeed[0] + random.randint(-64, 64),
            GameControl.normalizedTargetSeed[1] + random.randint(-64, 64),
            GameControl.normalizedTargetSeed[2] + random.randint(-64, 64)
            ), 0, 255
        )
        if playSound: sounds.AllSounds.announcenew.play()

    def initStable():
        GameControl.randomizeNormalized(False)
        GameControl.initialSeed = (
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        )
    killThreshold = 0.6

def getNeighbors(matrix: list[list[cell.Cell]], x: int, y: int) -> tuple[int, list[cell.Cell]]:
    w, h = len(matrix[0]), len(matrix)
    neighbor_count = 0
    neighboringCells : list[cell.Cell] = []
    for offset in neighbors:
        wX, wY = utility.wrap(x + offset[0], 0, w), utility.wrap(y + offset[1], 0, h)
        if matrix[wY][wX].life_state:
            neighbor_count += 1
            neighboringCells.append(matrix[wY][wX])
    return (neighbor_count, neighboringCells)

def ruleset(matrix: list[list[cell.Cell]]):
    w, h = len(matrix[0]), len(matrix)
    nextStates: list[list[bool]] = [[matrix[i][j].life_state for j in range(w)] for i in range(h)]
    nextBioWeight: list[list[bool]] = [[matrix[i][j].bio_weights[:] for j in range(w)] for i in range(h)] # bioweights copy

    weightDelta = 0
    cellsAlive = 1
    for i in range(h):
        for j in range(w):
            if matrix[i][j].life_state:
                cellsAlive += 1
                weightDelta += utility.arrDiff(matrix[i][j].bio_weights, GameControl.normalizedTargetSeed)

    extent = ((weightDelta / cellsAlive) / (255 * 3)) ** 0.5

    # normal extent
    lifeRange = (2, 3)
    reproduceThreshold = 3

    if extent < 0.2: # very close
        lifeRange = (4, 5)
        reproduceThreshold = 4
    elif extent < 0.4: # normal - must be a sharp "trough"
        pass
    elif extent < 0.7:
        lifeRange = (1, 3)
        reproduceThreshold == 2
    else:
        lifeRange = (1, 6)
        reproduceThreshold = 1
    GameControl.extent = extent
    
    for i in range(h):
        for j in range(w):
            ngbrs = getNeighbors(matrix, j, i)
            neighborCount = ngbrs[0]
            # dumbest fucking code ever made but oh well
            if neighborCount < lifeRange[0] or neighborCount > lifeRange[1]: nextStates[i][j] = False
            if neighborCount == reproduceThreshold and not matrix[i][j].life_state: nextStates[i][j] = True

            # next weights
            if neighborCount > 0:
                totalWeights = [0, 0, 0]
                for neighbor in ngbrs[1]:
                    totalWeights[0] += neighbor.bio_weights[0]
                    totalWeights[1] += neighbor.bio_weights[1]
                    totalWeights[2] += neighbor.bio_weights[2]
                nextBioWeight[i][j] = [val / neighborCount for val in totalWeights] if nextStates[i][j] else [0,0,0]

    for i in range(h): 
        for j in range(w): 
            matrix[i][j].life_state = nextStates[i][j]
            matrix[i][j].bio_weights = nextBioWeight[i][j]