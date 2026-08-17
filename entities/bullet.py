import pygame


class Bullet:
    def __init__(self, position, direction, speed, radius, color):
        self.position = pygame.Vector2(position)
        self.velocity = direction.normalize() * speed
        self.radius = radius
        self.color = color
    def update(self, dt):
        self.position += self.velocity * dt
    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            self.position,
            self.radius
        )