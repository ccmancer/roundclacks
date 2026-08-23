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
            size
        )

        self.size = size

        self.pincushion_duration = pincushion_duration
        self.pincushion_slow = pincushion_slow
        self.knockback = knockback

        self.homing_force = homing_force
        self.homing_range = homing_range

        self.bounces_remaining = bounces

        self.stuck_to = None
        self.stick_timer = 0
        self.stick_offset = pygame.Vector2()

    def update(self, dt):
        if self.stuck_to is not None:
            self.position = (
                self.stuck_to.position
                + self.stick_offset
            )

            self.stick_timer -= dt

            if self.stick_timer <= 0:
                if self in self.stuck_to.pinned_arrows:
                    self.stuck_to.pinned_arrows.remove(self)

                self.alive = False

            return

        self.apply_homing(dt)
        super().update(dt)

    def draw(self, screen):
        length = 25 + self.size * 2

        start = self.position
        end = (
            start
            + self.direction * length
        )

        # Arrow shaft
        pygame.draw.line(
            screen,
            "brown",
            start,
            end,
            max(2, int(self.size * 0.8))
        )

        # Arrowhead
        head_length = 8 + self.size
        head_width = 5 + self.size * 0.5

        perpendicular = pygame.Vector2(
            -self.direction.y,
            self.direction.x
        )

        tip = end

        left = (
            end
            - self.direction * head_length
            + perpendicular * head_width
        )

        right = (
            end
            - self.direction * head_length
            - perpendicular * head_width
        )

        pygame.draw.polygon(
            screen,
            "black",
            [tip, left, right]
        )

    def hit(self, player):
        if self.stuck_to is not None:
            return

        player.take_damage(self.damage)

        if self.knockback > 0:
            player.apply_force(
                self.direction,
                self.knockback,
                0.1
            )

        if self.pincushion_duration > 0:
            self.stuck_to = player

            self.stick_timer = self.pincushion_duration

            self.stick_offset = (
                self.position
                - player.position
            )

            player.pinned_arrows.append(self)

        else:
            self.alive = False

    def handle_boundary_collision(self, width, height):
        bounced = False

        if self.position.x - self.radius <= 0:
            self.position.x = self.radius
            self.direction.x *= -1
            bounced = True

        elif self.position.x + self.radius >= width:
            self.position.x = width - self.radius
            self.direction.x *= -1
            bounced = True

        if self.position.y - self.radius <= 0:
            self.position.y = self.radius
            self.direction.y *= -1
            bounced = True

        elif self.position.y + self.radius >= height:
            self.position.y = height - self.radius
            self.direction.y *= -1
            bounced = True

        if not bounced:
            return

        if self.bounces_remaining > 0:
            self.bounces_remaining -= 1
        else:
            self.alive = False

    def apply_homing(self, dt):
        if self.homing_force <= 0:
            return

        opponent = self.owner.opponent

        to_opponent = (
            opponent.position - self.position
        )

        distance = to_opponent.length()

        if distance == 0:
            return

        if distance > self.homing_range:
            return

        target_direction = to_opponent.normalize()

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
            target_angle - current_angle + 180
        ) % 360 - 180

        max_turn = self.homing_force * dt

        turn = max(
            -max_turn,
            min(angle_difference, max_turn)
        )

        self.direction = pygame.Vector2(
            1,
            0
        ).rotate(
            current_angle + turn
        )