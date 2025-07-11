# To access virtual environment, use:
# source .venv/bin/activate

import os
import sys
import json

import pygame

from shot import Shot
from score import Score
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import *
from states import (
    init_state,
    base_state,
    standard_state,
    paused_state,
    countdown_state,
    dead_state,
    game_over_state,
    high_score_state
)


def lives_icon_points(position, rotation, radius):
    location = pygame.Vector2(position)
    forward = pygame.Vector2(0, 1).rotate(rotation)
    right = pygame.Vector2(0, 1).rotate(rotation + 90) * radius / 1.5
    a = location + forward * radius
    b = location - forward * radius - right
    c = location - forward * radius + right
    return [a, b, c]


def get_score(dict):
    return dict["score"]


def main():
    pygame.init()
    pygame.font.init()
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)
    dead_font = pygame.font.Font(None, 128)
    score_font = pygame.font.SysFont("monospace", 52)
    high_score_font = pygame.font.SysFont("monospace", 24)
    hisc_name_font = pygame.font.SysFont("monospace", 36)

    # Creates high score file if it does not exist
    if not os.path.exists("highscores.json"):
        with open("highscores.json", "w") as file:
            json.dump([], file)
    if not os.path.exists("hardscores.json"):
        with open("hardscores.json", "w") as file:
            json.dump([], file)

    # Creates clock and change in time
    clock = pygame.time.Clock()
    dt = 0

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    icon_index = 0
    countdown_timer = 0.0
    high_scores = []
    hard_scores = []
    scores_timer = 10
    hard_mode = False
    state = "Init"

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    score_draw = pygame.sprite.Group()

    while True:
        # while True: is the standard convention for "infinite while loop."
        # The following for-loop will return None upon performing an action,
        # which ends the program when the action is performed.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state in ("Standard", "Countdown", "Angy"):
                        state = "Paused"
                        countdown_timer = 3.0 + dt
                    elif state == "Paused":
                        state = "Countdown"
                elif event.key == pygame.K_q and state == "Paused":
                    return
                elif ((event.key == pygame.K_y or event.key == pygame.K_h)
                       and state == "Init"):
                    state = "Base"
                    if event.key == pygame.K_h:
                        hard_mode = True
                    else:
                        hard_mode = False
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
                        padded_name = player_name.ljust(3, "-")
                        new_score = {"name": padded_name,
                                     "score": score.score}
                        if not hard_mode:
                            high_scores.append(new_score)
                            high_scores.sort(key=get_score, reverse=True)
                            high_scores = high_scores[:HIGH_SCORE_LIST_LENGTH]
                            with open("highscores.json", "w") as file:
                                json.dump(high_scores, file, indent=2)
                        else:
                            hard_scores.append(new_score)
                            hard_scores.sort(key=get_score, reverse=True)
                            hard_scores = hard_scores[:HIGH_SCORE_LIST_LENGTH]
                            with open("hardscores.json", "w") as file:
                                json.dump(hard_scores, file, indent=2)
                        state = "Init"

        # When game is started, or after a game over
        if state == "Init":
            with open("highscores.json", "r") as file:
                high_scores = json.load(file)
            with open("hardscores.json", "r") as file:
                hard_scores = json.load(file)
            if not hard_mode:
                display_scores = high_scores
            else:
                display_scores = hard_scores
            init_state(
                screen,
                drawable,
                updatable,
                score_draw,
                asteroids,
                shots,
                font,
                small_font,
                high_score_font,
                display_scores,
                hard_mode
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
            scores_timer = max(scores_timer - dt, 0)
            if scores_timer <= 0:
                scores_timer = 10
                hard_mode = False
            elif scores_timer <= 5:
                hard_mode = True

        # Spawn objects and begin game
        if state == "Base":
            base_state(
                drawable,
                updatable,
                asteroids,
                shots,
            )
            player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            asteroid_field = AsteroidField()
            field_count = 1
            angy_timer = 10
            score_mult = 1
            alive_timer = 15
            start_time = max(start_time - dt, 0)
            if hard_mode:
                life_threshold = EXTRA_LIFE_HARD
            else:
                life_threshold = EXTRA_LIFE_NORMAL
            if start_time <= 0:
                state = "Standard"

        # Normal game loop
        elif state == "Standard":
            standard_state(
                screen,
                drawable,
                updatable,
                score_draw,
                lives,
                dt,
                player,
                lives_icon_points
            )
            player.invuln_timer = max(player.invuln_timer - dt, 0)

            if hard_mode:
                alive_timer = max(alive_timer - dt, 0)
                if alive_timer <= 0:  # After 15 seconds
                    angy_timer = max(angy_timer - dt, 0)
                    if angy_timer <= 0:  # Every 10 seconds afterwards
                        asteroidfield = AsteroidField()
                        field_count += 1
                        score_mult += 1
                        angy_timer = 10

            for asteroid in asteroids:
                if asteroid.collision(player):
                    if player.invuln_timer <= 0:
                        state = "Dead"
                        player.invuln_timer = 0.5
                        lives -= 1
                        respawn_timer = RESPAWN_TIME

                for shot in shots:
                    if asteroid.collision(shot):
                        shot.kill()
                        asteroid.split(hard_mode, field_count)

                        old_score = score.score
                        score.gain_score(asteroid, hard_mode, score_mult)
                        score_gained = score.score - old_score
                        score_threshold += score_gained
                        if score_threshold >= life_threshold:
                            score_threshold -= life_threshold
                            lives += 1

        # If paused but not unpausing
        elif state == "Paused":
            paused_state(screen, font, small_font)

        # If player is unpausing, sets a 3-second countdown so that
        # the player can get their bearings
        if state == "Countdown":
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

        # If player dies
        elif state == "Dead":
            dead_state(
                screen,
                drawable,
                updatable,
                score_draw,
                asteroids,
                shots,
                dead_font,
                lives,
                respawn_timer,
                player,
                lives_icon_points
            )
            respawn_timer = max(respawn_timer - dt, 0)
            start_time = 0.1

            if respawn_timer <= 0:
                if not hard_mode:
                    current_scores = high_scores
                else:
                    current_scores = hard_scores
                high_score = (
                    len(current_scores) < HIGH_SCORE_LIST_LENGTH or
                    score.score > min(hs["score"] for hs in current_scores)
                )
                if lives > 0:
                    state = "Base"
                elif lives <= 0:
                    scores_timer = 10
                    if high_score:
                        player_name = ""
                        blink_timer = 2.0
                        state = "High Score"
                    else:
                        game_over_timer = 5.0
                        state = "Game Over"

        # If player dies with no extra lives remaining
        elif state == "Game Over":
            game_over_state(screen, score_draw, font, small_font)
            game_over_timer = max(game_over_timer - dt, 0)
            if game_over_timer <= 0:
                state = "Init"

        # If player's score is a record on game over
        elif state == "High Score":
            blink = blink_timer > 1
            high_score_state(
                screen,
                score_draw,
                font,
                small_font,
                hisc_name_font,
                blink,
                player_name
            )
            blink_timer = max(blink_timer - dt, 0)
            if blink_timer <= 0:
                blink_timer = 2.0

        pygame.display.flip()
        
        # 60 FPS cap
        dt = clock.tick(60) / 1000


# Runs the program; standard convention in Python is the following command.
if __name__ == "__main__":
    main()
