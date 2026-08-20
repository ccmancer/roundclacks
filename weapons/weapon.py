import pygame
import math
import random

class Weapon:
    def __init__(
        self,
        player,
        distance,
        rotation_speed,
        base_damage,
        base_cooldown
    ):
        self.player = player

        self.distance = distance
        self.rotation_speed = rotation_speed

        self.base_damage = base_damage
        self.base_cooldown = base_cooldown

        self.upgrades = []

        self.cooldown_timer = 0

        self.angle = 0
        self.position = pygame.Vector2()
        self.direction = pygame.Vector2(1, 0)

    def update(self, dt):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt

        self.angle += self.rotation_speed * dt

        self.direction = pygame.Vector2(
            math.cos(self.angle),
            math.sin(self.angle)
        )

        self.position = (
            self.player.position
            + self.direction * self.distance
        )

    def draw(self, screen):
        pass

    def get_damage(self):
        return self.base_damage

    def get_attack_cooldown(self):
        return self.base_cooldown

    def can_attack(self):
        return self.cooldown_timer <= 0

    def start_cooldown(self):
        self.cooldown_timer = self.get_attack_cooldown()

    def attack(self):
        raise NotImplementedError

    def handle_collision(self, opponent):
        pass

    def add_upgrade(self, upgrade):
        for existing_upgrade in self.upgrades:
            if existing_upgrade.name == upgrade.name:
                existing_upgrade.stacks += 1
                return

        self.upgrades.append(upgrade)

    def get_hit_damage(self):
        damage = self.get_damage()

        critical_chance = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Critical":
                critical_chance += 0.20 * upgrade.stacks

        if random.random() < critical_chance:
            return damage * 3

        return damage

    def get_step_force(self):
        force = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Step-in":
                force += 300 * upgrade.stacks

        return force

    def reset(self):
        self.cooldown_timer = 0
        self.angle = random.uniform(0, math.tau)