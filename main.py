# To access virtual environment, use:
# source venv/bin/activate

import pygame
from constants import *
from player import Player


def main():
    # Initializes pygame and fonts
    pygame.init()
    pygame.font.init()
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)

    # Creates clock and change in time
    clock = pygame.time.Clock()
    dt = 0

    # Sets base variables for screen and groups
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()

    # Sets player groups and variable
    Player.containers = (updatable, drawable)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    # Sets initial pause values
    paused = False
    countdown_active = False
    countdown_timer = 0

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
                    if not paused:
                        paused = True
                    elif paused and not countdown_active:
                        countdown_active = True
                        countdown_timer = 3.0 + dt
                elif event.key == pygame.K_q and paused:
                    return

        if paused:
            # Setting unpause countdown
            if countdown_active:
                countdown_timer -= dt

                # Create countdown protocol
                if countdown_timer <= 0:
                    paused = False
                    countdown_active = False
                
                # Countdown screen color overlay
                screen.fill("#3E0455")
                for object in drawable:
                    object.draw(screen)

                # Render countdown
                countdown_text = font.render(f"{int(countdown_timer) + 1}", True, "white")
                text_rect = countdown_text.get_rect(
                    center = (screen.get_width() // 2,
                              screen.get_height() // 2)
                )

                # Semi-transparent overlay for visibility
                overlay = pygame.Surface((200,100))
                overlay.set_alpha(128)
                overlay.fill("black")
                overlay_rect = overlay.get_rect(
                    center = (screen.get_width() // 2,
                              screen.get_height() // 2)
                )

                # Display countdown on-screen
                screen.blit(overlay, overlay_rect)
                screen.blit(countdown_text, text_rect)

            # If paused but not unpausing
            else:
                # Pause screen definitions
                screen.fill("black")
                pause_text = font.render("PAUSED", True, "white")
                instructions_text = small_font.render(
                    "Press Q to quit or Escape to continue", True, "white")

                # Defining pause screen area
                pause_rect = pause_text.get_rect(
                    center = (screen.get_width() // 2,
                              screen.get_height() // 2 - 30)
                )
                instructions_rect = instructions_text.get_rect(
                    center = (screen.get_width() // 2,
                              screen.get_height() // 2 + 30)
                )

                # Render pause screen
                screen.blit(pause_text, pause_rect)
                screen.blit(instructions_text, instructions_rect)

        # If not paused
        else:
            # Sets the screen to black, draws the objects, and updates what can be.
            screen.fill("black")
            for object in drawable:
                object.draw(screen)
            updatable.update(dt)

        pygame.display.flip()
        
        # 60 FPS cap
        dt = clock.tick(60) / 1000


# Runs the program; standard convention in Python is the following command.
if __name__ == "__main__":
    main()
