# @description: MAIN

# @section: IMPORTS
import pygame
import settings
import cell
import ruleset
import random
import utility

# @section: SETUP
pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.RESIZABLE|pygame.DOUBLEBUF|pygame.HWSURFACE|pygame.SCALED, vsync=1)
draw_dest = screen.copy()
debug_font = pygame.sysfont.SysFont("Arial", 15, False)
clock = pygame.Clock()

matrix:list[list[cell.Cell]] = [[cell.Cell(j, i) for j in range(settings.VCELLS)] for i in range(settings.VCELLS)]

# @section: RANDOMIZE LIFE
def randomizeLife(matrix: list[list[cell.Cell]]):
    mw, mh = len(matrix[0]), len(matrix)
    for i in range(mh):
        for j in range(mw):
            matrix[i][j].life_state = True if random.random() < 0.3 else False
            matrix[i][j].bio_weights = ruleset.GameControl.initialSeed
    
# @section: GAMEPLAY
def seedLife(matrix: list[list[cell.Cell]]):
    mw, mh = len(matrix[0]), len(matrix)
    for _ in range(30):
        x = random.randint(0, mw - 1)
        y = random.randint(0, mh - 1)
        matrix[y][x].life_state = True

# @section: MAIN GAME LOOP
def game():
    ruleset.GameControl.randomizeNormalized()
    print(ruleset.GameControl.normalizedTargetSeed)
    print(ruleset.GameControl.initialSeed)
    controllable_bioweights : list[utility.numericType] = [0.0] * 3
    pointer = 0
    
    randomizeLife(matrix)
    running = True


    timestep = ruleset.GameControl.timeStep
    
    mw, mh = len(matrix[0]), len(matrix)

    SEED_REF = 5 * 60
    seedstep = SEED_REF

    while running:
        # NECESSARY EVENT LOOP - PREVENT APP FREEZE-UPs
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_e:
                    pointer = 2 if pointer == 0 else pointer - 1
            elif event.type == pygame.QUIT:
                running = False

        # LOGIC
        if timestep > 0:
            timestep -= 1
        else:
            ruleset.ruleset(matrix)
            timestep = ruleset.GameControl.timeStep / (ruleset.GameControl.extent ** 0.5)
            seedstep -= 1
            if not seedstep: 
                if ruleset.GameControl.extent > 0.6: 
                    ruleset.GameControl.randomizeNormalized()
                else:
                    if random.random() < 0.3: ruleset.GameControl.randomizeNormalized()
                seedstep = SEED_REF

        # Control:
        dose_control = keys[pygame.K_UP] - keys[pygame.K_DOWN]
        previous_bioweights = controllable_bioweights[:]
        controllable_bioweights[pointer] = utility.clamp(controllable_bioweights[pointer] + dose_control, 0, 255)

        mx, my = pygame.mouse.get_pos()
        if mx < settings.VCELLS * settings.TILESIZE and my < settings.VCELLS * settings.TILESIZE:
            ix, iy = int(mx / settings.TILESIZE), int(my / settings.TILESIZE)
            for i in range(-2, 2):
                for j in range(-2, 2):
                    if utility.inRange(ix+j, 0, settings.VCELLS) and utility.inRange(iy+i, 0, settings.VCELLS): 
                        matrix[iy+i][ix+j].bio_weights = controllable_bioweights
                        
        for row in matrix:
            for cell in row: cell.cap_bioweight()

        # RENDERING
        draw_dest.fill(settings.PREDEF_COLS.BLACK)

        # Yah or nah indicator
        if dose_control != 0:
            col = settings.PREDEF_COLS.RED
            if utility.arrDiff(previous_bioweights, ruleset.GameControl.normalizedTargetSeed) > utility.arrDiff(controllable_bioweights, ruleset.GameControl.normalizedTargetSeed):
                col = settings.PREDEF_COLS.GREEN
            pygame.draw.rect(draw_dest, col, ((settings.VCELLS + 4) * settings.TILESIZE, 7 * settings.TILESIZE, settings.TILESIZE * 3, settings.TILESIZE * 3))
            pygame.draw.rect(draw_dest, settings.PREDEF_COLS.WHITE, ((settings.VCELLS + 4) * settings.TILESIZE, 7 * settings.TILESIZE, settings.TILESIZE * 3, settings.TILESIZE * 3), width=2)


        pygame.draw.rect(draw_dest, settings.PREDEF_COLS.RED, (0, 0, settings.VCELLS * settings.TILESIZE, settings.VCELLS * settings.TILESIZE), width=1)
        for i in range(mh):
            for j in range(mw):
                if matrix[i][j].life_state: 
                    pygame.draw.rect(draw_dest, matrix[i][j].bio_weights, (j * settings.TILESIZE, i * settings.TILESIZE, settings.TILESIZE, settings.TILESIZE))
                    pygame.draw.rect(draw_dest, settings.PREDEF_COLS.GREY, (j * settings.TILESIZE, i * settings.TILESIZE, settings.TILESIZE, settings.TILESIZE), width=1)


        # DRAWING BIOWEIGHTS
        indicator_string = " - ".join([str(controllable_bioweights[i]) + ("<" if i == pointer else "") for i in range(len(controllable_bioweights))])
        bioweight_text = debug_font.render(f"BIOWEIGHTS: {indicator_string} \n{ruleset.GameControl.extent}", False, settings.PREDEF_COLS.RED)
        bioweight_rect = bioweight_text.get_rect(topleft=((settings.VCELLS + 2) * settings.TILESIZE, 2 * settings.TILESIZE))
        draw_dest.blit(bioweight_text, bioweight_rect)
        
        # UI
        screen.blit(pygame.transform.scale(draw_dest, (screen.get_width(), screen.get_height())), (0, 0))

        pygame.display.flip()
        clock.tick(settings.GAME_FPS)

if __name__ == "__main__":
    game()