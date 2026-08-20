import pygame
import math

from weapons.weapon import Weapon
from game.upgrade_pool import SWORD_UPGRADES

import pygame
import math

from weapons.weapon import Weapon
from game.upgrade_pool import SWORD_UPGRADES


class Sword(Weapon):
    def __init__(self, player):
        super().__init__(
            player,
            100,    # orbit distance
            3,      # base rotation speed
            30,     # base damage
            1.0     # base cooldown
        )

        self.base_length = 140
        self.width = 12

        self.hit_cooldown = 0.25
        self.hit_timer = 0

        self.attacking = False
        self.attack_angle = 0

        self.base_attack_rotation_speed = 20

        self.upgrade_pool = SWORD_UPGRADES

    def update(self, dt):
        if self.hit_timer > 0:
            self.hit_timer -= dt

        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt

        if self.attacking:
            self.angle += self.get_attack_rotation_speed() * dt
            self.attack_angle += self.get_attack_rotation_speed() * dt

            if self.attack_angle >= math.tau:
                self.attacking = False
                self.attack_angle = 0
        else:
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
        start = self.player.position

        end = (
            self.player.position
            + self.direction * self.get_length()
        )

        pygame.draw.line(
            screen,
            "black",
            start,
            end,
            self.width
        )

    def get_damage(self):
        damage = self.base_damage

        for upgrade in self.upgrades:
            if upgrade.name == "Sharpness":
                damage *= 1.25 ** upgrade.stacks

        return damage

    def get_length(self):
        length = self.base_length

        for upgrade in self.upgrades:
            if upgrade.name == "Longsword":
                length *= 1.5 ** upgrade.stacks

        return length

    def get_rotation_speed(self):
        speed = self.rotation_speed

        for upgrade in self.upgrades:
            if upgrade.name == "Trained":
                speed *= 1.5 ** upgrade.stacks

        return speed

    def get_attack_rotation_speed(self):
        speed = self.base_attack_rotation_speed

        for upgrade in self.upgrades:
            if upgrade.name == "Trained":
                speed *= 1.5 ** upgrade.stacks

        return speed

    def can_hit(self):
        return self.hit_timer <= 0

    def hit(self):
        self.hit_timer = self.hit_cooldown

    def attack(self):
        if not self.can_attack():
            return

        self.start_cooldown()

        self.attacking = True
        self.attack_angle = 0