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

    def gain_score(self, input, hard_mode = False, score_mult = 1):
        def score_increment(input):
            if input.radius >= 60:
                return BASE_SCORE + 10
            elif input.radius >= 40:
                return BASE_SCORE * 4 + 10
            elif input.radius >= 20:
                return BASE_SCORE * 9 + 10
            else:
                raise Exception("Unexpected error: invalid asteroid radius")
        
        if hard_mode:
            score_increase = (score_increment(input) + 100) * score_mult
        else:
            score_increase = score_increment(input)
        self.score += score_increase
    
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
