import pygame

from entities.projectile import Projectile


class BearTrap(Projectile):
    def __init__(self, position, damage, owner, duration):
        super().__init__(
            position,
            pygame.Vector2(0, 0),
            0,
            damage,
            owner,
            20
        )

        self.duration = duration
        self.triggered = False

    def update(self, dt):
        if self.triggered:
            return

        self.duration -= dt

        if self.duration <= 0:
            self.alive = False

    def hit(self, player):
        if self.triggered:
            return

        self.triggered = True

        player.take_damage(self.damage)

        self.alive = False

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            "black",
            self.position,
            self.radius,
            3
        )