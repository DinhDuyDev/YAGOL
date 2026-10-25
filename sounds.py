import pygame.mixer

pygame.mixer.init()

class AllSounds:
    announce0 = pygame.mixer.Sound("./sounds/announce0.ogg")
    announce1 = pygame.mixer.Sound("./sounds/announce1.ogg")
    announce2 = pygame.mixer.Sound("./sounds/announce2.ogg")
    announcenew = pygame.mixer.Sound("./sounds/announcenew.ogg")
    gennoise = pygame.mixer.Sound("./sounds/gennoise.ogg")

AllSounds.announce0.set_volume(0.2)
AllSounds.announcenew.set_volume(0.2)
AllSounds.gennoise.set_volume(0.2)