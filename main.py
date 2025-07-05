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
    dead_state,
    game_over_state,
    init_state,
    high_score_state
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
    high_score_font = pygame.font.SysFont("monospace", 24)
    hisc_name_font = pygame.font.SysFont("monospace", 36)

    # Creates clock and change in time
    clock = pygame.time.Clock()
    dt = 0

    # Sets base variables for game logic
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    icon_index = 0
    respawn_timer = 3.5
    countdown_timer = 0.0
    state = "Init"
    high_scores = []

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
                elif event.key == pygame.K_y and state == "Init":
                    state = "Base"
                elif event.key == pygame.K_n and state == "Init":
                    return
                elif state == "High Score":
                    char = event.unicode
                    if (event.key == pygame.K_BACKSPACE and
                        len(player_name) > 0):
                        player_name = player_name[:-1]
                    elif char.isalnum() and len(player_name) < 3:
                        player_name += str(char.upper())
                    elif (event.key == pygame.K_RETURN or 
                          event.key == pygame.K_KP_ENTER):
                        state = "Init"
                    

        if state == "Init":
            init_state(
                screen,
                font,
                small_font,
                high_score_font,
                drawable,
                updatable,
                asteroids,
                shots,
                score_draw,
                high_scores
            )
            Player.containers = (updatable, drawable)
            Shot.containers = (updatable, drawable, shots)
            Score.containers = (score_draw)
            Asteroid.containers = (asteroids, updatable, drawable)
            AsteroidField.containers = (updatable)
            score = Score(score_font)
            score_threshold = 0
            lives = 3
            start_time = 0.1

        if state == "Base":
            base_state(
                drawable,
                updatable,
                asteroids,
                shots,
            )
            player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            asteroid_field = AsteroidField()
            start_time = max(start_time - dt, 0)
            if start_time <= 0:
                state = "Standard"

        if state == "Countdown":
            # Create countdown protocol
            if countdown_timer <= 0:
                state = "Standard"
            countdown_timer = max(countdown_timer - dt, 0)
            countdown_state(
                screen,
                drawable,
                score_draw,
                font,
                lives,
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
                lives_icon_points,
                lives
            )
            respawn_timer = max(respawn_timer - dt, 0)
            if respawn_timer <= 0:
                high_score = (
                    len(high_scores) < 15 or
                    score.score > min(hs["score"] for hs in high_scores)
                )
                if lives > 0:
                    state = "Base"
                elif lives <= 0:
                    if high_score:
                        player_name = ""
                        blink = True
                        blink_timer = 2.0
                        state = "High Score"
                    else:
                        game_over_timer = 5.0
                        state = "Game Over"

        elif state == "Game Over":
            game_over_state(screen, font, small_font, score_draw)
            game_over_timer = max(game_over_timer - dt, 0)
            if game_over_timer <= 0:
                state = "Init"

        elif state == "High Score":
            high_score_state(
                screen,
                score_draw,
                blink,
                font,
                small_font,
                hisc_name_font,
                player_name
            )
            blink_timer = max(blink_timer - dt, 0)
            if blink_timer <= 0:
                blink_timer = 2
            blink = blink_timer > 1

        # If nothing is wrong
        elif state == "Standard":
            standard_state(
                screen,
                drawable,
                score_draw,
                lives,
                lives_icon_points,
                updatable,
                dt,
                player
            )
            player.invuln_timer = max(player.invuln_timer - dt, 0)

            for asteroid in asteroids:
                # Life logic if player collides with asteroid
                if asteroid.collision(player):
                    if player.invuln_timer <= 0:
                        state = "Dead"
                        player.invuln_timer = 0.5
                        lives -= 1
                        respawn_timer = 3.5

                # Destroy asteroids when shot
                for shot in shots:
                    if asteroid.collision(shot):
                        shot.kill()
                        asteroid.split()

                        old_score = score.score
                        score.gain_score(asteroid)
                        score_gained = score.score - old_score
                        score_threshold += score_gained
                        if score_threshold >= 10000:
                            score_threshold -= 10000
                            lives += 1
                        
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
