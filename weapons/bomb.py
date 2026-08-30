import pygame

from game.asset_helper import load_image

from weapons.weapon import Weapon
from entities.bomb_projectile import BombProjectile
from upgrades.upgrade_pool import BOMB_UPGRADES


class Bomb(Weapon):
    def __init__(self, player):
        super().__init__(
            player,
            50,
            3,
            25,
            2.0,
            False,
            "bomb.png",
            60,
            60
        )

        self.missing_sprite = load_image(
            "sprites",
            "game",
            "bomb_missing.png"
        )

        self.throw_sound = self.player.game.audio.load_game_sound(
            "bomb_throw.mp3"
        )

        self.upgrade_pool = BOMB_UPGRADES

    # -------------------------------------------------
    # SPRITE
    # -------------------------------------------------

    def get_sprite(self):
        if self.can_attack():
            base_sprite = self.sprite
        else:
            base_sprite = self.missing_sprite

        sprite = pygame.transform.scale(
            base_sprite,
            (
                int(self.get_sprite_length()),
                int(self.get_sprite_width())
            )
        )

        return self.apply_ready_glow(
            sprite,
            self.get_ready_glow_strength()
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
    # ATTACK
    # -------------------------------------------------

    def attack(self):
        if not self.can_attack():
            return []

        self.start_cooldown()

        self.throw_sound.play()

        spread = self.get_spread()

        offset = (
            self.player.match.random.uniform(
                self.player.simulation_frame,
                self.player.player_number,
                "bomb_spread",
                -spread,
                spread
            )
        )

        direction = (
            self.direction.rotate(offset)
        )

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

    # -------------------------------------------------
    # DAMAGE / COOLDOWN
    # -------------------------------------------------

    def get_damage(self):
        damage = self.base_damage

        for upgrade in self.upgrades:
            if upgrade.name == "Lethality":
                damage *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Fuse":
                damage *= (
                    1.75 ** upgrade.stacks
                )

            elif upgrade.name == "Direct Hit":
                damage *= (
                    2 ** upgrade.stacks
                )

            elif upgrade.name == "Nuke":
                damage *= (
                    2 ** upgrade.stacks
                )

        return damage

    def get_attack_cooldown(self):
        cooldown = self.base_cooldown

        for upgrade in self.upgrades:
            if upgrade.name == "Madness":
                cooldown *= (
                    0.1 ** upgrade.stacks
                )

            elif upgrade.name == "Nuke":
                cooldown *= (
                    2 ** upgrade.stacks
                )

        return cooldown

    # -------------------------------------------------
    # PROJECTILE
    # -------------------------------------------------

    def get_initial_momentum(self):
        momentum = 500

        for upgrade in self.upgrades:
            if upgrade.name == "Fastball":
                momentum *= (
                    2 ** upgrade.stacks
                )

        return momentum

    def get_spread(self):
        spread = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Madness":
                spread += (
                    20
                    * upgrade.stacks
                )

        return spread

    # -------------------------------------------------
    # EXPLOSION
    # -------------------------------------------------

    def get_blast_radius(self):
        radius = 75

        for upgrade in self.upgrades:
            if upgrade.name == "Gunpowder":
                radius *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Fuse":
                radius *= (
                    1.75 ** upgrade.stacks
                )

            elif upgrade.name == "Direct Hit":
                radius *= (
                    0.75 ** upgrade.stacks
                )

            elif upgrade.name == "Nuke":
                radius *= (
                    2 ** upgrade.stacks
                )

        return radius

    def get_blast_knockback(self):
        knockback = 500

        for upgrade in self.upgrades:
            if upgrade.name == "Extra Force":
                knockback *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Fuse":
                knockback *= (
                    1.75 ** upgrade.stacks
                )

        return knockback

    # -------------------------------------------------
    # SPECIAL EFFECTS
    # -------------------------------------------------

    def get_fuse_time(self):
        fuse_time = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Fuse":
                fuse_time += (
                    0.5
                    * upgrade.stacks
                )

        return fuse_time

    def get_self_damage_multiplier(self):
        pyromaniac_stacks = 0
        professional_stacks = 0
        madness_stacks = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Pyromaniac":
                pyromaniac_stacks += upgrade.stacks

            elif upgrade.name == "Professional":
                professional_stacks += upgrade.stacks

            elif upgrade.name == "Madness":
                madness_stacks += upgrade.stacks

        if pyromaniac_stacks > 0:
            return 0

        multiplier = 1

        if professional_stacks > 0:
            multiplier *= (
                0.5 ** professional_stacks
            )

        if madness_stacks > 0:
            multiplier *= (
                1.5 ** madness_stacks
            )

        return multiplier

    def get_shellshock_duration(self):
        duration = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Shellshock":
                duration = (
                    5
                    * upgrade.stacks
                )

        return duration

    def get_mine_duration(self):
        duration = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Mine":
                duration = (
                    5
                    * upgrade.stacks
                )

        return duration

    def get_cluster_count(self):
        count = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Cluster Bomb":
                count += (
                    8
                    * upgrade.stacks
                )

        return count

    # -------------------------------------------------
    # PYROMANIAC
    # -------------------------------------------------

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

        if stacks > 0:
            stacks += self.get_professional_stacks()

        return stacks

    def get_pyromaniac_heal(self):
        return (
            0.5
            * self.get_pyromaniac_stacks()
        )

    # -------------------------------------------------
    # NUKES / CHAOS
    # -------------------------------------------------

    def get_pool_damage(self):
        damage = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Nuke":
                damage = upgrade.stacks

        return damage

    def get_earthlight_ray_damage(self):
        damage = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Earthlight Ray":
                damage = (
                    self.get_damage()
                    * 0.5
                    * 2 ** (
                        upgrade.stacks - 1
                    )
                )

        return damage

    def get_chaos_damage(self):
        damage = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Chaos Bomb":
                damage = (
                    self.get_damage()
                    * 0.5
                    * 2 ** (
                        upgrade.stacks - 1
                    )
                )

        return damage

    def get_chaos_size(self):
        return (
            self.get_blast_radius()
            * 0.5
        )