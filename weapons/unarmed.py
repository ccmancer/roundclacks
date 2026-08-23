import random

from weapons.weapon import Weapon
from upgrades.upgrade_pool import UNARMED_UPGRADES
from entities.fire_patch import FirePatch


class Unarmed(Weapon):
    def __init__(self, player):
        super().__init__(
            player,
            0,      # orbit distance
            0,      # rotation speed
            20,     # base damage
            0.75,   # base cooldown
            True
        )

        self.upgrade_pool = UNARMED_UPGRADES

        self.attack_timer = 0
        self.hit_players = set()

        # Distance-based hit reset.
        self.attack_distance = 0
        self.last_position = (
            self.player.position.copy()
        )
        self.hit_reset_distance = 50

        # PAC-MAN
        self.pacman_speed_stacks = 0

        # Tunnel Effect
        self.tunnel_speed_stacks = 0
        self.tunnel_contact_players = set()

        # Blazing Fast
        self.fire_trail_distance = 0
        self.last_fire_position = (
            self.player.position.copy()
        )
        self.spawned_entities = []

        # Instant Transmission
        self.meteor_speed_stacks = 0

        # TEMPORARY TEST
        for upgrade in self.upgrade_pool:
             if upgrade.name == "Instant Transmission":
                 self.add_upgrade(upgrade)
                 break

    def update(self, dt):
        # Clear entities after RoundState collects them.
        self.spawned_entities = []

        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt

        if self.attack_timer > 0:
            current_position = self.player.position

            # -----------------------------------------
            # Distance traveled during attack.
            # -----------------------------------------
            movement = (
                current_position
                - self.last_position
            )

            distance = movement.length()

            self.attack_distance += distance

            self.last_position = (
                current_position.copy()
            )

            # Reset normal hit list after enough movement.
            if (
                self.attack_distance
                >= self.hit_reset_distance
            ):
                self.hit_players.clear()
                self.attack_distance = 0

            # -----------------------------------------
            # Blazing Fast
            # -----------------------------------------
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

                # PAC-MAN
                self.pacman_speed_stacks = 0

                # Tunnel Effect
                self.tunnel_speed_stacks = 0
                self.tunnel_contact_players.clear()

                # Blazing Fast
                self.fire_trail_distance = 0
                self.last_fire_position = (
                    self.player.position.copy()
                )

                # Instant Transmission
                self.meteor_speed_stacks = 0

        else:
            self.last_position = (
                self.player.position.copy()
            )

            self.fire_trail_distance = 0
            self.last_fire_position = (
                self.player.position.copy()
            )

            self.tunnel_contact_players.clear()

    def draw(self, screen):
        pass

    def attack(self, width=None, height=None):
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

        # PAC-MAN
        self.pacman_speed_stacks = 0

        # Tunnel Effect
        self.tunnel_speed_stacks = 0
        self.tunnel_contact_players.clear()

        # Blazing Fast
        self.fire_trail_distance = 0
        self.last_fire_position = (
            self.player.position.copy()
        )

        # Instant Transmission
        self.meteor_speed_stacks = 0

        self.spawned_entities = []

        # Teleport immediately when the attack starts.
        if (
            self.is_meteor_combo()
            and width is not None
            and height is not None
        ):
            self.do_meteor_teleport(
                width,
                height
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

        # Tunnel Effect.
        if (
            self.is_tunnel_effect()
            and opponent
            not in self.tunnel_contact_players
        ):
            self.tunnel_contact_players.add(
                opponent
            )

            self.tunnel_speed_stacks += 1

    def get_damage(self):
        damage = self.base_damage

        for upgrade in self.upgrades:
            if upgrade.name == "Slugger":
                damage *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Cannonball":
                damage *= (
                    2 ** upgrade.stacks
                )

        # Momentum.
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

    def get_radius_multiplier(self):
        multiplier = 1

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

    def get_attack_duration(self):
        duration = 0.4

        for upgrade in self.upgrades:
            if upgrade.name == "Endurance":
                duration *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Marathon Runner":
                duration *= (
                    3 ** upgrade.stacks
                )

            elif upgrade.name == "Raging Demon":
                duration *= (
                    4 ** upgrade.stacks
                )

        return duration

    # -------------------------------------------------
    # PAC-MAN
    # -------------------------------------------------

    def get_pacman_speed_multiplier(self):
        pacman_stacks = 0

        for upgrade in self.upgrades:
            if upgrade.name == "PAC-MAN":
                pacman_stacks += upgrade.stacks

        return (
            1
            + 0.5
            * pacman_stacks
            * self.pacman_speed_stacks
        )

    # -------------------------------------------------
    # Tunnel Effect
    # -------------------------------------------------

    def is_tunnel_effect(self):
        for upgrade in self.upgrades:
            if upgrade.name == "Tunnel Effect":
                return True

        return False

    def get_tunnel_speed_multiplier(self):
        tunnel_upgrade_stacks = 0

        for upgrade in self.upgrades:
            if upgrade.name == "Tunnel Effect":
                tunnel_upgrade_stacks += upgrade.stacks

        return (
            1
            + 0.5
            * tunnel_upgrade_stacks
            * self.tunnel_speed_stacks
        )

    def on_tunnel_separation(self, opponent):
        self.tunnel_contact_players.discard(
            opponent
        )

    # -------------------------------------------------
    # Instant Transmission
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
        # +50% attacking movement speed per
        # Instant Transmission upgrade stack.
        return (
            1
            + 0.5
            * self.get_meteor_stacks()
        )

    def do_meteor_teleport(self, width, height):
        opponent = self.player.opponent

        if opponent is None:
            return

        margin = self.player.get_radius()

        self.player.position.x = random.uniform(
            margin,
            width - margin
        )

        self.player.position.y = random.uniform(
            margin,
            height - margin
        )

        # Face directly toward the opponent.
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
    # Speed
    # -------------------------------------------------

    def get_speed_multiplier(self):
        # Unarmed is naturally faster than other weapons.
        multiplier = 1.5

        for upgrade in self.upgrades:
            if upgrade.name == "Footwork":
                multiplier *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Marathon Runner":
                multiplier *= (
                    0.75 ** upgrade.stacks
                )

            elif upgrade.name == "Cannonball":
                multiplier *= (
                    0.75 ** upgrade.stacks
                )

        if not self.is_attacking():
            return multiplier

        # Base attack burst.
        multiplier *= 3

        for upgrade in self.upgrades:
            if upgrade.name == "Sprinter":
                multiplier *= (
                    2 ** upgrade.stacks
                )

            elif upgrade.name == "Raging Demon":
                multiplier *= (
                    8 ** upgrade.stacks
                )

        # PAC-MAN.
        multiplier *= (
            self.get_pacman_speed_multiplier()
        )

        # Tunnel Effect.
        multiplier *= (
            self.get_tunnel_speed_multiplier()
        )

        # Instant Transmission.
        multiplier *= (
            self.get_meteor_speed_multiplier()
        )

        return multiplier

    # -------------------------------------------------
    # Blazing Fast
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
        size = 20

        stacks = self.get_blazing_fast_stacks()

        size *= (
            1.5 ** stacks
        )

        return size

    def get_fire_duration(self):
        duration = 0.5

        stacks = self.get_blazing_fast_stacks()

        duration *= (
            1.5 ** stacks
        )

        return duration

    def get_fire_tick_interval(self):
        interval = 0.1

        stacks = self.get_blazing_fast_stacks()

        interval *= (
            0.5 ** stacks
        )

        return interval

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

            start_position = (
                patch_position
            )

            self.fire_trail_distance = 0

        self.fire_trail_distance += (
            remaining_distance
        )

        self.last_fire_position = (
            current_position.copy()
        )

    # -------------------------------------------------
    # Cooldown
    # -------------------------------------------------

    def get_attack_cooldown(self):
        downtime = self.base_cooldown

        for upgrade in self.upgrades:
            if upgrade.name == "Hyperactive":
                downtime *= (
                    0.5 ** upgrade.stacks
                )

            elif upgrade.name == "Raging Demon":
                downtime *= (
                    2 ** upgrade.stacks
                )

        return (
            self.get_attack_duration()
            + downtime
        )