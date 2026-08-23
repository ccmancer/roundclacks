import pygame

from entities.projectile import Projectile


class EarthlightRay(Projectile):
    def __init__(
        self,
        position,
        direction,
        damage,
        owner,
        speed=900,
        radius=5,
        lifetime=0.75
    ):
        super().__init__(
            position,
            direction,
            speed,
            damage,
            owner,
            radius
        )

        self.lifetime = lifetime

        # Prevent the ray from hitting the player
        # on the exact frame it is created.
        self.ignore_collision = True

    def update(self, dt):
        self.position += (
            self.direction
            * self.speed
            * dt
        )

        self.lifetime -= dt

        # Only ignore collision for one update.
        self.ignore_collision = False

        if self.lifetime <= 0:
            self.alive = False

    def draw(self, screen):
        length = 80

        start = self.position

        end = (
            start
            + self.direction * length
        )

        pygame.draw.line(
            screen,
            "cyan",
            start,
            end,
            6
        )

    def hit(self, player):
        player.take_damage(
            self.damage
        )

        self.alive = False

        return []