import pygame
import math

from entities.projectile import Projectile


class EarthlightRay(Projectile):
    def __init__(
        self,
        position,
        direction,
        damage,
        owner,
        speed=900,
        radius=20,
        lifetime=0.75
    ):
        super().__init__(
            position,
            direction,
            speed,
            damage,
            owner,
            radius,
            "earthlight_ray.png"
        )

        self.lifetime = lifetime

        # Ignore collision for the frame it is created.
        self.ignore_collision = True

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(self, dt):
        self.position += (
            self.direction
            * self.speed
            * dt
        )

        self.lifetime -= dt

        self.ignore_collision = False

        if self.lifetime <= 0:
            self.alive = False

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------

    def draw(self, screen):
        sprite = pygame.transform.scale(
            self.sprite,
            (
                80,
                20
            )
        )

        angle = math.degrees(
            math.atan2(
                self.direction.y,
                self.direction.x
            )
        )

        sprite = pygame.transform.rotate(
            sprite,
            -angle
        )

        rect = sprite.get_rect(
            midleft=self.position
        )

        screen.blit(
            sprite,
            rect
        )

    # -------------------------------------------------
    # HITBOX
    # -------------------------------------------------

    def get_hitbox_radius(self):
        return self.radius

    # -------------------------------------------------
    # HIT
    # -------------------------------------------------

    def hit(self, player):
        player.take_damage(
            self.damage
        )

        self.alive = False

        return []