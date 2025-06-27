# To access virtual environment, use:
# source venv/bin/activate

import pygame
from constants import *
from player import Player


def main():
    pygame.init()
    clock = pygame.time.Clock()
    dt = 0
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    updatables = pygame.sprite.Group()
    drawables = pygame.sprite.Group()
    Player.containers = (updatables, drawables)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        
        screen.fill("black")
        for player in drawables:
            player.draw(screen)
        updatables.update(dt)
        pygame.display.flip()
        
        # 60 FPS cap
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()
