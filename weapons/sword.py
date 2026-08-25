import pygame
import math
from pathlib import Path

from weapons.weapon import Weapon
from upgrades.upgrade_pool import SWORD_UPGRADES
from entities.magic_slash import MagicSlash


SOUND_FOLDER = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "audio"
    / "game"
)


class Sword(Weapon):
    def __init__(self, player):
        super().__init__(
            player,
            100,    # orbit distance
            3,      # base rotation speed
            20,     # base damage
            2.0,    # base cooldown
            True,
            "sword.png",
            140,    # sprite length
            140     # sprite width
        )

        # -------------------------------------------------
        # Hitbox
        # -------------------------------------------------

        self.base_hitbox_length = 140
        self.base_hitbox_width = 32

        # -------------------------------------------------
        # Hit cooldown
        # -------------------------------------------------

        self.hit_angle_cooldown = math.radians(60)
        self.hit_angle = self.hit_angle_cooldown

        # -------------------------------------------------
        # Attack
        # -------------------------------------------------

        self.beyblade_buffs = []

        self.attacking = False
        self.attack_angle = 0

        self.base_attack_rotation_speed = 20

        # -------------------------------------------------
        # Sound
        # -------------------------------------------------

        self.swing_sound = self.player.game.audio.load_game_sound(
            SOUND_FOLDER / "sword_swing.mp3"
        )

        self.upgrade_pool = SWORD_UPGRADES

    # -------------------------------------------------
    # UPDATE / DRAW
    # -------------------------------------------------

    def update(self, dt):
        # -------------------------------------------------
        # Cooldown
        # -------------------------------------------------

        # Beyblade has no cooldown whatsoever.
        if self.has_beyblade():
            self.cooldown_timer = 0

        elif self.cooldown_timer > 0:
            self.cooldown_timer -= dt

            if self.cooldown_timer < 0:
                self.cooldown_timer = 0

        # -------------------------------------------------
        # Beyblade buffs
        # -------------------------------------------------

        self.beyblade_buffs = [
            timer - dt
            for timer in self.beyblade_buffs
            if timer - dt > 0
        ]

        # -------------------------------------------------
        # Attack
        # -------------------------------------------------

        if self.attacking:
            rotation_speed = (
                self.get_attack_rotation_speed()
            )

            self.angle += (
                rotation_speed * dt
            )

            self.attack_angle += (
                rotation_speed * dt
            )

            self.hit_angle += (
                rotation_speed * dt
            )

            if (
                self.attack_angle
                >= self.get_attack_total_angle()
            ):
                self.attacking = False
                self.attack_angle = 0

                # Beyblade never starts a cooldown.
                if not self.has_beyblade():
                    self.start_cooldown()

        # -------------------------------------------------
        # Normal orbit
        # -------------------------------------------------

        else:
            rotation_speed = (
                self.get_rotation_speed()
            )

            self.angle += (
                rotation_speed * dt
            )

            self.hit_angle += (
                rotation_speed * dt
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
        blade_count = self.get_blade_count()

        glow_strength = (
            self.get_ready_glow_strength()
        )

        for i in range(blade_count):
            angle = (
                self.angle
                + (
                    math.tau
                    / blade_count
                ) * i
            )

            direction = pygame.Vector2(
                math.cos(angle),
                math.sin(angle)
            )

            sprite = self.get_sprite(
                angle
            )

            sprite = self.apply_ready_glow(
                sprite,
                glow_strength
            )

            sprite_position = (
                self.player.position
                + direction
                * self.get_sprite_length()
                / 2
            )

            rect = sprite.get_rect(
                center=sprite_position
            )

            screen.blit(
                sprite,
                rect
            )

    # -------------------------------------------------
    # STATE
    # -------------------------------------------------

    def is_attacking(self):
        return self.attacking

    # -------------------------------------------------
    # HITBOX
    # -------------------------------------------------

    def get_hitbox_length(self):
        length = self.base_hitbox_length

        for upgrade in self.upgrades:
            if upgrade.name == "Longsword":
                length *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Greatsword":
                length *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Juggernaut":
                length *= (
                    1.5 ** upgrade.stacks
                )

        return length

    def get_hitbox_width(self):
        return self.base_hitbox_width

    # -------------------------------------------------
    # SPRITE
    # -------------------------------------------------

    def get_sprite_length(self):
        length = 140

        for upgrade in self.upgrades:
            if upgrade.name == "Longsword":
                length *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Greatsword":
                length *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Juggernaut":
                length *= (
                    1.5 ** upgrade.stacks
                )

        return length

    def get_sprite_width(self):
        width = 140

        for upgrade in self.upgrades:
            if upgrade.name == "Greatsword":
                width *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Juggernaut":
                width *= (
                    1.5 ** upgrade.stacks
                )

        return width

    # -------------------------------------------------
    # PLAYER STATS
    # -------------------------------------------------

    def get_speed_multiplier(self):
        multiplier = (
            super().get_speed_multiplier()
        )

        multiplier *= 1.25

        return multiplier

    # -------------------------------------------------
    # ATTACK
    # -------------------------------------------------

    def attack(self):
        if not self.can_attack():
            return []

        self.swing_sound.play()

        step_force = self.get_step_force()

        if step_force > 0:
            opponent = self.player.opponent

            if opponent is not None:
                direction = (
                    opponent.position
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
            offset = (
                i
                - (hero_stacks - 1) / 2
            ) * spread

            direction = (
                self.direction.rotate_rad(
                    offset
                )
            )

            projectile_position = (
                self.player.position
                + direction
                * self.get_sprite_length()
                / 2
            )

            projectiles.append(
                MagicSlash(
                    projectile_position,
                    direction,
                    self.get_damage(),
                    self.player
                )
            )

        return projectiles

    # -------------------------------------------------
    # DAMAGE / STATS
    # -------------------------------------------------

    def get_damage(self):
        damage = self.base_damage

        for upgrade in self.upgrades:
            if upgrade.name == "Sharpness":
                damage *= (
                    1.25 ** upgrade.stacks
                )

            elif upgrade.name == "Greatsword":
                damage *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Rage":
                missing_health = (
                    1
                    - self.player.get_health_ratio()
                )

                damage *= (
                    1
                    + missing_health
                    * upgrade.stacks
                    * 2
                )

            elif upgrade.name == "Hero":
                damage *= (
                    1.5 ** upgrade.stacks
                )

        return damage

    def get_rotation_speed(self):
        speed = self.rotation_speed

        for upgrade in self.upgrades:
            if upgrade.name == "Trained":
                speed *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Greatsword":
                speed *= (
                    0.75 ** upgrade.stacks
                )

            elif upgrade.name == "Beyblade":
                beyblade_stacks = len(
                    self.beyblade_buffs
                )

                if beyblade_stacks > 0:
                    speed *= (
                        1.25 ** beyblade_stacks
                    )

        return speed

    def get_attack_cooldown(self):
        # Beyblade has zero cooldown unconditionally.
        if self.has_beyblade():
            return 0

        cooldown = self.base_cooldown

        for upgrade in self.upgrades:
            if upgrade.name == "Hero":
                cooldown *= (
                    0.5 ** upgrade.stacks
                )

        return cooldown

    # -------------------------------------------------
    # ATTACK ROTATION
    # -------------------------------------------------

    def get_attack_rotation_speed(self):
        speed = (
            self.base_attack_rotation_speed
        )

        for upgrade in self.upgrades:
            if upgrade.name == "Trained":
                speed *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Double Spin":
                speed *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Greatsword":
                speed *= (
                    0.75 ** upgrade.stacks
                )

            elif upgrade.name == "Beyblade":
                beyblade_stacks = len(
                    self.beyblade_buffs
                )

                if beyblade_stacks > 0:
                    speed *= (
                        1.25 ** beyblade_stacks
                    )

        return speed

    def get_attack_total_angle(self):
        spins = 1

        for upgrade in self.upgrades:
            if upgrade.name == "Double Spin":
                spins += upgrade.stacks

        return math.tau * spins

    # -------------------------------------------------
    # PROJECTILE
    # -------------------------------------------------

    def get_projectile_speed(self):
        speed = 900

        for upgrade in self.upgrades:
            if upgrade.name == "Trained":
                speed *= (
                    1.5 ** upgrade.stacks
                )

        return speed

    # -------------------------------------------------
    # HIT
    # -------------------------------------------------

    def can_hit(self):
        return (
            self.hit_angle
            >= self.hit_angle_cooldown
        )

    def hit(self, player):
        self.hit_angle = 0

        # Beyblade's on-hit effect:
        # gain a temporary 25% spin-speed buff.
        self.trigger_beyblade()

        damage = self.get_damage()

        player.take_damage(
            damage
        )

        self.player.heal(
            self.get_lifesteal()
            * damage
        )

        vortex_force = (
            self.get_vortex_force()
        )

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

    # -------------------------------------------------
    # UPGRADE EFFECTS
    # -------------------------------------------------

    def has_beyblade(self):
        return any(
            upgrade.name == "Beyblade"
            for upgrade in self.upgrades
        )

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
                + (
                    math.tau
                    / blade_count
                ) * i
            )

            directions.append(
                pygame.Vector2(
                    math.cos(angle),
                    math.sin(angle)
                )
            )

        return directions

    def get_lifesteal(self):
        lifesteal = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Bloodlust":
                lifesteal += (
                    0.5
                    * upgrade.stacks
                )

        return lifesteal

    def trigger_beyblade(self):
        if not self.has_beyblade():
            return

        # Each Beyblade stack gives one buff per hit.
        stacks = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Beyblade":
                stacks += upgrade.stacks

        for _ in range(stacks):
            self.beyblade_buffs.append(5.0)

    def get_hero_stacks(self):
        stacks = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Hero":
                stacks += upgrade.stacks

        return stacks

    def get_step_force(self):
        force = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Step-in":
                force += (
                    500
                    * upgrade.stacks
                )

        return force

    def get_vortex_force(self):
        force = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Vortex":
                force += (
                    250
                    * upgrade.stacks
                )

        return force

    # -------------------------------------------------
    # RESET
    # -------------------------------------------------

    def reset(self):
        super().reset()

        self.attacking = False
        self.attack_angle = 0

        self.hit_angle = (
            self.hit_angle_cooldown
        )

        self.beyblade_buffs = []

        # Make absolutely sure a Beyblade sword
        # starts with zero cooldown.
        if self.has_beyblade():
            self.cooldown_timer = 0