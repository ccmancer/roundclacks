import pygame
import random

from weapons.weapon import Weapon
from entities.bomb_projectile import BombProjectile
from upgrades.upgrade_pool import BOMB_UPGRADES


class Bomb(Weapon):
    def __init__(self, player):
        super().__init__(
            player,
            50,     # orbit distance
            3,      # rotation speed
            25,     # base damage
            1.0,    # base cooldown
            False
        )

        self.upgrade_pool = BOMB_UPGRADES



    def draw(self, screen):
        pygame.draw.circle(
            screen,
            "black",
            self.position,
            12
        )

    def attack(self):
        if not self.can_attack():
            return []

        self.start_cooldown()

        spread = self.get_spread()

        offset = random.uniform(
            -spread,
            spread
        )

        direction = self.direction.rotate(offset)

        return [
            BombProjectile(
                self.position,
                direction,
                self.get_damage(),
                self.player,
                self.get_initial_momentum(),
                self.get_blast_radius(),
                self.get_blast_knockback(),
                self.get_self_damage_multiplier(),
                self.get_fuse_time(),
                self.get_mine_duration(),
                self.get_cluster_count(),
                False,
                self.get_pool_damage(),
                self.get_pyromaniac_heal(),
                self.get_shellshock_duration(),
                self.get_earthlight_ray_damage(),
                self.get_chaos_damage(),
                self.get_chaos_size()
            )
        ]

    def get_damage(self):
        damage = self.base_damage

        for upgrade in self.upgrades:
            if upgrade.name == "Lethality":
                damage *= 1.5 ** upgrade.stacks

            elif upgrade.name == "Fuse":
                damage *= 1.75 ** upgrade.stacks

            elif upgrade.name == "Direct Hit":
                damage *= 2 ** upgrade.stacks

            elif upgrade.name == "Nuke":
                damage *= 2 ** upgrade.stacks

        return damage

    def get_initial_momentum(self):
        momentum = 500

        for upgrade in self.upgrades:
            if upgrade.name == "Fastball":
                momentum *= 2 ** upgrade.stacks

        return momentum

    def get_blast_radius(self):
        radius = 75

        for upgrade in self.upgrades:
            if upgrade.name == "Gunpower":
                radius *= 1.5 ** upgrade.stacks

            elif upgrade.name == "Fuse":
                radius *= 1.75 ** upgrade.stacks

            elif upgrade.name == "Direct Hit":
                radius *= 0.75 ** upgrade.stacks

            elif upgrade.name == "Nuke":
                radius *= 2 ** upgrade.stacks

        return radius

    def get_blast_knockback(self):
        knockback = 500

        for upgrade in self.upgrades:
            if upgrade.name == "Extra Force":
                knockback *= 1.5 ** upgrade.stacks

            elif upgrade.name == "Fuse":
                knockback *= 1.75 ** upgrade.stacks

        return knockback

    def get_professional_stacks(self):
        stacks = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Professional":
                stacks += upgrade.stacks

        return stacks

    def get_pyromaniac_stacks(self):
        stacks = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Pyromaniac":
                stacks += upgrade.stacks

        # Professional becomes extra Pyromaniac stacks
        # when Pyromaniac is present.
        if stacks > 0:
            stacks += self.get_professional_stacks()

        return stacks

    def get_self_damage_multiplier(self):
        pyromaniac_stacks = 0
        professional_stacks = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Pyromaniac":
                pyromaniac_stacks += upgrade.stacks

            elif upgrade.name == "Professional":
                professional_stacks += upgrade.stacks

        # Pyromaniac overwrites Professional.
        if pyromaniac_stacks > 0:
            return 0

        multiplier = 1

        if professional_stacks > 0:
            multiplier *= 0.5 ** professional_stacks

        return multiplier

    def get_fuse_time(self):
        fuse_time = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Fuse":
                fuse_time += 0.5 * upgrade.stacks

        return fuse_time

    def get_shellshock_duration(self):
        duration = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Shellshock":
                duration = 5 * upgrade.stacks

        return duration

    def get_mine_duration(self):
        duration = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Mine":
                duration = 5 * upgrade.stacks

        return duration

    def get_cluster_count(self):
        count = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Cluster Bomb":
                count += 8 * upgrade.stacks

        return count

    def get_pool_damage(self):
        damage = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Nuke":
                damage = upgrade.stacks

        return damage

    def get_pyromaniac_heal(self):
        stacks = self.get_pyromaniac_stacks()

        return 0.5 * stacks

    def get_earthlight_ray_damage(self):
        damage = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Earthlight Ray":
                damage = (
                    self.get_damage()
                    * 0.5
                    * 2 ** (upgrade.stacks - 1)
                )

        return damage

    def get_chaos_damage(self):
        damage = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Chaos Bomb":
                damage = (
                    self.get_damage()
                    * 0.5
                    * 2 ** (upgrade.stacks - 1)
                )

        return damage

    def get_chaos_size(self):
        # Scythes get larger with the blast radius.
        return self.get_blast_radius() * 0.5

    def get_attack_cooldown(self):
        cooldown = self.base_cooldown

        for upgrade in self.upgrades:
            if upgrade.name == "Madness":
                cooldown *= 0.25 ** upgrade.stacks

            elif upgrade.name == "Nuke":
                cooldown *= 2 ** upgrade.stacks

        return cooldown

    def get_spread(self):
        spread = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Madness":
                spread += 20 * upgrade.stacks

        return spread