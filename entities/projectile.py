import pygame
from pathlib import Path


SPRITE_FOLDER = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "sprites"
)


class Projectile:
    def __init__(
        self,
        position,
        direction,
        speed,
        damage,
        owner,
        radius,
        sprite_name=None
    ):
        self.position = pygame.Vector2(
            position
        )

        self.direction = pygame.Vector2(
            direction
        )

        if self.direction.length_squared() > 0:
            self.direction = (
                self.direction.normalize()
            )

        self.speed = speed
        self.damage = damage
        self.owner = owner

        # Gameplay hitbox.
        self.radius = radius

        self.alive = True

        # Normal projectiles cannot damage owner.
        self.can_hit_owner = False

        # Sprite.
        self.sprite = None

        if sprite_name is not None:
            self.sprite = pygame.image.load(
                SPRITE_FOLDER / sprite_name
            ).convert_alpha()

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(self, dt):
        self.position += (
            self.direction
            * self.speed
            * dt
        )

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------

    def draw(self, screen):
        if self.sprite is None:
            return

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
        return self.radius * 2

    def get_sprite_width(self):
        return self.radius * 2

    def get_sprite(self):
        if self.sprite is None:
            return None

        length = max(
            1,
            int(self.get_sprite_length())
        )

        width = max(
            1,
            int(self.get_sprite_width())
        )

        sprite = pygame.transform.scale(
            self.sprite,
            (length, width)
        )

        return pygame.transform.rotate(
            sprite,
            -self.direction.angle_to(
                pygame.Vector2(1, 0)
            )
        )

    # -------------------------------------------------
    # HITBOX
    # -------------------------------------------------

    def get_hitbox_radius(self):
        return self.radius

    # -------------------------------------------------
    # BOUNDS
    # -------------------------------------------------

    def is_out_of_bounds(self, width, height):
        radius = (
            self.get_hitbox_radius()
        )

        return (
            self.position.x < -radius
            or self.position.x > width + radius
            or self.position.y < -radius
            or self.position.y > height + radius
        )

    # -------------------------------------------------
    # HIT
    # -------------------------------------------------

    def hit(self, player):
        player.take_damage(
            self.damage
        )

        self.alive = False