import pygame.mixer

pygame.mixer.init()

class AllSounds:
    announce0 = pygame.mixer.Sound("./sounds/announce0.wav")
    announce1 = pygame.mixer.Sound("./sounds/announce1.wav")
    announce2 = pygame.mixer.Sound("./sounds/announce2.wav")
    announcenew = pygame.mixer.Sound("./sounds/announcenew.wav")
    gennoise = pygame.mixer.Sound("./sounds/gennoise.wav")

AllSounds.announce0.set_volume(0.2)
AllSounds.announcenew.set_volume(0.2)
AllSounds.gennoise.set_volume(0.2)