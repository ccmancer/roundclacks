import pygame


class Bullet:
    def __init__(self, position, direction, speed, radius, color, owner, damage):
        self.position = pygame.Vector2(position)
        self.velocity = direction.normalize() * speed
        self.radius = radius
        self.color = color
        self.owner = owner
        self.damage = damage
    def update(self, dt):
        self.position += self.velocity * dt
    def is_out_of_bounds(self, width, height):
        return (
            self.position.x < 0
            or self.position.x > width
            or self.position.y < 0
            or self.position.y > height
        )
    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            self.position,
            self.radius
        )