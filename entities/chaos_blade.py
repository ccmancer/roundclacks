import pygame
from pathlib import Path


SPRITE_FOLDER = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "sprites"
    / "game"
)


class ChaosBlade:
    def __init__(
        self,
        position,
        direction,
        max_distance,
        damage,
        owner,
        size,
        duration=1.5,
        rotation_speed=720,
        outward_speed=250
    ):
        self.center = pygame.Vector2(
            position
        )

        self.direction = pygame.Vector2(
            direction
        )

        if self.direction.length_squared() > 0:
            self.direction = (
                self.direction.normalize()
            )

        self.distance = 0
        self.max_distance = max_distance

        self.damage = damage
        self.owner = owner

        # -------------------------------------------------
        # Size
        # -------------------------------------------------

        # Make the blade larger while preserving its
        # proportional relationship with the explosion.
        self.size = size * 2

        # -------------------------------------------------
        # Lifetime / movement
        # -------------------------------------------------

        self.duration = duration
        self.timer = duration

        # Movement rotation.
        self.rotation_speed = rotation_speed

        self.outward_speed = outward_speed

        # -------------------------------------------------
        # Sprite rotation
        # -------------------------------------------------

        # Visual rotation is independent from movement.
        self.sprite_angle = 0

        # Quickly spins in place.
        self.sprite_rotation_speed = 720

        # -------------------------------------------------
        # State
        # -------------------------------------------------

        self.alive = True
        self.can_hit_owner = False

        self.hit_players = set()

        # -------------------------------------------------
        # Hitbox
        # -------------------------------------------------

        self.radius = max(
            5,
            self.size * 0.4
        )

        self.position = (
            self.center.copy()
        )

        # -------------------------------------------------
        # Movement phases
        # -------------------------------------------------

        self.phase = "outward"

        self.outward_time = (
            self.max_distance
            / self.outward_speed
        )

        self.pause_time = 0.5
        self.return_time = 0.35

        self.phase_timer = (
            self.outward_time
        )

        self.return_speed = (
            self.max_distance
            / self.return_time
        )

        # -------------------------------------------------
        # Sprite
        # -------------------------------------------------

        self.sprite = pygame.image.load(
            SPRITE_FOLDER / "chaos_blade.png"
        ).convert_alpha()

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(self, dt):
        if not self.alive:
            return

        self.timer -= dt

        if self.timer <= 0:
            self.alive = False
            return

        # -------------------------------------------------
        # Sprite rotation
        # -------------------------------------------------

        self.sprite_angle += (
            self.sprite_rotation_speed * dt
        )

        self.sprite_angle %= 360

        # -------------------------------------------------
        # Movement direction
        # -------------------------------------------------

        self.direction = (
            self.direction.rotate(
                self.rotation_speed * dt
            )
        )

        # -------------------------------------------------
        # Fly outward
        # -------------------------------------------------

        if self.phase == "outward":
            self.distance += (
                self.outward_speed * dt
            )

            if self.distance >= self.max_distance:
                self.distance = (
                    self.max_distance
                )

                self.phase = "pause"

                self.phase_timer = (
                    self.pause_time
                )

        # -------------------------------------------------
        # Pause
        # -------------------------------------------------

        elif self.phase == "pause":
            self.phase_timer -= dt

            if self.phase_timer <= 0:
                self.phase = "return"

        # -------------------------------------------------
        # Return inward
        # -------------------------------------------------

        elif self.phase == "return":
            self.distance -= (
                self.return_speed * dt
            )

            if self.distance <= 0:
                self.distance = 0
                self.alive = False

        self.position = (
            self.center
            + self.direction * self.distance
        )

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------

    def draw(self, screen):
        size = max(
            1,
            int(self.size)
        )

        sprite = pygame.transform.scale(
            self.sprite,
            (
                size,
                size
            )
        )

        # The sprite spins independently from the
        # direction the blade is travelling.
        sprite = pygame.transform.rotate(
            sprite,
            -self.sprite_angle
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
        if player in self.hit_players:
            return []

        self.hit_players.add(
            player
        )

        player.take_damage(
            self.damage
        )

        return []