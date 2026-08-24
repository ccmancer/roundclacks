import pygame
import math

from entities.projectile import Projectile


class Arrow(Projectile):
    def __init__(
        self,
        position,
        direction,
        damage,
        owner,
        speed,
        size,
        pincushion_duration=0,
        pincushion_slow=0,
        knockback=0,
        homing_force=0,
        homing_range=0,
        bounces=0
    ):
        super().__init__(
            position,
            direction,
            speed,
            damage,
            owner,
            size,
            "arrow.png"
        )

        # -------------------------------------------------
        # Gameplay
        # -------------------------------------------------

        self.size = size
        self.radius = size

        self.pincushion_duration = (
            pincushion_duration
        )

        self.pincushion_slow = (
            pincushion_slow
        )

        self.knockback = knockback

        self.homing_force = homing_force
        self.homing_range = homing_range

        self.bounces_remaining = bounces

        # -------------------------------------------------
        # Pincushion
        # -------------------------------------------------

        self.stuck_to = None
        self.stick_timer = 0
        self.stick_offset = pygame.Vector2()

        # -------------------------------------------------
        # Sprite
        # -------------------------------------------------

        # Normal arrow:
        # size = 6
        # sprite = 80 x 80
        self.base_sprite_size = 80
        self.base_projectile_size = 6

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(self, dt):
        if self.stuck_to is not None:
            player = self.stuck_to

            self.position = (
                player.position
                + self.stick_offset
            )

            self.stick_timer -= dt

            if self.stick_timer <= 0:
                self.remove_pincushion()

            return

        self.apply_homing(dt)

        super().update(dt)

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

    def get_sprite_scale(self):
        return (
            self.size
            / self.base_projectile_size
        )

    def get_sprite_size(self):
        return (
            self.base_sprite_size
            * self.get_sprite_scale()
        )

    def get_sprite(self):
        size = max(
            1,
            int(self.get_sprite_size())
        )

        sprite = pygame.transform.scale(
            self.sprite,
            (
                size,
                size
            )
        )

        angle = math.degrees(
            math.atan2(
                self.direction.y,
                self.direction.x
            )
        )

        return pygame.transform.rotate(
            sprite,
            -angle
        )

    # -------------------------------------------------
    # HITBOX
    # -------------------------------------------------

    def get_hitbox_radius(self):
        return self.radius

    # -------------------------------------------------
    # PINCUSHION
    # -------------------------------------------------

    def is_pincushion_active_for(self, player):
        return (
            self.stuck_to is player
            and self.stick_timer > 0
            and self.pincushion_slow > 0
        )

    def get_pincushion_speed_multiplier(self):
        if not self.is_pincushion_active_for(
            self.stuck_to
        ):
            return 1

        return (
            1
            - self.pincushion_slow
        )

    def remove_pincushion(self):
        player = self.stuck_to

        self.stuck_to = None
        self.stick_timer = 0

        if player is not None:
            if self in player.pinned_arrows:
                player.pinned_arrows.remove(
                    self
                )

        self.alive = False

    # -------------------------------------------------
    # HIT
    # -------------------------------------------------

    def hit(self, player):
        if self.stuck_to is not None:
            return

        player.take_damage(
            self.damage
        )

        if self.knockback > 0:
            player.apply_force(
                self.direction,
                self.knockback,
                0.1
            )

        if self.pincushion_duration > 0:
            self.stuck_to = player

            self.stick_timer = (
                self.pincushion_duration
            )

            self.stick_offset = (
                self.position
                - player.position
            )

            if self not in player.pinned_arrows:
                player.pinned_arrows.append(
                    self
                )

        else:
            self.alive = False

    # -------------------------------------------------
    # BOUNDARY COLLISION
    # -------------------------------------------------

    def handle_boundary_collision(
        self,
        width,
        height
    ):
        if self.stuck_to is not None:
            return

        radius = (
            self.get_hitbox_radius()
        )

        bounced = False

        if self.position.x - radius <= 0:
            self.position.x = radius
            self.direction.x *= -1
            bounced = True

        elif self.position.x + radius >= width:
            self.position.x = width - radius
            self.direction.x *= -1
            bounced = True

        if self.position.y - radius <= 0:
            self.position.y = radius
            self.direction.y *= -1
            bounced = True

        elif self.position.y + radius >= height:
            self.position.y = height - radius
            self.direction.y *= -1
            bounced = True

        if not bounced:
            return

        if self.bounces_remaining > 0:
            self.bounces_remaining -= 1
        else:
            self.alive = False

    # -------------------------------------------------
    # HOMING
    # -------------------------------------------------

    def apply_homing(self, dt):
        if self.homing_force <= 0:
            return

        opponent = self.owner.opponent

        if opponent is None:
            return

        to_opponent = (
            opponent.position
            - self.position
        )

        distance = to_opponent.length()

        if distance == 0:
            return

        if distance > self.homing_range:
            return

        target_direction = (
            to_opponent.normalize()
        )

        current_angle = math.degrees(
            math.atan2(
                self.direction.y,
                self.direction.x
            )
        )

        target_angle = math.degrees(
            math.atan2(
                target_direction.y,
                target_direction.x
            )
        )

        angle_difference = (
            target_angle
            - current_angle
            + 180
        ) % 360 - 180

        max_turn = (
            self.homing_force * dt
        )

        turn = max(
            -max_turn,
            min(
                angle_difference,
                max_turn
            )
        )

        self.direction = pygame.Vector2(
            1,
            0
        ).rotate(
            current_angle + turn
        )