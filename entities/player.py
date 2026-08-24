import pygame
import random
from pathlib import Path


HEALTH_FONT = pygame.font.Font(None, 24)

SPRITE_FOLDER = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "sprites"
)

SOUND_FOLDER = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "sounds"
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

        # -------------------------------------------------
        # Sprite / Sound
        # -------------------------------------------------

        self.sprite = pygame.image.load(
            SPRITE_FOLDER / "player.png"
        ).convert_alpha()

        self.hurt_sound = pygame.mixer.Sound(
            SOUND_FOLDER / "hurt.mp3"
        )

        # Prevent rapid repeated hurt sounds from
        # becoming too loud.
        self.hurt_sound_timer = 0
        self.hurt_sound_cooldown = 0.1

        # -------------------------------------------------
        # Weapon
        # -------------------------------------------------

        self.weapon = weapon_class(self)
        self.attack_key = attack_key

        # -------------------------------------------------
        # Health
        # -------------------------------------------------

        self.base_max_health = 100
        self.max_health = self.get_max_health()
        self.health = self.max_health

        # -------------------------------------------------
        # Movement
        # -------------------------------------------------

        self.reset_velocity(speed)

        self.external_velocity = pygame.Vector2()
        self.external_velocity_timer = 0

        # -------------------------------------------------
        # Status Effects
        # -------------------------------------------------

        # Pincushion.
        self.pinned_arrows = []

        # Shellshock.
        self.shellshock_timer = 0

        # -------------------------------------------------
        # Damage Flash
        # -------------------------------------------------

        self.damage_flash_timer = 0
        self.damage_flash_duration = 0.5

    # -------------------------------------------------
    # UPDATE / DRAW
    # -------------------------------------------------

    def update(self, dt, width, height):
        # -------------------------------------------------
        # Hurt sound cooldown
        # -------------------------------------------------

        if self.hurt_sound_timer > 0:
            self.hurt_sound_timer -= dt

            if self.hurt_sound_timer < 0:
                self.hurt_sound_timer = 0

        # -------------------------------------------------
        # Damage flash
        # -------------------------------------------------

        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt

            if self.damage_flash_timer < 0:
                self.damage_flash_timer = 0

        # -------------------------------------------------
        # Movement
        # -------------------------------------------------

        # Preserve movement direction while updating speed.
        if self.velocity.length_squared() > 0:
            self.velocity.scale_to_length(
                self.get_speed()
            )

        self.position += (
            self.velocity
            + self.external_velocity
        ) * dt

        # -------------------------------------------------
        # Shellshock
        # -------------------------------------------------

        if self.shellshock_timer > 0:
            self.shellshock_timer -= dt

            if self.shellshock_timer < 0:
                self.shellshock_timer = 0

        # -------------------------------------------------
        # External movement
        # -------------------------------------------------

        if self.external_velocity_timer > 0:
            self.external_velocity_timer -= dt
        else:
            self.external_velocity = pygame.Vector2()

        # -------------------------------------------------
        # Weapon-specific behavior
        # -------------------------------------------------

        self.weapon.handle_player_bounds(
            width,
            height
        )

        # Update weapon after player movement.
        self.weapon.update(dt)

    def draw(self, screen):
        # Weapon-specific visuals behind player.
        self.weapon.draw_before_player(
            screen
        )

        # -------------------------------------------------
        # Player sprite
        # -------------------------------------------------

        sprite = self.get_sprite()

        rect = sprite.get_rect(
            center=self.position
        )

        screen.blit(
            sprite,
            rect
        )

        # -------------------------------------------------
        # Health number
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Weapon
        # -------------------------------------------------

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

        # Apply player color.
        sprite.fill(
            (
                color.r,
                color.g,
                color.b,
                255
            ),
            special_flags=pygame.BLEND_RGBA_MULT
        )

        # -------------------------------------------------
        # Damage flash
        # -------------------------------------------------

        if self.damage_flash_timer > 0:
            flash_strength = (
                self.damage_flash_timer
                / self.damage_flash_duration
            )

            amount = int(
                255 * flash_strength
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

        # -------------------------------------------------
        # Weapon sprite effects
        # -------------------------------------------------

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

        # Restart damage flash.
        self.damage_flash_timer = (
            self.damage_flash_duration
        )

        # Play hurt sound with a very small cooldown.
        if self.hurt_sound_timer <= 0:
            self.hurt_sound.play()

            self.hurt_sound_timer = (
                self.hurt_sound_cooldown
            )

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

        # Pincushion.
        for arrow in self.pinned_arrows:
            if arrow.is_pincushion_active_for(self):
                speed *= (
                    arrow.get_pincushion_speed_multiplier()
                )

        # Shellshock.
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

        self.damage_flash_timer = 0
        self.hurt_sound_timer = 0

        self.weapon.reset()