# @description: MAIN

# @section: IMPORTS
import pygame
import settings
import cell
import ruleset
import random
import utility
import sounds
import patient

# @section: SETUP
pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.RESIZABLE|pygame.DOUBLEBUF|pygame.HWSURFACE|pygame.SCALED|pygame.FULLSCREEN, vsync=1)
draw_dest = screen.copy()
debug_font = pygame.sysfont.SysFont("Arial", 15, False)
clock = pygame.Clock()

matrix:list[list[cell.Cell]] = [[cell.Cell(j, i) for j in range(settings.VCELLS)] for i in range(settings.VCELLS)]

# @section: RANDOMIZE LIFE
def randomizeLife(matrix: list[list[cell.Cell]]):
    mw, mh = len(matrix[0]), len(matrix)
    for i in range(mh):
        for j in range(mw):
            matrix[i][j].life_state = True if random.random() < 0.5 else False
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

    # ANNOUNCE WHAT THE PLAYER DOES
    sounds.AllSounds.announce0.play()
    
    poison_rects = [pygame.Rect((settings.VCELLS + 4 + i * 8) * settings.TILESIZE, 8 * settings.TILESIZE, settings.TILESIZE * 4, 128) for i in range(3)]
    poison_colors = [settings.PREDEF_COLS.RED, settings.PREDEF_COLS.GREEN, settings.PREDEF_COLS.BLUE]
    strength_rect = pygame.Rect((settings.VCELLS + 4) * settings.TILESIZE, 160 + 8 * settings.TILESIZE, 20 * settings.TILESIZE, settings.TILESIZE * 4)
    health_rect = pygame.Rect((settings.VCELLS + 4) * settings.TILESIZE, 3 * settings.TILESIZE, 20 * settings.TILESIZE, settings.TILESIZE * 4)

    ruleset.GameControl.randomizeNormalized(playSound=False)
    controllable_bioweights : list[utility.numericType] = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
    randomizeLife(matrix)
    running = True

    SEED_REF = 5 * 60
    seedstep = SEED_REF

    timestep = ruleset.GameControl.timeStep
    
    mw, mh = len(matrix[0]), len(matrix)

    while running:
        # NECESSARY EVENT LOOP - PREVENT APP FREEZE-UPs
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.QUIT:
                running = False

        # LOGIC
        if timestep > 0:
            timestep -= 1
        else:
            # Play ruleset
            ruleset.ruleset(matrix)
            # Set next timestep according to how well along you are going
            timestep = ruleset.GameControl.timeStep / ((ruleset.GameControl.extent + 0.01) ** 0.75)
            seedstep -= 1
            if not seedstep: 
                if ruleset.GameControl.extent > 0.6: 
                    ruleset.GameControl.randomizeNormalized()
                else:
                    if random.random() < 0.3: ruleset.GameControl.randomizeNormalized()

            # Play some noise
            sounds.AllSounds.gennoise.play()

        # Heal the patient
        patient.Subject.heal(-ruleset.GameControl.extent + 0.5 if ruleset.GameControl.extent >= 0.7 else 0.01)

        # Control:
        mx, my = pygame.mouse.get_pos()
        if mx < settings.VCELLS * settings.TILESIZE and my < settings.VCELLS * settings.TILESIZE:
            ix, iy = int(mx / settings.TILESIZE), int(my / settings.TILESIZE)
            for i in range(-2, 2):
                for j in range(-2, 2):
                    if utility.inRange(ix+j, 0, settings.VCELLS) and utility.inRange(iy+i, 0, settings.VCELLS): 
                        matrix[iy+i][ix+j].bio_weights = controllable_bioweights

        # Controls on poison makers
        if pygame.mouse.get_pressed()[0]:
            for index, rect in enumerate(poison_rects):
                if rect.collidepoint(mx, my):
                    ratio = (rect.y + rect.h - my) / rect.h
                    controllable_bioweights[index] = ratio * 255

        # Limit the range of the words
        for row in matrix:
            for cell in row: cell.cap_bioweight()

        # RENDERING
        draw_dest.fill(settings.PREDEF_COLS.BLACK)
        screen.fill(settings.PREDEF_COLS.BLACK)

        # DRAWING POISON MIXER INDICATOR
        for index, rect in enumerate(poison_rects):
            pygame.draw.rect(draw_dest, poison_colors[index], (
                poison_rects[index].x,
                poison_rects[index].y + poison_rects[index].h * (1 - controllable_bioweights[index] / 255), 
                poison_rects[index].w, poison_rects[index].h * (controllable_bioweights[index] / 255)
            ))
            pygame.draw.rect(draw_dest, settings.PREDEF_COLS.WHITE, poison_rects[index], width=4)

        # Extent indicator
        pygame.draw.rect(draw_dest, (255 * (1 - ruleset.GameControl.extent), 255 * ruleset.GameControl.extent, 0), (
            strength_rect.x, strength_rect.y,
            strength_rect.w * ruleset.GameControl.extent, strength_rect.h
        ))
        pygame.draw.rect(draw_dest, settings.PREDEF_COLS.WHITE, strength_rect, width=4)
        pygame.draw.line(draw_dest, settings.PREDEF_COLS.RED, (strength_rect.x + strength_rect.w * 0.7, strength_rect.y + 4), 
                         (strength_rect.x + strength_rect.w * 0.7, strength_rect.y + strength_rect.h - 4), width=4)

        # Health indicator
        pygame.draw.rect(draw_dest, settings.PREDEF_COLS.GREEN, (
                health_rect.x, health_rect.y,
                health_rect.w * patient.Subject.health / 100, health_rect.h
            ))
        pygame.draw.rect(draw_dest, settings.PREDEF_COLS.WHITE, health_rect, width=4)

        # Drawing the automata map itself
        for i in range(mh):
            for j in range(mw):
                if matrix[i][j].life_state: 
                    pygame.draw.rect(draw_dest, matrix[i][j].bio_weights, (j * settings.TILESIZE, i * settings.TILESIZE, settings.TILESIZE, settings.TILESIZE))
                    pygame.draw.rect(draw_dest, settings.PREDEF_COLS.GREY, (j * settings.TILESIZE, i * settings.TILESIZE, settings.TILESIZE, settings.TILESIZE), width=1)
        
        # Border
        pygame.draw.rect(draw_dest, settings.PREDEF_COLS.GRAY, (0, 0, settings.VCELLS * settings.TILESIZE, settings.VCELLS * settings.TILESIZE), width=1)
        
        # UI
        screen.blit(pygame.transform.scale(draw_dest, (screen.get_width(), screen.get_height())), (0, 0))

        pygame.display.flip()
        clock.tick(settings.GAME_FPS)

if __name__ == "__main__":
    game()