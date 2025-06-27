# To access virtual environment, use:
# source venv/bin/activate

import pygame
from constants import *
from player import Player


def main():
    # initialize pygame
    pygame.init()

    # create clock and change in time
    clock = pygame.time.Clock()
    dt = 0

    # set base variables; screen, player, and groups
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    updatables = pygame.sprite.Group()
    drawables = pygame.sprite.Group()
    Player.containers = (updatables, drawables)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    # actual game loop
    while True:
        # while True: is standard convention for "infinite while loop"
        # the following for loop will return None upon performing an action
        # which ends the program when the action is performed.
        # In this case, the action is "click the quit button on pygame's UI"
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        
        # sets the screen to black and draws the objects
        screen.fill("black")
        for player in drawables:
            player.draw(screen)
        updatables.update(dt)
        pygame.display.flip()
        
        # 60 FPS cap
        dt = clock.tick(60) / 1000


# runs the program; standard convention is the following command
if __name__ == "__main__":
    main()
