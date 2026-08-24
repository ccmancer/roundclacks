import pygame
import random
from pathlib import Path


HEALTH_FONT = pygame.font.Font(None, 24)

SPRITE_FOLDER = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "sprites"
)


class Player:
    def __init__(
        self,
        x,
        y,
        radius,
        color,
        speed,
        weapon_class,
        attack_key
    ):
        self.position = pygame.Vector2(x, y)

        self.radius = radius
        self.color = color
        self.speed = speed

        self.sprite = pygame.image.load(
            SPRITE_FOLDER / "player.png"
        ).convert_alpha()

        self.weapon = weapon_class(self)
        self.attack_key = attack_key

        self.base_max_health = 100
        self.max_health = self.get_max_health()
        self.health = self.max_health

        self.reset_velocity(speed)

        self.external_velocity = pygame.Vector2()
        self.external_velocity_timer = 0

        self.pinned_arrows = []
        self.shellshock_timer = 0

    # -------------------------------------------------
    # UPDATE / DRAW
    # -------------------------------------------------

    def update(self, dt, width, height):
        if self.velocity.length_squared() > 0:
            self.velocity.scale_to_length(
                self.get_speed()
            )

        self.position += (
            self.velocity
            + self.external_velocity
        ) * dt

        if self.shellshock_timer > 0:
            self.shellshock_timer -= dt

            if self.shellshock_timer < 0:
                self.shellshock_timer = 0

        if self.external_velocity_timer > 0:
            self.external_velocity_timer -= dt
        else:
            self.external_velocity = pygame.Vector2()

        self.weapon.handle_player_bounds(
            width,
            height
        )

        self.weapon.update(dt)

    def draw(self, screen):
        self.weapon.draw_before_player(
            screen
        )

        sprite = self.get_sprite()

        rect = sprite.get_rect(
            center=self.position
        )

        screen.blit(
            sprite,
            rect
        )

        health_text = HEALTH_FONT.render(
            str(round(self.health)),
            True,
            "black"
        )

        health_rect = health_text.get_rect(
            center=(
                self.position.x,
                self.position.y
                - self.get_hitbox_radius()
                - 15
            )
        )

        screen.blit(
            health_text,
            health_rect
        )

        self.weapon.draw(screen)

    # -------------------------------------------------
    # SPRITE
    # -------------------------------------------------

    def get_sprite_size(self):
        return (
            self.get_hitbox_radius() * 2
        )

    def get_sprite(self):
        size = max(
            1,
            int(self.get_sprite_size())
        )

        sprite = pygame.transform.scale(
            self.sprite,
            (
                size,
                size
            )
        )

        sprite = sprite.copy()

        color = pygame.Color(
            self.color
        )

        sprite.fill(
            (
                color.r,
                color.g,
                color.b,
                255
            ),
            special_flags=pygame.BLEND_RGBA_MULT
        )

        return self.weapon.modify_player_sprite(
            sprite
        )

    # -------------------------------------------------
    # HEALTH
    # -------------------------------------------------

    def take_damage(self, damage):
        damage = self.weapon.modify_incoming_damage(
            damage
        )

        self.health -= damage

    def heal(self, amount):
        self.health = min(
            self.health + amount,
            self.max_health
        )

    def is_alive(self):
        return self.health > 0

    def get_health_ratio(self):
        if self.max_health <= 0:
            return 0

        return max(
            0,
            self.health / self.max_health
        )

    # -------------------------------------------------
    # PLAYER STATS
    # -------------------------------------------------

    def get_max_health(self):
        return (
            self.base_max_health
            * self.weapon.get_max_health_multiplier()
        )

    def get_hitbox_radius(self):
        return (
            self.radius
            * self.weapon.get_radius_multiplier()
        )

    def get_speed(self):
        speed = (
            self.speed
            * self.weapon.get_speed_multiplier()
        )

        for arrow in self.pinned_arrows:
            if arrow.is_pincushion_active_for(self):
                speed *= (
                    arrow.get_pincushion_speed_multiplier()
                )

        if self.shellshock_timer > 0:
            speed *= 0.5

        return speed

    # -------------------------------------------------
    # MOVEMENT
    # -------------------------------------------------

    def reset_velocity(self, speed):
        angle = random.randint(
            0,
            360
        )

        self.velocity = pygame.Vector2()

        self.velocity.from_polar(
            (
                speed,
                angle
            )
        )

    def apply_force(
        self,
        direction,
        force,
        duration
    ):
        if direction.length_squared() == 0:
            return

        direction = direction.normalize()

        self.external_velocity = (
            direction * force
        )

        self.external_velocity_timer = duration

    # -------------------------------------------------
    # STATUS EFFECTS
    # -------------------------------------------------

    def apply_shellshock(self, duration):
        self.shellshock_timer = max(
            self.shellshock_timer,
            duration
        )

    # -------------------------------------------------
    # RESET
    # -------------------------------------------------

    def reset(self, position):
        self.position = pygame.Vector2(
            position
        )

        self.max_health = (
            self.get_max_health()
        )

        self.health = self.max_health

        self.reset_velocity(
            self.speed
        )

        self.external_velocity = pygame.Vector2()
        self.external_velocity_timer = 0

        self.shellshock_timer = 0
        self.pinned_arrows = []

        self.weapon.reset()