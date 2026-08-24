import pygame
from pathlib import Path

from entities.nuke_pool import NukePool
from entities.earthlight_ray import EarthlightRay
from entities.chaos_blade import ChaosBlade


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
        self.position = pygame.Vector2(
            position
        )

        # -------------------------------------------------
        # Gameplay
        # -------------------------------------------------

        self.radius = radius

        self.damage = damage
        self.knockback = knockback
        self.owner = owner

        self.self_damage_multiplier = (
            self_damage_multiplier
        )

        # Fuse / warning time.
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

        # Used to make sure the explosion sound only
        # plays once.
        self.sound_played = False

        # -------------------------------------------------
        # Sound
        # -------------------------------------------------

        self.explosion_sound = pygame.mixer.Sound(
            SOUND_FOLDER / "bomb_explosion.mp3"
        )

        # -------------------------------------------------
        # Sprites
        # -------------------------------------------------

        self.explosion_sprite = pygame.image.load(
            SPRITE_FOLDER / "explosion.png"
        ).convert_alpha()

        self.warning_sprite = pygame.image.load(
            SPRITE_FOLDER / "warning.png"
        ).convert_alpha()

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(self, dt):
        # -------------------------------------------------
        # Fuse / warning phase
        # -------------------------------------------------

        if self.startup_timer > 0:
            self.startup_timer -= dt

            if self.startup_timer <= 0:
                self.startup_timer = 0

                # Play explosion sound exactly when
                # the fuse finishes.
                if not self.sound_played:
                    self.explosion_sound.play()
                    self.sound_played = True

            return

        # -------------------------------------------------
        # Immediate explosion
        # -------------------------------------------------

        if not self.sound_played:
            self.explosion_sound.play()
            self.sound_played = True

        # -------------------------------------------------
        # Explosion lifetime
        # -------------------------------------------------

        self.timer -= dt

        if self.timer <= 0:
            self.timer = 0
            self.alive = False

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------

    def draw(self, screen):
        sprite_size = max(
            1,
            int(self.radius * 2)
        )

        if self.startup_timer > 0:
            sprite = self.warning_sprite
            alpha = 255

        else:
            sprite = self.explosion_sprite

            fade = max(
                0,
                min(
                    1,
                    self.timer / self.duration
                )
            )

            alpha = int(
                255 * fade
            )

        sprite = pygame.transform.scale(
            sprite,
            (
                sprite_size,
                sprite_size
            )
        )

        sprite = sprite.copy()

        sprite.set_alpha(
            alpha
        )

        rect = sprite.get_rect(
            center=self.position
        )

        screen.blit(
            sprite,
            rect
        )

    # -------------------------------------------------
    # HITBOX
    # -------------------------------------------------

    def get_hitbox_radius(self):
        return self.radius

    # -------------------------------------------------
    # HIT
    # -------------------------------------------------

    def hit(self, player):
        if self.startup_timer > 0:
            return []

        if player in self.hit_players:
            return []

        self.hit_players.add(player)

        damage = self.damage

        if player == self.owner:
            if self.pyromaniac_heal > 0:
                self.owner.heal(
                    self.damage
                    * self.pyromaniac_heal
                )

            damage *= (
                self.self_damage_multiplier
            )

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

    # -------------------------------------------------
    # SPAWNED ENTITIES
    # -------------------------------------------------

    def get_spawned_entities(self):
        if self.startup_timer > 0:
            return []

        if self.spawned:
            return []

        self.spawned = True

        spawned = []

        # Nuke Pool.
        if self.pool_damage > 0:
            spawned.append(
                NukePool(
                    self.position,
                    self.radius,
                    self.pool_damage,
                    self.owner
                )
            )

        # Earthlight Ray.
        if self.earthlight_ray_damage > 0:
            opponent = self.owner.opponent

            if opponent is not None:
                direction = (
                    opponent.position
                    - self.position
                )

                if direction.length_squared() > 0:
                    direction = (
                        direction.normalize()
                    )

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

        # Chaos Bomb.
        if self.chaos_damage > 0:
            for angle in range(
                0,
                360,
                90
            ):
                direction = pygame.Vector2(
                    1,
                    0
                ).rotate(angle)

                spawned.append(
                    ChaosBlade(
                        self.position,
                        direction,
                        self.radius * 2,
                        self.chaos_damage,
                        self.owner,
                        self.chaos_size,
                        2,
                        180,
                        250
                    )
                )

        return spawned