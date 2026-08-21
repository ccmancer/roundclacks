import pygame

from entities.projectile import Projectile


class Arrow(Projectile):
    def __init__(self, position, direction, damage, owner, speed):
        super().__init__(
            position,
            direction,
            speed,
            damage,
            owner,
            6
        )

    def draw(self, screen):
        end = (
            self.position
            + self.direction * 25
        )

        pygame.draw.line(
            screen,
            "brown",
            self.position,
            end,
            5
        )