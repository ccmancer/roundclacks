import pygame
import math

from entities.projectile import Projectile


class MagicSlash(Projectile):
    def __init__(
        self,
        position,
        direction,
        damage,
        owner
    ):
        super().__init__(
            position,
            direction,
            1000,
            damage,
            owner,
            16,                 # hitbox radius fallback
            "magic_slash.png"
        )

        # -------------------------------------------------
        # Hitbox
        # -------------------------------------------------

        self.length = 140
        self.width = 32

        # Used by collision.py to give this a directional
        # hitbox instead of treating it like a normal circle.
        self.is_magic_slash = True

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(self, dt):
        super().update(dt)

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------

    def draw(self, screen):
        sprite = self.get_sprite()

        rect = sprite.get_rect(
            center=self.position
        )

        screen.blit(
            sprite,
            rect
        )

    # -------------------------------------------------
    # SPRITE
    # -------------------------------------------------

    def get_sprite_length(self):
        return 140

    def get_sprite_width(self):
        return 140

    def get_sprite(self):
        sprite = pygame.transform.scale(
            self.sprite,
            (
                int(self.get_sprite_length()),
                int(self.get_sprite_width())
            )
        )

        # Same orientation convention as Sword:
        # sprite faces right when direction is (1, 0).
        angle = math.degrees(
            math.atan2(
                self.direction.y,
                self.direction.x
            )
        )

        return pygame.transform.rotate(
            sprite,
            -angle
        )

    # -------------------------------------------------
    # HITBOX
    # -------------------------------------------------

    def get_hitbox_radius(self):
        return self.width / 2

    def get_hitbox_length(self):
        return self.length

    def get_hitbox_width(self):
        return self.width