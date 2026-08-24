import random

import pygame

from weapons.weapon import Weapon
from upgrades.upgrade_pool import UNARMED_UPGRADES
from entities.fire_patch import FirePatch


class Unarmed(Weapon):
    def __init__(self, player):
        super().__init__(
            player,
            0,
            0,
            20,
            2.0,          # 2 second base cooldown
            True
        )

        self.upgrade_pool = UNARMED_UPGRADES

        self.attack_timer = 0
        self.hit_players = set()

        self.attack_distance = 0
        self.last_position = (
            self.player.position.copy()
        )
        self.hit_reset_distance = 50

        self.pacman_speed_stacks = 0

        self.tunnel_speed_stacks = 0
        self.tunnel_contact_players = set()

        self.fire_trail_distance = 0
        self.last_fire_position = (
            self.player.position.copy()
        )
        self.spawned_entities = []

        self.meteor_speed_stacks = 0

        self.afterimages = []
        self.afterimage_spacing = 15
        self.afterimage_distance = 0
        self.last_afterimage_position = (
            self.player.position.copy()
        )

        from upgrades.upgrade import Upgrade
        self.add_upgrade(
            Upgrade(
                "Blazing Fast",
                "Common",
                ""
            )
        )

    # -------------------------------------------------
    # UPDATE / DRAW
    # -------------------------------------------------

    def update(self, dt):
        super().update(dt)

        self.spawned_entities = []

        attacking = self.is_attacking()

        if attacking:
            current_position = (
                self.player.position
            )

            movement = (
                current_position
                - self.last_position
            )

            distance = movement.length()

            self.attack_distance += distance

            self.last_position = (
                current_position.copy()
            )

            if (
                self.attack_distance
                >= self.hit_reset_distance
            ):
                self.hit_players.clear()
                self.attack_distance = 0

            if self.has_blazing_fast():
                self.spawn_fire_trail(
                    current_position,
                    movement,
                    distance
                )

            self.attack_timer -= dt

            if self.attack_timer <= 0:
                self.attack_timer = 0

                self.hit_players.clear()
                self.attack_distance = 0

                self.pacman_speed_stacks = 0

                self.tunnel_speed_stacks = 0
                self.tunnel_contact_players.clear()

                self.fire_trail_distance = 0
                self.last_fire_position = (
                    self.player.position.copy()
                )

                self.meteor_speed_stacks = 0

                self.afterimage_distance = 0
                self.last_afterimage_position = (
                    self.player.position.copy()
                )

        else:
            self.last_position = (
                self.player.position.copy()
            )

            self.fire_trail_distance = 0
            self.last_fire_position = (
                self.player.position.copy()
            )

            self.tunnel_contact_players.clear()

            self.afterimage_distance = 0
            self.last_afterimage_position = (
                self.player.position.copy()
            )

        if attacking:
            self.update_afterimages()
        else:
            self.afterimage_distance = 0

        self.remove_expired_afterimages(dt)

    def draw_before_player(self, screen):
        for afterimage in self.afterimages:
            sprite = afterimage["sprite"].copy()

            sprite.set_alpha(
                afterimage["alpha"]
            )

            rect = sprite.get_rect(
                center=afterimage["position"]
            )

            screen.blit(
                sprite,
                rect
            )

    # -------------------------------------------------
    # PLAYER SPRITE
    # -------------------------------------------------

    def modify_player_sprite(self, sprite):
        return self.apply_ready_glow(
            sprite,
            self.get_ready_glow_strength()
        )

    # -------------------------------------------------
    # PLAYER INTERACTION
    # -------------------------------------------------

    def modify_incoming_damage(self, damage):
        damage = super().modify_incoming_damage(
            damage
        )

        if self.is_attacking():
            for upgrade in self.upgrades:
                if upgrade.name == "Superarmor":
                    damage *= (
                        0.5 ** upgrade.stacks
                    )

        return damage

    def handle_player_bounds(
        self,
        width,
        height
    ):
        if self.is_pacman_active():
            self.handle_pacman_bounds(
                width,
                height
            )
            return

        super().handle_player_bounds(
            width,
            height
        )

    # -------------------------------------------------
    # ATTACK
    # -------------------------------------------------

    def attack(
        self,
        width=None,
        height=None
    ):
        if not self.can_attack():
            return []

        self.start_cooldown()

        self.attack_timer = (
            self.get_attack_duration()
        )

        self.hit_players.clear()

        self.attack_distance = 0
        self.last_position = (
            self.player.position.copy()
        )

        self.pacman_speed_stacks = 0

        self.tunnel_speed_stacks = 0
        self.tunnel_contact_players.clear()

        self.fire_trail_distance = 0
        self.last_fire_position = (
            self.player.position.copy()
        )

        self.meteor_speed_stacks = 0

        self.spawned_entities = []

        self.afterimage_distance = 0
        self.last_afterimage_position = (
            self.player.position.copy()
        )

        if (
            self.is_meteor_combo()
            and width is not None
            and height is not None
        ):
            self.do_meteor_teleport(
                width,
                height
            )

            self.last_afterimage_position = (
                self.player.position.copy()
            )

        return []

    def is_attacking(self):
        return self.attack_timer > 0

    def can_hit(self, opponent):
        return (
            self.is_attacking()
            and opponent not in self.hit_players
        )

    def hit(self, opponent):
        if not self.can_hit(opponent):
            return

        self.hit_players.add(opponent)

        opponent.take_damage(
            self.get_damage()
        )

        if (
            self.is_tunnel_effect()
            and opponent
            not in self.tunnel_contact_players
        ):
            self.tunnel_contact_players.add(
                opponent
            )

            self.tunnel_speed_stacks += 1

    # -------------------------------------------------
    # DAMAGE
    # -------------------------------------------------

    def get_damage(self):
        damage = self.base_damage

        for upgrade in self.upgrades:
            if upgrade.name == "Slugger":
                damage *= 1.5 ** upgrade.stacks

            elif upgrade.name == "Cannonball":
                damage *= 2 ** upgrade.stacks

        for upgrade in self.upgrades:
            if upgrade.name == "Momentum":
                normal_attack_speed = (
                    self.player.speed
                    * 1.5
                    * 3
                )

                current_speed = (
                    self.player.get_speed()
                )

                speed_bonus = max(
                    0,
                    current_speed
                    / normal_attack_speed
                    - 1
                )

                damage *= (
                    1
                    + speed_bonus
                    * upgrade.stacks
                )

        return damage

    # -------------------------------------------------
    # PLAYER STATS
    # -------------------------------------------------

    def get_radius_multiplier(self):
        multiplier = (
            super().get_radius_multiplier()
        )

        for upgrade in self.upgrades:
            if upgrade.name == "Cannonball":
                multiplier *= (
                    1.25 ** upgrade.stacks
                )

            elif upgrade.name == "Brute":
                multiplier *= (
                    1.25 ** upgrade.stacks
                )

        return multiplier

    def get_speed_multiplier(self):
        multiplier = (
            super().get_speed_multiplier()
        )

        multiplier *= 1.5

        for upgrade in self.upgrades:
            if upgrade.name == "Footwork":
                multiplier *= 1.5 ** upgrade.stacks

            elif upgrade.name == "Marathon Runner":
                multiplier *= 0.75 ** upgrade.stacks

            elif upgrade.name == "Cannonball":
                multiplier *= 0.75 ** upgrade.stacks

        if not self.is_attacking():
            return multiplier

        multiplier *= 3

        for upgrade in self.upgrades:
            if upgrade.name == "Sprinter":
                multiplier *= 2 ** upgrade.stacks

            elif upgrade.name == "Raging Demon":
                multiplier *= 8 ** upgrade.stacks

        multiplier *= (
            self.get_pacman_speed_multiplier()
        )

        multiplier *= (
            self.get_tunnel_speed_multiplier()
        )

        multiplier *= (
            self.get_meteor_speed_multiplier()
        )

        return multiplier

    def get_attack_cooldown(self):
        downtime = self.base_cooldown

        for upgrade in self.upgrades:
            if upgrade.name == "Hyperactive":
                downtime *= 0.5 ** upgrade.stacks

            elif upgrade.name == "Raging Demon":
                downtime *= 2 ** upgrade.stacks

        return (
            self.get_attack_duration()
            + downtime
        )

    def get_attack_duration(self):
        duration = 0.4

        for upgrade in self.upgrades:
            if upgrade.name == "Endurance":
                duration *= 1.5 ** upgrade.stacks

            elif upgrade.name == "Marathon Runner":
                duration *= 3 ** upgrade.stacks

            elif upgrade.name == "Raging Demon":
                duration *= 4 ** upgrade.stacks

        return duration

    # -------------------------------------------------
    # PAC-MAN
    # -------------------------------------------------

    def is_pacman_active(self):
        if not self.is_attacking():
            return False

        for upgrade in self.upgrades:
            if upgrade.name == "PAC-MAN":
                return True

        return False

    def handle_pacman_bounds(
        self,
        width,
        height
    ):
        radius = (
            self.player.get_hitbox_radius()
        )

        wrapped = False

        if self.player.position.x + radius < 0:
            self.player.position.x = (
                width + radius
            )
            wrapped = True

        elif self.player.position.x - radius > width:
            self.player.position.x = -radius
            wrapped = True

        if self.player.position.y + radius < 0:
            self.player.position.y = (
                height + radius
            )
            wrapped = True

        elif self.player.position.y - radius > height:
            self.player.position.y = -radius
            wrapped = True

        if wrapped:
            self.pacman_speed_stacks += 1

    def get_pacman_speed_multiplier(self):
        stacks = 0

        for upgrade in self.upgrades:
            if upgrade.name == "PAC-MAN":
                stacks += upgrade.stacks

        return (
            1
            + 0.5
            * stacks
            * self.pacman_speed_stacks
        )

    # -------------------------------------------------
    # TUNNEL EFFECT
    # -------------------------------------------------

    def is_tunnel_effect(self):
        for upgrade in self.upgrades:
            if upgrade.name == "Tunnel Effect":
                return True

        return False

    def get_tunnel_speed_multiplier(self):
        stacks = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Tunnel Effect":
                stacks += upgrade.stacks

        return (
            1
            + 0.5
            * stacks
            * self.tunnel_speed_stacks
        )

    def on_tunnel_separation(self, opponent):
        self.tunnel_contact_players.discard(
            opponent
        )

    # -------------------------------------------------
    # INSTANT TRANSMISSION
    # -------------------------------------------------

    def is_meteor_combo(self):
        for upgrade in self.upgrades:
            if upgrade.name == "Instant Transmission":
                return True

        return False

    def get_meteor_stacks(self):
        stacks = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Instant Transmission":
                stacks += upgrade.stacks

        return stacks

    def get_meteor_speed_multiplier(self):
        return (
            1
            + 0.5
            * self.get_meteor_stacks()
        )

    def do_meteor_teleport(
        self,
        width,
        height
    ):
        opponent = self.player.opponent

        if opponent is None:
            return

        margin = (
            self.player.get_hitbox_radius()
        )

        self.player.position.x = random.uniform(
            margin,
            width - margin
        )

        self.player.position.y = random.uniform(
            margin,
            height - margin
        )

        direction = (
            opponent.position
            - self.player.position
        )

        if direction.length_squared() > 0:
            self.player.velocity = (
                direction.normalize()
                * self.player.get_speed()
            )

    # -------------------------------------------------
    # HIT / FIRE
    # -------------------------------------------------

    def has_blazing_fast(self):
        for upgrade in self.upgrades:
            if upgrade.name == "Blazing Fast":
                return True

        return False

    def get_blazing_fast_stacks(self):
        stacks = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Blazing Fast":
                stacks += upgrade.stacks

        return stacks

    def get_fire_damage(self):
        return 0.5

    def get_fire_size(self):
        return (
            20
            * 1.5
            ** self.get_blazing_fast_stacks()
        )

    def get_fire_duration(self):
        return (
            0.5
            * 1.5
            ** self.get_blazing_fast_stacks()
        )

    def get_fire_tick_interval(self):
        return (
            0.1
            * 0.5
            ** self.get_blazing_fast_stacks()
        )

    def get_fire_spacing(self):
        return 20

    def spawn_fire_trail(
        self,
        current_position,
        movement,
        distance
    ):
        if distance <= 0:
            return

        fire_spacing = (
            self.get_fire_spacing()
        )

        movement_direction = (
            movement.normalize()
        )

        remaining_distance = distance

        start_position = (
            self.last_fire_position.copy()
        )

        while (
            self.fire_trail_distance
            + remaining_distance
            >= fire_spacing
        ):
            needed_distance = (
                fire_spacing
                - self.fire_trail_distance
            )

            patch_position = (
                start_position
                + movement_direction
                * needed_distance
            )

            self.spawned_entities.append(
                FirePatch(
                    patch_position,
                    self.get_fire_damage(),
                    self.player,
                    self.get_fire_size(),
                    self.get_fire_duration(),
                    self.get_fire_tick_interval()
                )
            )

            remaining_distance -= (
                needed_distance
            )

            start_position = patch_position
            self.fire_trail_distance = 0

        self.fire_trail_distance += (
            remaining_distance
        )

        self.last_fire_position = (
            current_position.copy()
        )

    # -------------------------------------------------
    # AFTERIMAGES
    # -------------------------------------------------

    def update_afterimages(self):
        current_position = (
            self.player.position
        )

        movement = (
            current_position
            - self.last_afterimage_position
        )

        distance = movement.length()

        if distance <= 0:
            return

        self.afterimage_distance += distance

        movement_direction = (
            movement.normalize()
        )

        while (
            self.afterimage_distance
            >= self.afterimage_spacing
        ):
            overshoot = (
                self.afterimage_distance
                - self.afterimage_spacing
            )

            spawn_position = (
                current_position
                - movement_direction
                * overshoot
            )

            self.afterimages.append({
                "position": spawn_position.copy(),
                "sprite": self.player.get_sprite().copy(),
                "alpha": 140,
                "timer": 0.18
            })

            self.afterimage_distance -= (
                self.afterimage_spacing
            )

        self.last_afterimage_position = (
            current_position.copy()
        )

    def remove_expired_afterimages(self, dt):
        for afterimage in self.afterimages:
            afterimage["timer"] -= dt

            afterimage["alpha"] = max(
                0,
                int(
                    140
                    * (
                        afterimage["timer"]
                        / 0.18
                    )
                )
            )

        self.afterimages = [
            afterimage
            for afterimage in self.afterimages
            if afterimage["timer"] > 0
        ]

    # -------------------------------------------------
    # RESET
    # -------------------------------------------------

    def reset(self):
        super().reset()

        self.attack_timer = 0
        self.hit_players.clear()

        self.attack_distance = 0
        self.last_position = (
            self.player.position.copy()
        )

        self.pacman_speed_stacks = 0

        self.tunnel_speed_stacks = 0
        self.tunnel_contact_players.clear()

        self.fire_trail_distance = 0
        self.last_fire_position = (
            self.player.position.copy()
        )

        self.meteor_speed_stacks = 0

        self.spawned_entities = []

        self.afterimages = []
        self.afterimage_distance = 0
        self.last_afterimage_position = (
            self.player.position.copy()
        )