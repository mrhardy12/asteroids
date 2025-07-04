# To access virtual environment, use:
# source .venv/bin/activate

import sys
import pygame
from constants import *
from player import Player
from shot import Shot
from score import Score
from states import (
    countdown_state,
    paused_state,
    standard_state,
    base_state,
    clear_objects,
    dead_state,
    # game_over_state
)
from asteroid import Asteroid
from asteroidfield import AsteroidField


def main():
    # Initializes pygame and fonts
    pygame.init()
    pygame.font.init()
    font = pygame.font.Font(None, 74)
    score_font = pygame.font.SysFont("monospace", 52)
    small_font = pygame.font.Font(None, 36)
    dead_font = pygame.font.Font(None, 128)

    # Creates clock and change in time
    clock = pygame.time.Clock()
    dt = 0

    # Sets base variables for game logic
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    icon_index = 0
    respawn_timer = 3.5
    start_time = 0.1
    countdown_timer = 0
    state = "Init"

    # Sets base groups for game objects
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    score_draw = pygame.sprite.Group()


    # Actual game loop
    while True:
        # while True: is the standard convention for "infinite while loop."
        # The following for-loop will return None upon performing an action
        # which ends the program when the action is performed.
        # In this case, the actions are "click the quit button on pygame's UI"
        # and "press the Escape key on the keyboard."
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state in ("Standard", "Countdown"):
                        state = "Paused"
                        countdown_timer = 3.0 + dt
                    elif state == "Paused":
                        state = "Countdown"
                elif event.key == pygame.K_q and state == "Paused":
                    return

        if state == "Init":
            clear_objects(drawable, updatable, asteroids, shots)
            score_draw.empty()
            Player.containers = (updatable, drawable)
            Shot.containers = (updatable, drawable, shots)
            Score.containers = (score_draw)
            Asteroid.containers = (asteroids, updatable, drawable)
            AsteroidField.containers = (updatable)
            score = Score(score_font)
            lives = 3
            state = "Base"

        if state == "Base":
            player, asteroid_field = base_state(
                drawable,
                updatable,
                asteroids,
                shots,
                lives
            )
            start_time = max(start_time - dt, 0)
            if start_time <= 0:
                state = "Standard"

        if state == "Countdown":
            # Create countdown protocol
            if countdown_timer <= 0:
                state = "Standard"
            countdown_timer -= dt
            countdown_state(
                screen,
                drawable,
                score_draw,
                font,
                player,
                countdown_timer,
                lives_icon_points
            )

        # If paused but not unpausing
        elif state == "Paused":
            paused_state(screen, font, small_font)

        elif state == "Dead":
            dead_state(
                screen,
                dead_font,
                score_draw,
                player,
                drawable,
                updatable,
                asteroids,
                shots,
                respawn_timer,
                lives_icon_points
            )
            respawn_timer = max(respawn_timer - dt, 0)
            if respawn_timer <= 0:
                state = "Base"

        # If nothing is wrong
        elif state == "Standard":
            standard_state(
                screen,
                drawable,
                score_draw,
                player,
                lives_icon_points,
                updatable,
                dt
            )

            for asteroid in asteroids:
                # Life logic if player collides with asteroid
                if asteroid.collision(player):
                    if player.lives > 1 and player.invuln_timer <= 0:
                        state = "Dead"
                        player.invuln_timer = 0.5
                        lives -= 1
                        respawn_timer = 3.5
                    elif player.lives == 1 and player.invuln_timer <= 0:
                        print("Game over!")
                        sys.exit()

                # Destroy asteroids when shot
                for shot in shots:
                    if asteroid.collision(shot):
                        shot.kill()
                        asteroid.split()
                        score.gain_score(asteroid)
                        
        pygame.display.flip()
        
        # 60 FPS cap
        dt = clock.tick(60) / 1000


def lives_icon_points(position, rotation, radius):
    location = pygame.Vector2(position)
    forward = pygame.Vector2(0, 1).rotate(rotation)
    right = pygame.Vector2(0, 1).rotate(rotation + 90) * radius / 1.5
    a = location + forward * radius
    b = location - forward * radius - right
    c = location - forward * radius + right
    return [a, b, c]


# Runs the program; standard convention in Python is the following command.
if __name__ == "__main__":
    main()
