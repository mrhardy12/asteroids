import pygame
from constants import *


class Score(pygame.sprite.Sprite):
    def __init__(self, font):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()
        self.score = 0
        self.font = font

    def gain_score(self, input):
        if input.radius >= 60:
            self.score += BASE_SCORE
        elif input.radius >= 40:
            self.score += BASE_SCORE * 4
        elif input.radius >= 20:
            self.score += BASE_SCORE * 9
        else:
            raise Exception("Unexpected error: invalid asteroid radius")
    
    def draw(self, screen):
        score_text = self.font.render(str(self.score), True, "white")
        score_rect = score_text.get_rect(topleft = (10, 10))

        score_overlay = pygame.Surface((score_text.get_width() + 10,
                                        score_text.get_height() + 10))
        score_overlay.set_alpha(128)
        score_overlay.fill("black")
        score_overlay_rect = score_overlay.get_rect(topleft = (5, 5))

        screen.blit(score_overlay, score_overlay_rect)
        screen.blit(score_text, score_rect)
