# @description: GAMEDEFES

# @section: SCREENDEF
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 360

# @section: GAMEDEF
TILESIZE = 8
HCELLS = int(SCREEN_WIDTH / TILESIZE)
VCELLS = int(SCREEN_HEIGHT / TILESIZE)

# @section: TIMEDEF
SECONDS = 60
GAME_FPS = 60

# @section: COLORDEF
class PREDEF_COLS:
    RED     = (255, 0, 0)
    GREEN   = (0, 255, 0)
    BLUE    = (0, 0, 255)
    WHITE   = (255, 255, 255)
    BLACK   = (0, 0, 0)
    GRAY    = (128, 128, 128)
    GREY    = (128, 128, 128) # in case any british people ever come across here