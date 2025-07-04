import pygame
from constants import *
from player import Player
from asteroidfield import AsteroidField


def draw_everything(
        screen,
        player,
        drawable,
        score_draw,
        lives_icon_points,
        color = None
    ):
    for object in drawable:
        if isinstance(object, Player) and color is not None:
            continue
        object.draw(screen)
    for object in score_draw:
        object.draw(screen)
    for icon_index in range(player.lives - 1):
        icon_x = LIFE_ICON_START + icon_index * LIFE_ICON_SPACING
        points = lives_icon_points((icon_x, 85), 180, 20)
        pygame.draw.polygon(screen, "white", points, 2)


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
        player,
        countdown_timer,
        lives_icon_points
    ):
    # Countdown screen
    screen.fill("#3E0455")
    draw_everything(screen, player, drawable, score_draw, lives_icon_points)
    
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
        player,
        lives_icon_points,
        updatable,
        dt
    ):
    # Sets the screen to black, draws the objects, and updates what can be.
    screen.fill("black")
    draw_everything(screen, player, drawable, score_draw, lives_icon_points)
    player.invuln_timer = max(player.invuln_timer - dt, 0)
    updatable.update(dt)


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
        lives_icon_points
    ):
    screen.fill("black")
    color = "red"
    draw_everything(screen, player, drawable, score_draw,
                    lives_icon_points, color)
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


def base_state(drawable, updatable, asteroids, shots, lives):
    clear_objects(drawable, updatable, asteroids, shots)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, lives)
    asteroid_field = AsteroidField()
    return player, asteroid_field
