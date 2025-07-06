import pygame
import random
from circleshape import CircleShape
from constants import *


class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)

    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, self.radius, 2)

    def update(self, dt):
        self.position += self.velocity * dt
    
    def split(self, hard_mode = False, field_count = 1):
        def spawn_pair(random_angle):
            positive_rotation = self.velocity.rotate(random_angle)
            negative_rotation = self.velocity.rotate(-random_angle)
            new_radius = self.radius - ASTEROID_MIN_RADIUS
            new_asteroid_1 = Asteroid(self.position.x, self.position.y, new_radius)
            new_asteroid_1.velocity = positive_rotation * 1.2
            new_asteroid_2 = Asteroid(self.position.x, self.position.y, new_radius)
            new_asteroid_2.velocity = negative_rotation * 1.2

        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return

        if hard_mode:
            for i in range(field_count):
                random_angle = random.uniform(20, 200)
                spawn_pair(random_angle)
        else:
            random_angle = random.uniform(20, 50)
            spawn_pair(random_angle)
