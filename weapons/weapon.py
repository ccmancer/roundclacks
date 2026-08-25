import pygame
import math
import random
from pathlib import Path

from upgrades.upgrade import Upgrade


SPRITE_FOLDER = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "sprites"
    / "game"
)


class Weapon:
    def __init__(
        self,
        player,
        distance,
        rotation_speed,
        base_damage,
        base_cooldown,
        melee,
        sprite_filename=None,
        sprite_length=0,
        sprite_width=0
    ):
        self.player = player

        self.distance = distance
        self.rotation_speed = rotation_speed

        self.base_damage = base_damage
        self.base_cooldown = base_cooldown
        self.melee = melee

        self.upgrades = []

        self.cooldown_timer = 0

        # -------------------------------------------------
        # Weapon position
        # -------------------------------------------------

        self.angle = 0
        self.position = pygame.Vector2()
        self.direction = pygame.Vector2(1, 0)

        # -------------------------------------------------
        # Sprite
        # -------------------------------------------------

        self.sprite_filename = sprite_filename

        self.base_sprite_length = sprite_length
        self.base_sprite_width = sprite_width

        self.sprite = None

        if sprite_filename is not None:
            self.sprite = pygame.image.load(
                SPRITE_FOLDER / sprite_filename
            ).convert_alpha()

    # -------------------------------------------------
    # UPDATE / DRAW
    # -------------------------------------------------

    def update(self, dt):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt

            if self.cooldown_timer < 0:
                self.cooldown_timer = 0

        self.angle += (
            self.get_rotation_speed()
            * dt
        )

        self.direction = pygame.Vector2(
            math.cos(self.angle),
            math.sin(self.angle)
        )

        self.position = (
            self.player.position
            + self.direction * self.distance
        )

    def draw_before_player(self, screen):
        pass

    def draw(self, screen):
        if self.sprite is None:
            return

        sprite = self.get_sprite()

        if sprite is None:
            return

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
        return self.base_sprite_length

    def get_sprite_width(self):
        return self.base_sprite_width

    def get_sprite_scale(self):
        return 1

    def get_sprite(self, angle=None):
        if self.sprite is None:
            return None

        length = max(
            1,
            int(
                self.get_sprite_length()
                * self.get_sprite_scale()
            )
        )

        width = max(
            1,
            int(
                self.get_sprite_width()
                * self.get_sprite_scale()
            )
        )

        sprite = pygame.transform.scale(
            self.sprite,
            (
                length,
                width
            )
        )

        if angle is None:
            angle = self.angle

        return pygame.transform.rotate(
            sprite,
            -math.degrees(angle)
        )

    # -------------------------------------------------
    # READY GLOW
    # -------------------------------------------------

    def get_ready_glow_strength(self):
        if not self.can_attack():
            return 0

        time = (
            pygame.time.get_ticks()
            / 1000
        )

        return (
            math.sin(
                time * 5
            )
            + 1
        ) / 2

    def apply_ready_glow(
        self,
        sprite,
        strength
    ):
        if sprite is None or strength <= 0:
            return sprite

        sprite = sprite.copy()

        amount = int(
            255 * strength
        )

        sprite.fill(
            (
                amount,
                amount,
                amount
            ),
            special_flags=pygame.BLEND_RGB_ADD
        )

        return sprite

    def modify_player_sprite(self, sprite):
        return sprite

    # -------------------------------------------------
    # ATTACK
    # -------------------------------------------------

    def attack(self):
        raise NotImplementedError

    def is_attacking(self):
        return False

    def get_damage(self):
        return self.base_damage

    def get_attack_cooldown(self):
        return self.base_cooldown

    def can_attack(self):
        return (
            self.cooldown_timer <= 0
            and not self.is_attacking()
        )

    def start_cooldown(self):
        self.cooldown_timer = (
            self.get_attack_cooldown()
        )

    def reset_cooldown(self):
        self.cooldown_timer = 0

    # -------------------------------------------------
    # PLAYER STATS
    # -------------------------------------------------

    def get_max_health_multiplier(self):
        multiplier = 1

        for upgrade in self.upgrades:
            if upgrade.name == "Armor":
                multiplier *= (
                    1.25 ** upgrade.stacks
                )

            elif upgrade.name == "Juggernaut":
                multiplier *= (
                    2 ** upgrade.stacks
                )

            elif upgrade.name == "Light Armor":
                multiplier *= (
                    1.1 ** upgrade.stacks
                )

            elif upgrade.name == "Brute":
                multiplier *= (
                    1.5 ** upgrade.stacks
                )

        return multiplier

    def get_radius_multiplier(self):
        multiplier = 1

        for upgrade in self.upgrades:
            if upgrade.name == "Juggernaut":
                multiplier *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Lightweight":
                multiplier *= (
                    0.75 ** upgrade.stacks
                )

        return multiplier

    def get_speed_multiplier(self):
        multiplier = 1

        for upgrade in self.upgrades:
            if upgrade.name == "Rage":
                missing_health = (
                    1
                    - self.player.get_health_ratio()
                )

                multiplier *= (
                    1
                    + missing_health
                    * upgrade.stacks
                    * 2
                )

            elif upgrade.name == "Light Armor":
                multiplier *= (
                    1.25 ** upgrade.stacks
                )

        return multiplier

    def get_rotation_speed(self):
        return self.rotation_speed

    def modify_incoming_damage(self, damage):
        return damage

    # -------------------------------------------------
    # PLAYER / ARENA INTERACTION
    # -------------------------------------------------

    def handle_player_bounds(
        self,
        width,
        height
    ):
        radius = (
            self.player.get_hitbox_radius()
        )

        bounced = False

        bounce_angle = 10

        # -------------------------------------------------
        # Left wall
        # -------------------------------------------------

        if self.player.position.x - radius <= 0:
            self.player.position.x = radius

            if self.player.velocity.x < 0:
                self.player.velocity.x *= -1

                self.player.velocity = (
                    self.player.velocity.rotate(
                        -bounce_angle
                    )
                )

                bounced = True

            if self.player.external_velocity.x < 0:
                self.player.external_velocity.x = 0

        # -------------------------------------------------
        # Right wall
        # -------------------------------------------------

        elif self.player.position.x + radius >= width:
            self.player.position.x = (
                width - radius
            )

            if self.player.velocity.x > 0:
                self.player.velocity.x *= -1

                self.player.velocity = (
                    self.player.velocity.rotate(
                        bounce_angle
                    )
                )

                bounced = True

            if self.player.external_velocity.x > 0:
                self.player.external_velocity.x = 0

        # -------------------------------------------------
        # Top wall
        # -------------------------------------------------

        if self.player.position.y - radius <= 0:
            self.player.position.y = radius

            if self.player.velocity.y < 0:
                self.player.velocity.y *= -1

                self.player.velocity = (
                    self.player.velocity.rotate(
                        bounce_angle
                    )
                )

                bounced = True

            if self.player.external_velocity.y < 0:
                self.player.external_velocity.y = 0

        # -------------------------------------------------
        # Bottom wall
        # -------------------------------------------------

        elif self.player.position.y + radius >= height:
            self.player.position.y = (
                height - radius
            )

            if self.player.velocity.y > 0:
                self.player.velocity.y *= -1

                self.player.velocity = (
                    self.player.velocity.rotate(
                        -bounce_angle
                    )
                )

                bounced = True

            if self.player.external_velocity.y > 0:
                self.player.external_velocity.y = 0

        # -------------------------------------------------
        # Preserve movement speed
        # -------------------------------------------------

        if (
            bounced
            and self.player.velocity.length_squared() > 0
        ):
            self.player.velocity.scale_to_length(
                self.player.get_speed()
            )

    # -------------------------------------------------
    # COLLISION / UPGRADES
    # -------------------------------------------------

    def handle_collision(self, opponent):
        pass

    def has_upgrade(self, name):
        return any(
            upgrade.name == name
            for upgrade in self.upgrades
        )

    def add_upgrade(self, upgrade):
        for existing_upgrade in self.upgrades:
            if existing_upgrade.name == upgrade.name:
                existing_upgrade.stacks += 1
                return

        self.upgrades.append(
            Upgrade(
                upgrade.name,
                upgrade.rarity,
                upgrade.description
            )
        )

    # -------------------------------------------------
    # RESET / DEATH
    # -------------------------------------------------

    def reset(self):
        self.cooldown_timer = 0

        self.angle = random.uniform(
            0,
            math.tau
        )

    def on_death(self):
        """
        Called when the round ends.

        Weapons with looping sounds or other
        persistent effects override this.
        """
        pass