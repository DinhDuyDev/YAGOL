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
import bg_cgol
import asyncio

# @section: SETUP
pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.RESIZABLE|pygame.DOUBLEBUF|pygame.HWSURFACE|pygame.SCALED|pygame.FULLSCREEN, vsync=1)
draw_dest = screen.copy()
debug_font = pygame.font.Font("./fonts/Minecraft.ttf", 15)
title_font = pygame.font.Font("./fonts/Minecraft.ttf", 45)
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

# @section: GAMEPLAY SETUP
class State:
    poison_rects = [pygame.Rect((settings.VCELLS + 2 + i * 8) * settings.TILESIZE, 6 * settings.TILESIZE, settings.TILESIZE * 4, 128) for i in range(3)]
    poison_colors = [settings.PREDEF_COLS.RED, settings.PREDEF_COLS.GREEN, settings.PREDEF_COLS.BLUE]
    strength_rect = pygame.Rect((settings.VCELLS + 2) * settings.TILESIZE, 128 + 8 * settings.TILESIZE, 20 * settings.TILESIZE, settings.TILESIZE * 4)
    health_rect = pygame.Rect((settings.VCELLS + 2) * settings.TILESIZE, 1 * settings.TILESIZE, 20 * settings.TILESIZE, settings.TILESIZE * 4)

    ruleset.GameControl.initStable()
    controllable_bioweights : list[utility.numericType] = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
    randomizeLife(matrix)
    mw, mh = len(matrix[0]), len(matrix)
    SEED_REF = 30
    seedstep = SEED_REF
    timestep = ruleset.GameControl.timeStep
    state_counter = 0
    titleBop = True
    timer = 0
    hasWon = 0 # 0 - in progress, 1 - won, 2 - lose
    playNoise = True


# Title screen
def title():
    if State.timer > 30:
        State.timer = 0
        State.titleBop = not State.titleBop
        bg_cgol.BGCGol.next()

    State.timer += 1

    # drawing the background CGOL
    for i in range(settings.VCELLS):
        for j in range(settings.HCELLS):
            if bg_cgol.BGCGol.matrix[i][j].life_state:
                pygame.draw.rect(draw_dest, settings.PREDEF_COLS.DRKGR, (j * settings.TILESIZE, i * settings.TILESIZE, settings.TILESIZE, settings.TILESIZE))

    # SCUFFED VON SCUFFED
    title_text = title_font.render("YAGOL", False, settings.PREDEF_COLS.WHITE)
    for border in [(-1, 0), (0, -1), (0, 1), (1, 0), (0, 0)]:
        if border == (0,0): title_text = title_font.render("YAGOL", False, settings.PREDEF_COLS.RED)
        title_rect = title_text.get_rect(center=(settings.SCREEN_WIDTH/2 + border[0] * 4, settings.SCREEN_HEIGHT/4 + border[1] * 4 + State.titleBop * 16))
        draw_dest.blit(title_text, title_rect)

    # SCUFFED VON SCUFFED
    start_button = title_font.render("START GAME", False, settings.PREDEF_COLS.WHITE)
    for border in [(-1, 0), (0, -1), (0, 1), (1, 0), (0, 0)]:
        if border == (0, 0): start_button = title_font.render("START GAME", False, settings.PREDEF_COLS.RED)
        button_rect  = start_button.get_rect(center=(settings.SCREEN_WIDTH/2 + border[0] * 4, settings.SCREEN_HEIGHT/2 + border[1] * 4))
        draw_dest.blit(start_button, button_rect)

    if button_rect.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(draw_dest, settings.PREDEF_COLS.RED, (
            button_rect.x - 8, button_rect.y - 12, button_rect.w + 16, button_rect.h + 8
            ), width=4)
        if pygame.mouse.get_pressed()[0]:
            State.state_counter = 1

def resetGame():
    ruleset.GameControl.initStable()
    patient.Subject.health = 20
    State.controllable_bioweights = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
    randomizeLife(matrix)
    State.playNoise = True

# Gameplay logic
def loop():
    keys = pygame.key.get_pressed()
    # still going
    mx, my = pygame.mouse.get_pos()

    # Check for patient state 
    if patient.Subject.health >= 100:
        patient.Subject.health = 100
        State.hasWon = 2
        if State.playNoise: 
            State.playNoise = False
            sounds.AllSounds.announce1.play()

    elif patient.Subject.health <= 0:
        patient.Subject.health = -0.5
        State.hasWon = 1
        if State.playNoise: 
            State.playNoise = False
            sounds.AllSounds.announce2.play()

    if State.hasWon == 0:
        # LOGIC
        if State.timestep > 0:
            State.timestep -= 1
        else:
            # Play ruleset
            ruleset.ruleset(matrix)
            # Set next timestep according to how well along you are going
            State.timestep = ruleset.GameControl.timeStep / ((ruleset.GameControl.extent + 0.01) ** 0.75)
            State.seedstep -= 1
            if not State.seedstep: 
                if ruleset.GameControl.extent > ruleset.GameControl.killThreshold:
                    ruleset.GameControl.randomizeNormalized()
                else:
                    if random.random() < 0.5: 
                        print("randomize")
                        ruleset.GameControl.randomizeNormalized()
                seedstep = State.SEED_REF
            # Play some noise
            sounds.AllSounds.gennoise.play()

        # Heal the patient
        patient.Subject.heal(
            ((-ruleset.GameControl.extent + 0.45) * 0.1 if ruleset.GameControl.extent >= ruleset.GameControl.killThreshold else 0) + 0.01)

        # Control:
        if mx < settings.VCELLS * settings.TILESIZE and my < settings.VCELLS * settings.TILESIZE:
            ix, iy = int(mx / settings.TILESIZE), int(my / settings.TILESIZE)
            for i in range(-2, 2):
                for j in range(-2, 2):
                    if utility.inRange(ix+j, 0, settings.VCELLS) and utility.inRange(iy+i, 0, settings.VCELLS): 
                        matrix[iy+i][ix+j].bio_weights = State.controllable_bioweights

        # Controls on poison makers
        if pygame.mouse.get_pressed()[0]:
            for index, rect in enumerate(State.poison_rects):
                if rect.collidepoint(mx, my):
                    ratio = (rect.y + rect.h - my) / rect.h
                    State.controllable_bioweights[index] = ratio * 255

        # Limit the range of the words
        for row in matrix:
            for cell in row: cell.cap_bioweight()

    else:
        if keys[pygame.K_r]:
            State.hasWon = 0
            resetGame()

    # DRAWING POISON MIXER INDICATOR
    for index, rect in enumerate(State.poison_rects):
        pygame.draw.rect(draw_dest, State.poison_colors[index], (
            State.poison_rects[index].x,
            State.poison_rects[index].y + State.poison_rects[index].h * (1 - State.controllable_bioweights[index] / 255), 
            State.poison_rects[index].w, State.poison_rects[index].h * (State.controllable_bioweights[index] / 255)
        ))
        pygame.draw.rect(draw_dest, settings.PREDEF_COLS.WHITE, State.poison_rects[index], width=4)

    # Extent indicator
    pygame.draw.rect(draw_dest, (255 * (1 - ruleset.GameControl.extent), 255 * ruleset.GameControl.extent, 0), (
        State.strength_rect.x, State.strength_rect.y,
        State.strength_rect.w * ruleset.GameControl.extent, State.strength_rect.h
    ))

    pygame.draw.rect(draw_dest, settings.PREDEF_COLS.WHITE, State.strength_rect, width=4)
    pygame.draw.line(draw_dest, settings.PREDEF_COLS.RED, (State.strength_rect.x + State.strength_rect.w * ruleset.GameControl.killThreshold,  State.strength_rect.y + 4), 
                        (State.strength_rect.x + State.strength_rect.w * ruleset.GameControl.killThreshold, State.strength_rect.y + State.strength_rect.h - 4), width=4)

    # Health indicator
    pygame.draw.rect(draw_dest, settings.PREDEF_COLS.GREEN, (
            State.health_rect.x, State.health_rect.y,
            State.health_rect.w * patient.Subject.health / 100, State.health_rect.h
        ))
    pygame.draw.rect(draw_dest, settings.PREDEF_COLS.WHITE, State.health_rect, width=4)

    # Drawing the automata map itself
    for i in range(State.mh):
        for j in range(State.mw):
            if matrix[i][j].life_state: 
                pygame.draw.rect(draw_dest, matrix[i][j].bio_weights, (j * settings.TILESIZE, i * settings.TILESIZE, settings.TILESIZE, settings.TILESIZE))
                pygame.draw.rect(draw_dest, settings.PREDEF_COLS.GREY, (j * settings.TILESIZE, i * settings.TILESIZE, settings.TILESIZE, settings.TILESIZE), width=1)

    # Border
    pygame.draw.rect(draw_dest, settings.PREDEF_COLS.GRAY, (0, 0, settings.VCELLS * settings.TILESIZE, settings.VCELLS * settings.TILESIZE), width=1)

    text = '''
        [PLACEHOLDER]
        '''
    if State.hasWon == 0:
        text = '''
            Drag the appropriate poison
            values from the 3 bars.
            Apply it to your virus.
            Cross the threshold to 
            damage your patient!
            Don't let your patient survive!
                '''
    elif State.hasWon == 1:
        text = '''
        You killed him! Great job!
        Press [R] to start again!
            '''
    else:
        text = '''
        Your patient survived!
        Dangit...
        Press [R] to start again!
            '''
    # Instructions
    instruction_text = debug_font.render(
        text, False, settings.PREDEF_COLS.RED
    )
    instruction_rect = instruction_text.get_rect(topleft=((settings.VCELLS - 4) * settings.TILESIZE, 160 + 8 * settings.TILESIZE))
    draw_dest.blit(instruction_text, instruction_rect)

# @section: MAIN GAME LOOP

async def game():
    # Setup background of title screen

    bg_cgol.BGCGol.setup()
    running = True
    while running:
        # NECESSARY EVENT LOOP - PREVENT APP FREEZE-UPs
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.QUIT:
                running = False

        # RENDERING
        draw_dest.fill(settings.PREDEF_COLS.BLACK)
        screen.fill(settings.PREDEF_COLS.BLACK)

        if State.state_counter == 0: title()
        else: loop()
        
        # UI
        screen.blit(pygame.transform.scale(draw_dest, (screen.get_width(), screen.get_height())), (0, 0))

        pygame.display.flip()
        clock.tick(settings.GAME_FPS)
        await asyncio.sleep(0)

asyncio.run(game())