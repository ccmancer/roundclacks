import pygame
import random

from entities.projectile import Projectile
from entities.explosion import Explosion


class BombProjectile(Projectile):
    def __init__(
        self,
        position,
        direction,
        damage,
        owner,
        speed,
        blast_radius=100,
        blast_knockback=500,
        self_damage_multiplier=1,
        fuse_time=0,
        mine_duration=0,
        cluster_count=0,
        cluster_child=False,
        pool_damage=0,
        pyromaniac_heal=0,
        shellshock_duration=0,
        earthlight_ray_damage=0,
        chaos_damage=0,
        chaos_size=0,
        cluster_delay=0.25,
        radius=10,
        gravity=700
    ):
        super().__init__(
            position,
            direction,
            speed,
            damage,
            owner,
            radius,
            "bomb.png"
        )

        self.velocity = (
            self.direction * speed
        )

        self.gravity = gravity

        self.blast_radius = blast_radius
        self.blast_knockback = blast_knockback

        self.self_damage_multiplier = (
            self_damage_multiplier
        )

        self.fuse_time = fuse_time

        # Mine.
        self.mine_duration = mine_duration
        self.mine_timer = mine_duration
        self.is_mine = (
            mine_duration > 0
        )
        self.stuck_to_border = False
        self.should_explode = False

        # Cluster Bomb.
        self.cluster_count = cluster_count
        self.cluster_child = cluster_child
        self.cluster_timer = cluster_delay

        # Nuke.
        self.pool_damage = pool_damage

        # Pyromaniac.
        self.pyromaniac_heal = pyromaniac_heal

        # Shellshock.
        self.shellshock_duration = (
            shellshock_duration
        )

        # Earthlight Ray.
        self.earthlight_ray_damage = (
            earthlight_ray_damage
        )

        # Chaos Bomb.
        self.chaos_damage = chaos_damage
        self.chaos_size = chaos_size

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(self, dt):
        if self.cluster_child:
            self.position += (
                self.velocity * dt
            )

            self.cluster_timer -= dt

            if self.cluster_timer <= 0:
                self.should_explode = True

            return

        if self.stuck_to_border:
            self.mine_timer -= dt

            opponent = self.owner.opponent

            if opponent is not None:
                distance = (
                    self.position.distance_to(
                        opponent.position
                    )
                )

                if distance <= (
                    self.blast_radius
                    + opponent.get_hitbox_radius()
                ):
                    self.should_explode = True

            if self.mine_timer <= 0:
                self.should_explode = True

            return

        self.velocity.y += (
            self.gravity * dt
        )

        self.position += (
            self.velocity * dt
        )

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------

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
    # SPRITE
    # -------------------------------------------------

    def get_sprite_length(self):
        if self.cluster_child:
            return 30

        return 60

    def get_sprite_width(self):
        if self.cluster_child:
            return 30

        return 60

    def get_sprite(self):
        return pygame.transform.scale(
            self.sprite,
            (
                int(self.get_sprite_length()),
                int(self.get_sprite_width())
            )
        )

    # -------------------------------------------------
    # HITBOX
    # -------------------------------------------------

    def get_hitbox_radius(self):
        return self.radius

    # -------------------------------------------------
    # BORDER
    # -------------------------------------------------

    def stick_to_border(
        self,
        width,
        height
    ):
        radius = (
            self.get_hitbox_radius()
        )

        distances = {
            "left": self.position.x,
            "right": width - self.position.x,
            "top": self.position.y,
            "bottom": height - self.position.y
        }

        border = min(
            distances,
            key=distances.get
        )

        if border == "left":
            self.position.x = radius

        elif border == "right":
            self.position.x = (
                width - radius
            )

        elif border == "top":
            self.position.y = radius

        elif border == "bottom":
            self.position.y = (
                height - radius
            )

        self.velocity = pygame.Vector2()
        self.stuck_to_border = True

    # -------------------------------------------------
    # EXPLOSION
    # -------------------------------------------------

    def explode(self):
        explosion = Explosion(
            self.position,
            self.blast_radius,
            self.damage,
            self.blast_knockback,
            self.owner,
            self.self_damage_multiplier,
            self.fuse_time,
            self.shellshock_duration,
            self.pool_damage,
            self.pyromaniac_heal,
            self.earthlight_ray_damage,
            self.chaos_damage,
            self.chaos_size
        )

        self.alive = False

        spawned = [
            explosion
        ]

        if (
            self.cluster_count > 0
            and not self.cluster_child
        ):
            for _ in range(
                self.cluster_count
            ):
                direction = pygame.Vector2(
                    1,
                    0
                ).rotate(
                    random.uniform(
                        0,
                        360
                    )
                )

                fragment_speed = random.uniform(
                    self.blast_radius * 2,
                    self.blast_radius * 4
                )

                fragment_delay = random.uniform(
                    0.15,
                    0.4
                )

                spawned.append(
                    BombProjectile(
                        self.position,
                        direction,
                        self.damage * 0.5,
                        self.owner,
                        fragment_speed,
                        self.blast_radius * 0.5,
                        self.blast_knockback,
                        self.self_damage_multiplier,
                        self.fuse_time,
                        0,
                        0,
                        True,
                        self.pool_damage,
                        self.pyromaniac_heal,
                        self.shellshock_duration,
                        self.earthlight_ray_damage,
                        self.chaos_damage,
                        self.chaos_size,
                        fragment_delay,
                        6,
                        0
                    )
                )

        return spawned

    # -------------------------------------------------
    # HIT
    # -------------------------------------------------

    def hit(self, player):
        if self.cluster_child:
            return []

        return self.explode()