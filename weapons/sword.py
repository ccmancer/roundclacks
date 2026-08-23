import pygame
import math

from weapons.weapon import Weapon
from upgrades.upgrade_pool import SWORD_UPGRADES
from entities.magic_slash import MagicSlash

class Sword(Weapon):
    def __init__(self, player):
        super().__init__(
            player,
            100,    # orbit distance
            3,      # base rotation speed
            20,     # base damage
            1.0,     # base cooldown
            True
        )

        self.base_length = 140
        self.width = 12

        # Hit cooldown is based on degrees traveled
        self.hit_angle_cooldown = math.radians(60)
        self.hit_angle = self.hit_angle_cooldown

        # Beyblade temporary speed buffs
        self.beyblade_buffs = []

        self.attacking = False
        self.attack_angle = 0

        self.base_attack_rotation_speed = 20

        self.upgrade_pool = SWORD_UPGRADES

    def update(self, dt):
        # Weapon attack cooldown
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt

        # Remove expired Beyblade buffs
        self.beyblade_buffs = [
            timer - dt
            for timer in self.beyblade_buffs
            if timer - dt > 0
        ]

        if self.attacking:
            rotation_speed = self.get_attack_rotation_speed()

            self.angle += rotation_speed * dt
            self.attack_angle += rotation_speed * dt
            self.hit_angle += rotation_speed * dt

            if self.attack_angle >= self.get_attack_total_angle():
                self.attacking = False
                self.attack_angle = 0

        else:
            rotation_speed = self.get_rotation_speed()

            self.angle += rotation_speed * dt
            self.hit_angle += rotation_speed * dt

        self.direction = pygame.Vector2(
            math.cos(self.angle),
            math.sin(self.angle)
        )

        self.position = (
            self.player.position
            + self.direction * self.distance
        )

    def draw(self, screen):
        blade_count = self.get_blade_count()

        for i in range(blade_count):
            angle = (
                self.angle
                + (math.tau / blade_count) * i
            )

            direction = pygame.Vector2(
                math.cos(angle),
                math.sin(angle)
            )

            start = self.player.position

            end = (
                self.player.position
                + direction * self.get_length()
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

            elif upgrade.name == "Greatsword":
                damage *= 1.5 ** upgrade.stacks

            elif upgrade.name == "Rage":
                missing_health = 1 - self.player.get_health_ratio()
                damage *= (
                    1
                    + missing_health
                    * upgrade.stacks
                    * 2
                )

            elif upgrade.name == "Hero":
                damage *= 1.5 ** upgrade.stacks

        return damage

    def get_length(self):
        length = self.base_length

        for upgrade in self.upgrades:
            if upgrade.name == "Longsword":
                length *= 1.5 ** upgrade.stacks

            elif upgrade.name == "Greatsword":
                length *= 1.5 ** upgrade.stacks

            elif upgrade.name == "Juggernaut":
                length *= 1.5 ** upgrade.stacks

        return length

    def get_rotation_speed(self):
        speed = self.rotation_speed

        for upgrade in self.upgrades:
            if upgrade.name == "Trained":
                speed *= 1.5 ** upgrade.stacks

            elif upgrade.name == "Greatsword":
                speed *= 0.75 ** upgrade.stacks

        return speed

    def get_attack_cooldown(self):
        cooldown = self.base_cooldown

        for upgrade in self.upgrades:
            if upgrade.name == "Hero":
                cooldown *= 0.5 ** upgrade.stacks

        return cooldown

    def get_attack_rotation_speed(self):
        speed = self.base_attack_rotation_speed

        for upgrade in self.upgrades:
            if upgrade.name == "Trained":
                speed *= 1.5 ** upgrade.stacks

            elif upgrade.name == "Double Spin":
                speed *= 1.5 ** upgrade.stacks

            elif upgrade.name == "Greatsword":
                speed *= 0.75 ** upgrade.stacks

            elif upgrade.name == "Beyblade":
                beyblade_stacks = len(self.beyblade_buffs)
                if beyblade_stacks > 0:
                    speed *= 1.25 ** beyblade_stacks


        return speed

    def get_attack_total_angle(self):
        spins = 1

        for upgrade in self.upgrades:
            if upgrade.name == "Double Spin":
                spins += upgrade.stacks

        return math.tau * spins

    def can_hit(self):
        return self.hit_angle >= self.hit_angle_cooldown

    def hit(self, player):
        self.hit_angle = 0
        self.trigger_beyblade()
        damage = self.get_damage()

        player.take_damage(damage)

        self.player.heal(
            self.get_lifesteal() * damage
        )

        vortex_force = self.get_vortex_force()

        if vortex_force > 0:
            direction = (
                self.player.position
                - player.position
            )

            self.player.opponent.apply_force(
                direction,
                vortex_force,
                0.2
            )

    def attack(self):
        if not self.can_attack():
            return []

        self.start_cooldown()

        # Step-in
        step_force = self.get_step_force()

        if step_force > 0:
            direction = (
                self.player.opponent.position
                - self.player.position
            )

            self.player.apply_force(
                direction,
                step_force,
                0.1
            )

        self.attacking = True
        self.attack_angle = 0

        projectiles = []

        hero_stacks = self.get_hero_stacks()
        spread = math.radians(10)

        for i in range(hero_stacks):
            offset = (i - (hero_stacks - 1) / 2) * spread

            direction = self.direction.rotate_rad(offset)

            projectiles.append(
                MagicSlash(
                    self.player.position,
                    direction,
                    self.get_damage(),
                    self.player
                )
            )

        return projectiles

    def get_lifesteal(self):
        lifesteal = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Bloodlust":
                lifesteal += 0.50 * upgrade.stacks

        return lifesteal

    def get_blade_count(self):
        count = 1

        for upgrade in self.upgrades:
            if upgrade.name == "Dual Wielder":
                count += upgrade.stacks

        return count

    def get_blade_directions(self):
        blade_count = self.get_blade_count()

        directions = []

        for i in range(blade_count):
            angle = (
                self.angle
                + (math.tau / blade_count) * i
            )

            direction = pygame.Vector2(
                math.cos(angle),
                math.sin(angle)
            )

            directions.append(direction)

        return directions

    def trigger_beyblade(self):
        has_beyblade = False

        for upgrade in self.upgrades:
            if upgrade.name == "Beyblade":
                has_beyblade = True
                break

        if not has_beyblade:
            return

        self.cooldown_timer = 0

        self.beyblade_buffs.append(5.0)

    def get_hero_stacks(self):
        stacks = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Hero":
                stacks += upgrade.stacks

        return stacks

    def reset(self):
        super().reset()

        self.attacking = False
        self.attack_angle = 0
        self.hit_angle = self.hit_angle_cooldown

    def get_step_force(self):
        force = 0
        for upgrade in self.upgrades:
            if upgrade.name == "Step-in":
                force += 500 * upgrade.stacks

        return force

    def get_vortex_force(self):
        force = 0
        for upgrade in self.upgrades:
            if upgrade.name == "Vortex":
                force += 250 * upgrade.stacks

        return force

    