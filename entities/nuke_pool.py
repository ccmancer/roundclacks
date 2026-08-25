import pygame
from pathlib import Path


SPRITE_FOLDER = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "sprites"
    / "game"
)


class NukePool:
    def __init__(
        self,
        position,
        radius,
        damage,
        owner,
        duration=3.0,
        tick_interval=0.02
    ):
        self.position = pygame.Vector2(
            position
        )

        # Gameplay hitbox.
        self.radius = radius

        self.damage = damage
        self.owner = owner

        self.duration = duration
        self.timer = duration

        self.tick_interval = tick_interval
        self.damage_timers = {}

        self.alive = True
        self.can_hit_owner = True

        self.sprite = pygame.image.load(
            SPRITE_FOLDER / "nuke_pool.png"
        ).convert_alpha()

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(self, dt):
        self.timer -= dt

        if self.timer <= 0:
            self.alive = False
            return

        for player in list(
            self.damage_timers
        ):
            self.damage_timers[player] -= dt

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------

    def draw(self, screen):
        size = max(
            1,
            int(self.radius * 2)
        )

        sprite = pygame.transform.scale(
            self.sprite,
            (
                size,
                size
            )
        )

        sprite = sprite.copy()

        fade = max(
            0,
            min(
                1,
                self.timer / self.duration
            )
        )

        sprite.set_alpha(
            int(255 * fade)
        )

        rect = sprite.get_rect(
            center=self.position
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
        if player not in self.damage_timers:
            player.take_damage(
                self.damage
            )

            self.damage_timers[player] = (
                self.tick_interval
            )

            return

        if self.damage_timers[player] <= 0:
            player.take_damage(
                self.damage
            )

            self.damage_timers[player] = (
                self.tick_interval
            )