import pygame
import math
import random
from pathlib import Path

from weapons.weapon import Weapon
from entities.arrow import Arrow
from upgrades.upgrade_pool import BOW_UPGRADES
from entities.bear_trap import BearTrap


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


class Bow(Weapon):
    def __init__(self, player):
        super().__init__(
            player,
            50,
            3,
            20,
            2.0,          # 2 second base cooldown
            False,
            "bow.png",
            80,
            80
        )

        # -------------------------------------------------
        # Sprites
        # -------------------------------------------------

        self.primed_sprite = pygame.image.load(
            SPRITE_FOLDER / "bow_primed.png"
        ).convert_alpha()

        # -------------------------------------------------
        # Sound
        # -------------------------------------------------

        self.shoot_sound = pygame.mixer.Sound(
            SOUND_FOLDER / "bow_shoot.mp3"
        )

        # -------------------------------------------------
        # Upgrades
        # -------------------------------------------------

        self.upgrade_pool = BOW_UPGRADES

    # -------------------------------------------------
    # SPRITE
    # -------------------------------------------------

    def get_sprite_scale(self):
        scale = 1

        for upgrade in self.upgrades:
            if upgrade.name == "Greatbow":
                scale *= (
                    1.5 ** upgrade.stacks
                )

        return scale

    def get_sprite_length(self):
        return (
            self.base_sprite_length
            * self.get_sprite_scale()
        )

    def get_sprite_width(self):
        return (
            self.base_sprite_width
            * self.get_sprite_scale()
        )

    def get_sprite(self, angle=None):
        if self.can_attack():
            base_sprite = self.primed_sprite
        else:
            base_sprite = self.sprite

        length = max(
            1,
            int(self.get_sprite_length())
        )

        width = max(
            1,
            int(self.get_sprite_width())
        )

        sprite = pygame.transform.scale(
            base_sprite,
            (
                length,
                width
            )
        )

        if angle is None:
            angle = self.angle

        sprite = pygame.transform.rotate(
            sprite,
            -math.degrees(angle)
        )

        return self.apply_ready_glow(
            sprite,
            self.get_ready_glow_strength()
        )

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(self, dt):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt

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

    # -------------------------------------------------
    # ATTACK
    # -------------------------------------------------

    def attack(self):
        if not self.can_attack():
            return []

        self.start_cooldown()

        # Play once per successful shot.
        self.shoot_sound.play()

        projectiles = []

        count = self.get_projectile_count()

        if count > 1:
            spread = self.get_spread()

            for i in range(count):
                offset = (
                    i
                    - (count - 1) / 2
                ) * spread

                direction = (
                    self.direction.rotate(offset)
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

        else:
            spread = self.get_spread()

            offset = random.uniform(
                -spread,
                spread
            )

            direction = (
                self.direction.rotate(offset)
            )

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

        trap_duration = (
            self.get_bear_trap_duration()
        )

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

    # -------------------------------------------------
    # DAMAGE / STATS
    # -------------------------------------------------

    def get_damage(self):
        damage = self.base_damage

        for upgrade in self.upgrades:
            if upgrade.name == "Machinegun":
                damage *= (
                    0.5 ** upgrade.stacks
                )

            elif upgrade.name == "Pointiness":
                damage *= (
                    1.25 ** upgrade.stacks
                )

            elif upgrade.name == "Greatbow":
                damage *= (
                    2 ** upgrade.stacks
                )

            elif upgrade.name == "Sniper":
                damage *= (
                    2 ** upgrade.stacks
                )

            elif upgrade.name == "Heavy Arrows":
                damage *= (
                    2 ** upgrade.stacks
                )

            elif upgrade.name == "Shotgun":
                damage *= (
                    0.5 ** upgrade.stacks
                )

            elif upgrade.name == "MLG":
                damage *= (
                    5 ** upgrade.stacks
                )

        return damage

    def get_rotation_speed(self):
        speed = self.rotation_speed

        for upgrade in self.upgrades:
            if upgrade.name == "Aim Sensitivity":
                speed *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Sniper":
                speed *= (
                    0.75 ** upgrade.stacks
                )

            elif upgrade.name == "MLG":
                speed *= (
                    3 ** upgrade.stacks
                )

        return speed

    def get_attack_cooldown(self):
        cooldown = self.base_cooldown

        for upgrade in self.upgrades:
            if upgrade.name == "Machinegun":
                cooldown *= (
                    0.01 ** upgrade.stacks
                )

            elif upgrade.name == "Greatbow":
                cooldown *= (
                    2 ** upgrade.stacks
                )

            elif upgrade.name == "Sniper":
                cooldown *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Quickdraw":
                cooldown *= (
                    0.5 ** upgrade.stacks
                )

        return cooldown

    # -------------------------------------------------
    # PROJECTILES
    # -------------------------------------------------

    def get_projectile_speed(self):
        speed = 1000

        for upgrade in self.upgrades:
            if upgrade.name == "Aerodynamic":
                speed *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Sniper":
                speed *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Heavy Arrows":
                speed *= (
                    0.75 ** upgrade.stacks
                )

            elif upgrade.name == "MLG":
                speed *= (
                    2 ** upgrade.stacks
                )

        return speed

    def get_projectile_size(self):
        size = 6

        for upgrade in self.upgrades:
            if upgrade.name == "Greatbow":
                size *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Heavy Arrows":
                size *= (
                    1.5 ** upgrade.stacks
                )

        return size

    def get_projectile_count(self):
        count = 1

        for upgrade in self.upgrades:
            if upgrade.name == "Shotgun":
                count += (
                    5
                    * upgrade.stacks
                )

        return count

    def get_spread(self):
        spread = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Shotgun":
                spread += (
                    5
                    * upgrade.stacks
                )

            elif upgrade.name == "Machinegun":
                spread += (
                    10
                    * upgrade.stacks
                )

        return spread

    def get_recoil(self):
        recoil = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Lightweight":
                recoil += (
                    250
                    * upgrade.stacks
                )

        return recoil

    # -------------------------------------------------
    # EFFECTS
    # -------------------------------------------------

    def get_pincushion_duration(self):
        duration = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Pincushion":
                duration = (
                    5
                    * upgrade.stacks
                )

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
                force += (
                    250
                    * upgrade.stacks
                )

        return force

    def get_bear_trap_duration(self):
        duration = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Bear Trap":
                duration = (
                    5
                    * upgrade.stacks
                )

        return duration

    def get_homing_force(self):
        force = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Homing":
                force += (
                    250
                    * upgrade.stacks
                )

        return force

    def get_homing_range(self):
        range_ = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Homing":
                range_ = (
                    250
                    * upgrade.stacks
                )

        return range_

    def get_bounces(self):
        bounces = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Ricochet":
                bounces += (
                    5
                    * upgrade.stacks
                )

        return bounces