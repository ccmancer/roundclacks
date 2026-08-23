import pygame
import math

from weapons.weapon import Weapon
from entities.beam import Beam
from upgrades.upgrade_pool import GRIMOIRE_UPGRADES


class Grimoire(Weapon):
    def __init__(self, player):
        super().__init__(
            player,
            50,     # orbit distance
            3,      # rotation speed
            1,      # base tick damage
            1.0,    # base cooldown / downtime
            False
        )

        self.upgrade_pool = GRIMOIRE_UPGRADES

        # Slows movement/orbit while the beam is active.
        self.attack_slow_timer = 0

        # Tribeam self-damage timer.
        self.tribeam_self_damage_timer = 0

    def update(self, dt):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt

        if self.attack_slow_timer > 0:
            self.attack_slow_timer -= dt

            if self.attack_slow_timer < 0:
                self.attack_slow_timer = 0

        if self.tribeam_self_damage_timer > 0:
            self.tribeam_self_damage_timer -= dt

            if self.tribeam_self_damage_timer < 0:
                self.tribeam_self_damage_timer = 0

        # Tribeam self-damage happens once per tick,
        # regardless of how many books are active.
        tribeam_damage = self.get_tribeam_self_damage()

        if (
            tribeam_damage > 0
            and self.attack_slow_timer > 0
            and self.tribeam_self_damage_timer <= 0
        ):
            self.player.take_damage(
                tribeam_damage
            )

            self.tribeam_self_damage_timer = (
                self.get_tick_interval()
            )

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
        pygame.draw.rect(
            screen,
            "purple",
            (
                self.position.x - 12,
                self.position.y - 8,
                24,
                16
            )
        )

    def attack(self):
        if not self.can_attack():
            return []

        self.start_cooldown()

        self.attack_slow_timer = (
            self.get_beam_duration()
        )

        beams = []

        count = self.get_book_count()

        for i in range(count):
            offset = 0

            if count > 1:
                offset = (
                    i - (count - 1) / 2
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

    def get_book_count(self):
        count = 1

        for upgrade in self.upgrades:
            if upgrade.name == "Double Spark":
                count += upgrade.stacks

        return count

    def get_rotation_speed(self):
        speed = self.rotation_speed

        # Base firing slowdown.
        if self.attack_slow_timer > 0:
            speed *= 0.5

        for upgrade in self.upgrades:
            if upgrade.name == "Water Enchantment":
                speed *= 0.75 ** upgrade.stacks

        return speed

    def get_tick_damage(self):
        damage = self.base_damage

        for upgrade in self.upgrades:
            if upgrade.name == "Earth Enchantment":
                damage += upgrade.stacks

            elif upgrade.name == "Tribeam":
                damage *= 4 ** upgrade.stacks

        return damage

    def get_beam_duration(self):
        duration = 1.0

        for upgrade in self.upgrades:
            if upgrade.name == "Mana Reserves":
                duration *= 1.5 ** upgrade.stacks

            elif upgrade.name == "Fire Enchantment":
                duration *= 0.5 ** upgrade.stacks

            elif upgrade.name == "Master Spark":
                duration *= 3 ** upgrade.stacks

        return duration

    def get_tick_interval(self):
        interval = 0.02

        for upgrade in self.upgrades:
            if upgrade.name == "Hotter Beam":
                interval *= 0.5 ** upgrade.stacks

            elif upgrade.name == "Fire Enchantment":
                interval *= (1 / 3) ** upgrade.stacks

            elif upgrade.name == "Earth Enchantment":
                interval *= 1.25 ** upgrade.stacks

            elif upgrade.name == "Master Spark":
                interval *= (1 / 3) ** upgrade.stacks

        return interval

    def get_beam_width(self):
        width = 80

        for upgrade in self.upgrades:
            if upgrade.name == "Spell Proficiency":
                width *= 1.5 ** upgrade.stacks

            elif upgrade.name == "Water Enchantment":
                width *= 2 ** upgrade.stacks

            elif upgrade.name == "Master Spark":
                width *= 3 ** upgrade.stacks

        return width

    def get_knockback(self):
        force = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Faster Current":
                force += 250 * upgrade.stacks

        return force

    def get_lifesteal(self):
        lifesteal = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Wood Enchantment":
                lifesteal += 0.5 * upgrade.stacks

        return lifesteal

    def get_tribeam_self_damage(self):
        damage = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Tribeam":
                damage += upgrade.stacks

        return damage

    def get_attack_cooldown(self):
        cooldown = self.base_cooldown

        # Fast Reader only reduces downtime.
        for upgrade in self.upgrades:
            if upgrade.name == "Fast Reader":
                cooldown *= 0.5 ** upgrade.stacks

            elif upgrade.name == "Master Spark":
                cooldown *= 3 ** upgrade.stacks

        return (
            self.get_beam_duration()
            + cooldown
        )