import pygame


class Projectile:
    def __init__(
        self,
        position,
        direction,
        speed,
        damage,
        owner,
        radius
    ):
        self.position = pygame.Vector2(position)
        self.direction = pygame.Vector2(direction).normalize()

        self.speed = speed
        self.damage = damage
        self.owner = owner
        self.radius = radius

    def update(self, dt):
        self.position += self.direction * self.speed * dt

    def is_out_of_bounds(self, width, height):
        return (
            self.position.x < -self.radius
            or self.position.x > width + self.radius
            or self.position.y < -self.radius
            or self.position.y > height + self.radius
        )