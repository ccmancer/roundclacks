import pygame
import math
import random

from weapons.weapon import Weapon
from entities.arrow import Arrow
from upgrades.upgrade_pool import BOW_UPGRADES
from entities.bear_trap import BearTrap


class Bow(Weapon):
    def __init__(self, player):
        super().__init__(
            player,
            50,    # orbit distance
            3,     # rotation speed
            20,    # base damage
            0.75,  # base cooldown
            False
        )

        self.upgrade_pool = BOW_UPGRADES

    def update(self, dt):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt

        self.angle += self.get_rotation_speed() * dt

        self.direction = pygame.Vector2(
            math.cos(self.angle),
            math.sin(self.angle)
        )

        self.position = (
            self.player.position
            + self.direction * self.distance
        )

    def draw(self, screen):
        direction = self.direction.normalize()

        # Perpendicular to the bow direction
        perpendicular = pygame.Vector2(
            -direction.y,
            direction.x
        )

        # Bow dimensions
        bow_length = 70
        bow_curve = 20

        center = self.position

        # Endpoints of the bow
        top = center + perpendicular * (bow_length / 2)
        bottom = center - perpendicular * (bow_length / 2)

        # Bow curves away from the firing direction
        curve = center + direction * bow_curve

        # Draw the curved bow using several line segments
        points = []

        for i in range(11):
            t = i / 10

            point = (
                (1 - t) ** 2 * top
                + 2 * (1 - t) * t * curve
                + t ** 2 * bottom
            )

            points.append(point)

        pygame.draw.lines(
            screen,
            "brown",
            False,
            points,
            8
        )

        # Draw the bow string
        pygame.draw.line(
            screen,
            "black",
            top,
            bottom,
            2
        )

    def attack(self):
        if not self.can_attack():
            return []

        self.start_cooldown()

        projectiles = []

        count = self.get_projectile_count()

        # Shotgun keeps its fixed multi-arrow spread.
        if count > 1:
            spread = self.get_spread()

            for i in range(count):
                offset = (
                    (i - (count - 1) / 2)
                    * spread
                )

                direction = self.direction.rotate(offset)

                projectiles.append(
                    Arrow(
                        self.position,
                        direction,
                        self.get_damage(),
                        self.player,
                        self.get_projectile_speed(),
                        self.get_projectile_size(),
                        self.get_pincushion_duration(),
                        self.get_pincushion_slow(),
                        self.get_knockback(),
                        self.get_homing_force(),
                        self.get_homing_range(),
                        self.get_bounces()
                    )
                )

        # Machinegun fires one arrow with random spread.
        else:
            spread = self.get_spread()

            offset = random.uniform(
                -spread,
                spread
            )

            direction = self.direction.rotate(offset)

            recoil = self.get_recoil()

            if recoil > 0:
                self.player.apply_force(
                    -direction,
                    recoil,
                    0.1
                )

            projectiles.append(
                Arrow(
                    self.position,
                    direction,
                    self.get_damage(),
                    self.player,
                    self.get_projectile_speed(),
                    self.get_projectile_size(),
                    self.get_pincushion_duration(),
                    self.get_pincushion_slow(),
                    self.get_knockback(),
                    self.get_homing_force(),
                    self.get_homing_range(),
                    self.get_bounces()
                )
            )

        # Bear Trap
        trap_duration = self.get_bear_trap_duration()

        if trap_duration > 0:
            projectiles.append(
                BearTrap(
                    self.position,
                    self.get_damage(),
                    self.player,
                    trap_duration
                )
            )

        return projectiles

    def get_projectile_speed(self):
        speed = 500

        for upgrade in self.upgrades:
            if upgrade.name == "Aerodynamic":
                speed *= 2 ** upgrade.stacks

            elif upgrade.name == "Sniper":
                speed *= 2 ** upgrade.stacks

            elif upgrade.name == "Heavy Arrows":
                speed *= 0.75 ** upgrade.stacks

            elif upgrade.name == "MLG":
                speed *= 4 ** upgrade.stacks

        return speed

    def get_recoil(self):
        recoil = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Lightweight":
                recoil += 250 * upgrade.stacks

        return recoil

    def get_rotation_speed(self):
        speed = self.rotation_speed

        for upgrade in self.upgrades:
            if upgrade.name == "Aim Sensitivity":
                speed *= 1.5 ** upgrade.stacks

            elif upgrade.name == "Sniper":
                speed *= 0.75 ** upgrade.stacks

            elif upgrade.name == "MLG":
                speed *= 3 ** upgrade.stacks

        return speed

    def get_attack_cooldown(self):
        cooldown = self.base_cooldown

        for upgrade in self.upgrades:
            if upgrade.name == "Machinegun":
                cooldown *= 0.05 ** upgrade.stacks

            elif upgrade.name == "Greatbow":
                cooldown *= 2 ** upgrade.stacks

            elif upgrade.name == "Sniper":
                cooldown *= 1.5 ** upgrade.stacks

            elif upgrade.name == "Quickdraw":
                cooldown *= 0.5 ** upgrade.stacks

        return cooldown

    def get_damage(self):
        damage = self.base_damage

        for upgrade in self.upgrades:
            if upgrade.name == "Machinegun":
                damage *= 0.5 ** upgrade.stacks

            elif upgrade.name == "Pointiness":
                damage *= 1.25 ** upgrade.stacks

            elif upgrade.name == "Greatbow":
                damage *= 2 ** upgrade.stacks

            elif upgrade.name == "Sniper":
                damage *= 2 ** upgrade.stacks

            elif upgrade.name == "Heavy Arrows":
                damage *= 2 ** upgrade.stacks

            elif upgrade.name == "Shotgun":
                damage *= 0.5 ** upgrade.stacks

            elif upgrade.name == "MLG":
                damage *= 5 ** upgrade.stacks

        return damage

    def get_projectile_size(self):
        size = 6

        for upgrade in self.upgrades:
            if upgrade.name == "Greatbow":
                size *= 1.5 ** upgrade.stacks

            elif upgrade.name == "Heavy Arrows":
                size *= 1.5 ** upgrade.stacks

        return size

    def get_pincushion_duration(self):
        duration = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Pincushion":
                duration = 5 * upgrade.stacks

        return duration

    def get_pincushion_slow(self):
        for upgrade in self.upgrades:
            if upgrade.name == "Pincushion":
                return 0.25

        return 0

    def get_knockback(self):
        force = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Heavy Arrows":
                force += 250 * upgrade.stacks

        return force

    def get_bear_trap_duration(self):
        duration = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Bear Trap":
                duration = 5 * upgrade.stacks

        return duration

    def get_projectile_count(self):
        count = 1

        for upgrade in self.upgrades:
            if upgrade.name == "Shotgun":
                count += 5 * upgrade.stacks

        return count

    def get_spread(self):
        spread = 0

        # Shotgun: fixed spread between multiple arrows
        for upgrade in self.upgrades:
            if upgrade.name == "Shotgun":
                spread += 5 * upgrade.stacks

            # Machinegun: random spread for the single arrow
            elif upgrade.name == "Machinegun":
                spread += 10 * upgrade.stacks

        return spread

    def get_homing_force(self):
        force = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Homing":
                force += 250 * upgrade.stacks

        return force

    def get_homing_range(self):
        range_ = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Homing":
                range_ = 250 * upgrade.stacks

        return range_

    def get_bounces(self):
        bounces = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Ricochet":
                bounces += 5 * upgrade.stacks

        return bounces