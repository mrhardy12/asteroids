import pygame
from constants import *
from player import Player
from asteroidfield import AsteroidField


def draw_everything(
    screen,
    lives,
    drawable,
    score_draw,
    lives_icon_points,
    color = None
):
    for object in drawable:
        if isinstance(object, Player) and color is not None:
            continue
        object.draw(screen)
    draw_score(screen, score_draw)
    for icon_index in range(lives - 1):
        icon_x = LIFE_ICON_START + icon_index * LIFE_ICON_SPACING
        points = lives_icon_points((icon_x, 85), 180, 20)
        pygame.draw.polygon(screen, "white", points, 2)


def draw_score(screen, score_draw):
    for object in score_draw:
        object.draw(screen)


def clear_objects(drawable, updatable, asteroids, shots):
    updatable.empty()
    drawable.empty()
    asteroids.empty()
    shots.empty()


def countdown_state(
    screen,
    drawable,
    score_draw,
    font,
    lives,
    countdown_timer,
    lives_icon_points
):
    # Countdown screen
    screen.fill("#3E0455")
    draw_everything(screen, lives, drawable, score_draw, lives_icon_points)
    
    # Actual countdown rendering
    countdown_text = font.render(f"{int(countdown_timer) + 1}", True, "white")
    countdown_rect = countdown_text.get_rect(
        center = (
            screen.get_width() // 2,
            screen.get_height() // 2
        )
    )

    # Semi-transparent overlay for timer visibility
    count_overlay = pygame.Surface((200, 100))
    count_overlay.set_alpha(128)
    count_overlay.fill("black")
    count_overlay_rect = count_overlay.get_rect(
        center = (
            screen.get_width() // 2,
            screen.get_height() // 2
        )
    )

    # Display countdown timer on-screen
    screen.blit(count_overlay, count_overlay_rect)
    screen.blit(countdown_text, countdown_rect)


def paused_state(screen, font, small_font):
    # Pause screen definitions
    screen.fill("black")
    pause_text = font.render("PAUSED", True, "white")
    instructions_text = small_font.render(
        "Press Q to quit or Escape to continue",
        True,
        "white"
    )

    # Defining pause screen area
    pause_rect = pause_text.get_rect(
        center = (
            screen.get_width() // 2,
            screen.get_height() // 2 - 30
        )
    )
    instructions_rect = instructions_text.get_rect(
        center = (
            screen.get_width() // 2,
            screen.get_height() // 2 + 30
        )
    )

    # Render pause screen
    screen.blit(pause_text, pause_rect)
    screen.blit(instructions_text, instructions_rect)


def standard_state(
        screen,
        drawable,
        score_draw,
        lives,
        lives_icon_points,
        updatable,
        dt,
        player
):
    # Sets the screen to black, draws the objects, and updates what can be.
    screen.fill("black")
    draw_everything(screen, lives, drawable, score_draw, lives_icon_points)
    updatable.update(dt)

    if player.position.x < 0:
        player.position.x = SCREEN_WIDTH
        player.invuln_timer = 0.2
    if player.position.x > SCREEN_WIDTH:
        player.position.x = 0
        player.invuln_timer = 0.2
    if player.position.y < 0:
        player.position.y = SCREEN_HEIGHT
        player.invuln_timer = 0.2
    if player.position.y > SCREEN_HEIGHT:
        player.position.y = 0
        player.invuln_timer = 0.2
    
    for object in drawable:
        if (object.position.x < -80 or
            object.position.x > SCREEN_WIDTH + 80 or
            object.position.y < -80 or
            object.position.y > SCREEN_HEIGHT + 80
        ):
            object.kill()


def dead_state(
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
):
    screen.fill("black")
    color = "red"
    draw_everything(
        screen,
        lives,
        drawable,
        score_draw,
        lives_icon_points,
        color
    )
    dead_text = dead_font.render("You died!", True, "white")
    dead_rect = dead_text.get_rect(
        center = (
            screen.get_width() // 2,
            screen.get_height() // 2
        )
    )
    dead_overlay = pygame.Surface((300, 150))
    dead_overlay.set_alpha(128)
    dead_overlay.fill("black")
    dead_overlay_rect = dead_overlay.get_rect(
        center = (
            screen.get_width() // 2,
            screen.get_height() // 2
        )
    )

    screen.blit(dead_overlay, dead_overlay_rect)
    screen.blit(dead_text, dead_rect)

    # Helper function for circle-rectangle collision
    def circle_overlaps_rect(circle_pos, circle_radius, rect):
        px, py = circle_pos
        rx, ry, rw, rh = rect
        closest_x = max(rx, min(px, rx + rw))
        closest_y = max(ry, min(py, ry + rh))
        distance = ((px - closest_x) ** 2 + (py - closest_y) ** 2) ** 0.5
        return distance <= circle_radius

    if respawn_timer > 1.5:
        # Only draw halo if overlap with the dead text overlay
        halo_radius = player.radius * 1.5
        if circle_overlaps_rect(
            (player.position.x, player.position.y),
            halo_radius,
            dead_overlay_rect
        ):
            halo_color = (0, 0, 0, 128)
            halo_surface = pygame.Surface(
                (halo_radius * 2, halo_radius * 2),
                pygame.SRCALPHA
            )
            pygame.draw.circle(
                halo_surface,
                halo_color,
                (halo_radius, halo_radius),
                halo_radius
            )
            screen.blit(
                halo_surface,
                (
                    int(player.position.x - halo_radius),
                    int(player.position.y - halo_radius)
                )
            )
        player.draw(screen, "red")
    elif respawn_timer <= 1.5:
        clear_objects(drawable, updatable, asteroids, shots)


def base_state(drawable, updatable, asteroids, shots):
    clear_objects(drawable, updatable, asteroids, shots)


def game_over_state(screen, font, small_font, score_draw):
    screen.fill("black")
    draw_score(screen, score_draw)
    gaov_text = font.render("Game Over!", True, "white")
    gaov_small_text = small_font.render(
        "Better luck next time!",
        True,
        "white"
    )

    gaov_rect = gaov_text.get_rect(
        center = (
            screen.get_width() // 2,
            screen.get_height() // 2 - 30
        )
    )
    gaov_small_rect = gaov_small_text.get_rect(
        center = (
            screen.get_width() // 2,
            screen.get_height() // 2 + 30
        )
    )

    screen.blit(gaov_text, gaov_rect)
    screen.blit(gaov_small_text, gaov_small_rect)


def init_state(
    screen,
    font,
    small_font,
    high_score_font,
    drawable,
    updatable,
    asteroids,
    shots,
    score_draw,
    display_scores,
    hard_mode
):
    def get_string(input, placeholder, variable):
        if len(input) - 1 < i:
            return placeholder
        else:
            return input[i][variable]

    clear_objects(drawable, updatable, asteroids, shots)
    score_draw.empty()
    screen.fill("black")
    command_text = small_font.render(
        "New game? Press Y for yes, N for no, or H for hard mode!",
        True,
        "white"
    )
    command_rect = command_text.get_rect(
        center = (
            screen.get_width() // 2,
            screen.get_height() - 30
        )
    )
    screen.blit(command_text, command_rect)

    if not hard_mode:
        title_text = font.render("HIGH SCORES", True, "white")
        title_rect = title_text.get_rect(
            center = (
                screen.get_width() // 2,
                40
            )
        )
        screen.blit(title_text, title_rect)

        for i in range(0, 15):
            # Display ranks
            rank_text = high_score_font.render(f"{i + 1}.", True, "white")
            rank_rect = rank_text.get_rect(
                topright = (
                    screen.get_width() // 8,
                    96 + 36 * i
                )
            )
            screen.blit(rank_text, rank_rect)

            # Display names
            name_string = get_string(display_scores, "---", "name")
            name_text = high_score_font.render(name_string, True, "white")
            name_rect = name_text.get_rect(
                topleft = (
                    screen.get_width() // 3,
                    96 + 36 * i
                )
            )
            screen.blit(name_text, name_rect)

            # Display scores
            score_string = str(get_string(display_scores, "-----", "score"))
            score_text = high_score_font.render(score_string, True, "white")
            score_rect = score_text.get_rect(
                topright = (
                    screen.get_width() * 7 // 8,
                    96 + 36 * i
                )
            )
            screen.blit(score_text, score_rect)

    else:
        title_text = font.render("HIGH SCORES (HARD MODE)", True, "white")
        title_rect = title_text.get_rect(
            center = (
                screen.get_width() // 2,
                40
            )
        )
        screen.blit(title_text, title_rect)

        for i in range(0, 15):
            # Display ranks
            rank_text = high_score_font.render(f"{i + 1}.", True, "white")
            rank_rect = rank_text.get_rect(
                topright = (
                    screen.get_width() // 8,
                    96 + 36 * i
                )
            )
            screen.blit(rank_text, rank_rect)

            # Display names
            name_string = get_string(display_scores, "---", "name")
            name_text = high_score_font.render(name_string, True, "white")
            name_rect = name_text.get_rect(
                topleft = (
                    screen.get_width() // 3,
                    96 + 36 * i
                )
            )
            screen.blit(name_text, name_rect)

            # Display scores
            score_string = str(get_string(display_scores, "-----", "score"))
            score_text = high_score_font.render(score_string, True, "white")
            score_rect = score_text.get_rect(
                topright = (
                    screen.get_width() * 7 // 8,
                    96 + 36 * i
                )
            )
            screen.blit(score_text, score_rect)


def high_score_state(
        screen,
        score_draw,
        blink,
        font,
        small_font,
        hisc_name_font,
        player_name
):
    screen.fill("black")
    draw_score(screen, score_draw)
    hisc_text = font.render("NEW HIGH SCORE!", True, "white")
    hisc_small_text = small_font.render("Enter your name:", True, "white")
    hisc_name_input = hisc_name_font.render(player_name, True, "white")
    name_char_width = hisc_name_font.size("A")[0]

    hisc_rect = hisc_text.get_rect(
        center = (
            screen.get_width() // 2,
            screen.get_height() // 2 - 30
        )
    )
    hisc_small_rect = hisc_small_text.get_rect(
        center = (
            screen.get_width() // 2,
            screen.get_height() // 2 + 30
        )
    )
    hisc_name_rect = hisc_name_input.get_rect(
        topleft = (
            screen.get_width() // 2 - name_char_width * 1.5,
            screen.get_height() // 2 + 60
        )
    )

    screen.blit(hisc_text, hisc_rect)
    screen.blit(hisc_small_text, hisc_small_rect)
    screen.blit(hisc_name_input, hisc_name_rect)

    if blink == True and len(player_name) < 3:
        base_x = screen.get_width() // 2 - name_char_width * 1.5
        cursor_x = base_x + name_char_width * len(player_name)
        cursor_y = screen.get_height() // 2 + 60

        blink_pos = hisc_name_font.render("█", True, "white")
        blink_rect = blink_pos.get_rect(topleft = (cursor_x, cursor_y))
        screen.blit(blink_pos, blink_rect)


def angy_state(
    screen,
    drawable,
    score_draw,
    lives,
    lives_icon_points,
    updatable,
    dt,
    player
):
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
