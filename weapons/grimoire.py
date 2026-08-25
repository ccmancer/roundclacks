import pygame
import math
from pathlib import Path

from weapons.weapon import Weapon
from entities.beam import Beam
from upgrades.upgrade_pool import GRIMOIRE_UPGRADES


SPRITE_FOLDER = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "sprites"
    / "game"
)

SOUND_FOLDER = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "audio"
    / "game"
)


class Grimoire(Weapon):
    def __init__(self, player):
        super().__init__(
            player,
            50,
            3,
            1,
            2.0,
            False,
            "grimoire.png",
            80,
            80
        )

        # -------------------------------------------------
        # Sprites
        # -------------------------------------------------

        self.attack_sprite = pygame.image.load(
            SPRITE_FOLDER / "grimoire_attack.png"
        ).convert_alpha()

        # -------------------------------------------------
        # Sound
        # -------------------------------------------------

        self.beam_sound = (
            self.player.game.audio.load_game_sound(
                SOUND_FOLDER / "grimoire_beam.mp3"
            )
        )

        self.beam_sound_channel = None

        # -------------------------------------------------
        # State
        # -------------------------------------------------

        self.upgrade_pool = GRIMOIRE_UPGRADES

        self.attack_slow_timer = 0

        self.tribeam_self_damage_timer = 0

    # -------------------------------------------------
    # UPDATE / DRAW
    # -------------------------------------------------

    def update(self, dt):
        was_attacking = self.is_attacking()

        # -------------------------------------------------
        # Cooldown
        # -------------------------------------------------

        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt

            if self.cooldown_timer < 0:
                self.cooldown_timer = 0

        # -------------------------------------------------
        # Beam timer
        # -------------------------------------------------

        if self.attack_slow_timer > 0:
            self.attack_slow_timer -= dt

            if self.attack_slow_timer < 0:
                self.attack_slow_timer = 0

        # -------------------------------------------------
        # Beam ended
        # -------------------------------------------------

        if (
            was_attacking
            and not self.is_attacking()
        ):
            self.stop_beam_sound()
            self.start_cooldown()

        # -------------------------------------------------
        # Tribeam self-damage timer
        # -------------------------------------------------

        if self.tribeam_self_damage_timer > 0:
            self.tribeam_self_damage_timer -= dt

            if self.tribeam_self_damage_timer < 0:
                self.tribeam_self_damage_timer = 0

        tribeam_damage = (
            self.get_tribeam_self_damage()
        )

        if (
            tribeam_damage > 0
            and self.is_attacking()
            and self.tribeam_self_damage_timer <= 0
        ):
            self.player.take_damage(
                tribeam_damage
            )

            self.tribeam_self_damage_timer = (
                self.get_tick_interval()
            )

        # -------------------------------------------------
        # Orbit
        # -------------------------------------------------

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
    # STATE
    # -------------------------------------------------

    def is_attacking(self):
        return self.attack_slow_timer > 0

    # -------------------------------------------------
    # SOUND
    # -------------------------------------------------

    def start_beam_sound(self):
        if (
            self.beam_sound_channel is not None
            and self.beam_sound_channel.get_busy()
        ):
            return

        self.beam_sound_channel = (
            self.beam_sound.play(-1)
        )

    def stop_beam_sound(self):
        if self.beam_sound_channel is not None:
            self.beam_sound_channel.stop()
            self.beam_sound_channel = None

    def on_death(self):
        self.stop_beam_sound()

    # -------------------------------------------------
    # SPRITE
    # -------------------------------------------------

    def get_sprite(self):
        if self.is_attacking():
            base_sprite = self.attack_sprite
        else:
            base_sprite = self.sprite

        sprite = pygame.transform.scale(
            base_sprite,
            (
                int(self.get_sprite_length()),
                int(self.get_sprite_width())
            )
        )

        sprite = pygame.transform.rotate(
            sprite,
            -math.degrees(self.angle)
        )

        if (
            self.can_attack()
            and not self.is_attacking()
        ):
            sprite = self.apply_ready_glow(
                sprite,
                self.get_ready_glow_strength()
            )

        return sprite

    def get_sprite_length(self):
        return self.base_sprite_length

    def get_sprite_width(self):
        return self.base_sprite_width

    # -------------------------------------------------
    # ATTACK
    # -------------------------------------------------

    def attack(self):
        if not self.can_attack():
            return []

        self.attack_slow_timer = (
            self.get_beam_duration()
        )

        self.start_beam_sound()

        beams = []

        count = self.get_book_count()

        for i in range(count):
            offset = 0

            if count > 1:
                offset = (
                    i
                    - (count - 1) / 2
                ) * 20

            beams.append(
                Beam(
                    self,
                    self.get_tick_damage(),
                    self.get_beam_duration(),
                    self.get_beam_width(),
                    self.get_tick_interval(),
                    self.get_knockback(),
                    self.get_lifesteal(),
                    offset
                )
            )

        return beams

    # -------------------------------------------------
    # PLAYER STATS / DAMAGE
    # -------------------------------------------------

    def get_damage(self):
        return self.get_tick_damage()

    def get_speed_multiplier(self):
        multiplier = (
            super().get_speed_multiplier()
        )

        if self.is_attacking():
            multiplier *= 0.5

        return multiplier

    def modify_incoming_damage(self, damage):
        damage = (
            super().modify_incoming_damage(
                damage
            )
        )

        if self.is_attacking():

            for upgrade in self.upgrades:

                if upgrade.name == "Magic Barrier":
                    damage *= (
                        0.1 ** upgrade.stacks
                    )

        return damage

    def get_attack_cooldown(self):
        cooldown = self.base_cooldown

        for upgrade in self.upgrades:

            if upgrade.name == "Fast Reader":
                cooldown *= (
                    0.5 ** upgrade.stacks
                )

            elif upgrade.name == "Master Spark":
                cooldown *= (
                    3 ** upgrade.stacks
                )

        return cooldown

    # -------------------------------------------------
    # BEAM
    # -------------------------------------------------

    def get_book_count(self):
        count = 1

        for upgrade in self.upgrades:

            if upgrade.name == "Double Spark":
                count += upgrade.stacks

        return count

    def get_rotation_speed(self):
        speed = self.rotation_speed

        if self.is_attacking():
            speed *= 0.5

        for upgrade in self.upgrades:

            if upgrade.name == "Water Enchantment":
                speed *= (
                    0.75 ** upgrade.stacks
                )

        return speed

    def get_tick_damage(self):
        damage = self.base_damage

        for upgrade in self.upgrades:

            if upgrade.name == "Earth Enchantment":
                damage += upgrade.stacks

            elif upgrade.name == "Tribeam":
                damage *= (
                    4 ** upgrade.stacks
                )

        return damage

    def get_beam_duration(self):
        duration = 1.0

        for upgrade in self.upgrades:

            if upgrade.name == "Mana Reserves":
                duration *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Fire Enchantment":
                duration *= (
                    0.5 ** upgrade.stacks
                )

            elif upgrade.name == "Master Spark":
                duration *= (
                    3 ** upgrade.stacks
                )

        return duration

    def get_tick_interval(self):
        interval = 0.02

        for upgrade in self.upgrades:

            if upgrade.name == "Hotter Beam":
                interval *= (
                    0.5 ** upgrade.stacks
                )

            elif upgrade.name == "Fire Enchantment":
                interval *= (
                    (1 / 3)
                    ** upgrade.stacks
                )

            elif upgrade.name == "Earth Enchantment":
                interval *= (
                    1.25 ** upgrade.stacks
                )

            elif upgrade.name == "Master Spark":
                interval *= (
                    (1 / 3)
                    ** upgrade.stacks
                )

        return interval

    def get_beam_width(self):
        width = 80

        for upgrade in self.upgrades:

            if upgrade.name == "Spell Proficiency":
                width *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Water Enchantment":
                width *= (
                    2 ** upgrade.stacks
                )

            elif upgrade.name == "Master Spark":
                width *= (
                    3 ** upgrade.stacks
                )

        return width

    def get_knockback(self):
        force = 0

        for upgrade in self.upgrades:

            if upgrade.name == "Faster Current":
                force += (
                    250
                    * upgrade.stacks
                )

        return force

    def get_lifesteal(self):
        lifesteal = 0

        for upgrade in self.upgrades:

            if upgrade.name == "Wood Enchantment":
                lifesteal += (
                    0.5
                    * upgrade.stacks
                )

        return lifesteal

    def get_tribeam_self_damage(self):
        damage = 0

        for upgrade in self.upgrades:

            if upgrade.name == "Tribeam":
                damage += upgrade.stacks

        return damage

    # -------------------------------------------------
    # RESET
    # -------------------------------------------------

    def reset(self):
        super().reset()

        self.attack_slow_timer = 0
        self.tribeam_self_damage_timer = 0

        self.stop_beam_sound()