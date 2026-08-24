import pygame

from entities.projectile import Projectile


class BearTrap(Projectile):
    def __init__(
        self,
        position,
        damage,
        owner,
        duration
    ):
        super().__init__(
            position,
            pygame.Vector2(0, 0),
            0,
            damage,
            owner,
            40,
            "bear_trap.png"
        )

        self.duration = duration
        self.triggered = False

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(self, dt):
        if self.triggered:
            return

        self.duration -= dt

        if self.duration <= 0:
            self.alive = False

    # -------------------------------------------------
    # SPRITE
    # -------------------------------------------------

    def get_sprite_length(self):
        return 80

    def get_sprite_width(self):
        return 80

    # -------------------------------------------------
    # HIT
    # -------------------------------------------------

    def hit(self, player):
        if self.triggered:
            return

        self.triggered = True

        player.take_damage(
            self.damage
        )

        self.alive = False