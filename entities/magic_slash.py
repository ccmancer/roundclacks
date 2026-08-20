import pygame

from entities.projectile import Projectile


class MagicSlash(Projectile):
    def __init__(self, position, direction, damage, owner):
        super().__init__(
            position,
            direction,
            500,
            damage,
            owner,
            12
        )

        self.length = 40
        self.width = 12

    def draw(self, screen):
        start = self.position

        end = (
            self.position
            + self.direction * self.length
        )

        pygame.draw.line(
            screen,
            "purple",
            start,
            end,
            self.width
        )