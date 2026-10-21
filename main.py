##### DEMO FOR TEXTURE MAPPING
import pygame
import settings

pygame.init()
pygame.font.init()

# setup
screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.RESIZABLE|pygame.DOUBLEBUF|pygame.SRCALPHA|pygame.SCALED|pygame.FULLSCREEN, vsync=1)
draw_dest = screen.copy()
debug_font = pygame.sysfont.SysFont("Arial", 10, False)

clock = pygame.Clock()
GAME_FPS = 60

# game
def game():
    running = True
    while running:
        # Game loop
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.QUIT:
                running = False

        # UI
        pygame.draw.circle(draw_dest, (255, 0, 0), (settings.SCREEN_WIDTH/2, settings.SCREEN_HEIGHT/2), radius=5, width=1)


        screen.blit(pygame.transform.scale(draw_dest, (screen.get_width(), screen.get_height())), (0, 0))

        pygame.display.flip()
        clock.tick(GAME_FPS)

if __name__ == "__main__":
    game()