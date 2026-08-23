import pygame

from entities.nuke_pool import NukePool
from entities.earthlight_ray import EarthlightRay
from entities.chaos_blade import ChaosBlade


class Explosion:
    def __init__(
        self,
        position,
        radius,
        damage,
        knockback,
        owner,
        self_damage_multiplier=1,
        startup=0,
        shellshock_duration=0,
        pool_damage=0,
        pyromaniac_heal=0,
        earthlight_ray_damage=0,
        chaos_damage=0,
        chaos_size=0,
        duration=0.5
    ):
        self.position = pygame.Vector2(position)

        self.radius = radius

        self.damage = damage
        self.knockback = knockback
        self.owner = owner

        self.self_damage_multiplier = (
            self_damage_multiplier
        )

        self.startup_timer = startup

        self.shellshock_duration = (
            shellshock_duration
        )

        self.pool_damage = pool_damage
        self.pyromaniac_heal = pyromaniac_heal

        self.earthlight_ray_damage = (
            earthlight_ray_damage
        )

        self.chaos_damage = chaos_damage
        self.chaos_size = chaos_size

        self.duration = duration
        self.timer = duration

        self.alive = True
        self.can_hit_owner = True

        self.hit_players = set()
        self.spawned = False

    def update(self, dt):
        if self.startup_timer > 0:
            self.startup_timer -= dt
            return

        self.timer -= dt

        if self.timer <= 0:
            self.alive = False

    def draw(self, screen):
        if self.startup_timer > 0:
            pygame.draw.circle(
                screen,
                "red",
                self.position,
                int(self.radius),
                3
            )
            return

        pygame.draw.circle(
            screen,
            "orange",
            self.position,
            int(self.radius)
        )

        pygame.draw.circle(
            screen,
            "red",
            self.position,
            int(self.radius),
            4
        )

        inner_radius = max(
            1,
            int(self.radius * 0.35)
        )

        pygame.draw.circle(
            screen,
            "yellow",
            self.position,
            inner_radius
        )

    def hit(self, player):
        if self.startup_timer > 0:
            return []

        if player in self.hit_players:
            return []

        self.hit_players.add(player)

        damage = self.damage

        if player == self.owner:
            # Heal before applying self-damage.
            if self.pyromaniac_heal > 0:
                self.owner.heal(
                    self.damage
                    * self.pyromaniac_heal
                )

            damage *= self.self_damage_multiplier

        player.take_damage(
            damage
        )

        direction = (
            player.position
            - self.position
        )

        if direction.length_squared() > 0:
            player.apply_force(
                direction,
                self.knockback,
                0.2
            )

        if self.shellshock_duration > 0:
            player.apply_shellshock(
                self.shellshock_duration
            )

        return []

    def get_spawned_entities(self):
        if self.startup_timer > 0:
            return []

        if self.spawned:
            return []

        self.spawned = True

        spawned = []

        # Nuke pool
        if self.pool_damage > 0:
            spawned.append(
                NukePool(
                    self.position,
                    self.radius,
                    self.pool_damage,
                    self.owner
                )
            )

        # Earthlight Ray
        if self.earthlight_ray_damage > 0:
            opponent = self.owner.opponent

            direction = (
                opponent.position
                - self.position
            )

            if direction.length_squared() > 0:
                direction = direction.normalize()

                ray_position = (
                    self.position
                    + direction * 20
                )

                spawned.append(
                    EarthlightRay(
                        ray_position,
                        direction,
                        self.earthlight_ray_damage,
                        self.owner
                    )
                )
        if self.chaos_damage > 0:
            for angle in range(0, 360, 90):
                direction = pygame.Vector2(
                    1,
                    0
                ).rotate(angle)

                spawned.append(
                    ChaosBlade(
                        self.position,
                        direction,
                        self.radius*2,
                        self.chaos_damage,
                        self.owner,
                        self.chaos_size,
                        2,   # duration
                        180,    # rotation speed
                        250     # outward speed
                    )
                )

        return spawned