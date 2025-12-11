import pygame
pygame.init()
WIN_SIZE = (1920, 1080)
is_fullscreen = False
screen = pygame.display.set_mode(WIN_SIZE)

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
            is_fullscreen = not is_fullscreen
            if is_fullscreen:
                info = pygame.display.Info()
                screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
            else:
                screen = pygame.display.set_mode(WIN_SIZE)
    # draw/update here
    pygame.display.flip()