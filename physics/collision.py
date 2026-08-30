import pygame


# -------------------------------------------------
# Collision constants
# -------------------------------------------------

COLLISION_EPSILON = 0.0001

ZERO_DISTANCE_EPSILON = 0.0000000001


# -------------------------------------------------
# Circle collision
# -------------------------------------------------

def check_circle_collision(
    player1,
    player2
):
    distance_squared = (
        player1.position
        - player2.position
    ).length_squared()

    radius_sum = (
        player1.get_hitbox_radius()
        + player2.get_hitbox_radius()
    )

    collision_distance = (
        radius_sum
        + COLLISION_EPSILON
    )

    return distance_squared <= (
        collision_distance
        * collision_distance
    )


def resolve_circle_collision(
    player1,
    player2
):
    direction = (
        player2.position
        - player1.position
    )

    distance_squared = (
        direction.length_squared()
    )

    radius_sum = (
        player1.get_hitbox_radius()
        + player2.get_hitbox_radius()
    )

    # -------------------------------------------------
    # Perfect / near-perfect overlap
    # -------------------------------------------------
    #
    # Always choose the same direction.
    # Never depend on Python object identity,
    # memory addresses, or randomness.
    # -------------------------------------------------

    if distance_squared <= ZERO_DISTANCE_EPSILON:

        normal = pygame.Vector2(
            1,
            0
        )

        distance = 0.0

    else:

        distance = (
            distance_squared ** 0.5
        )

        normal = (
            direction
            / distance
        )

    # -------------------------------------------------
    # Positional separation
    # -------------------------------------------------

    overlap = (
        radius_sum
        - distance
    )

    if overlap > 0:

        correction = (
            normal
            * (
                overlap / 2
            )
        )

        player1.position -= (
            correction
        )

        player2.position += (
            correction
        )

    # -------------------------------------------------
    # Relative velocity
    # -------------------------------------------------
    #
    # Only modify the component along the collision
    # normal.
    #
    # Tangential movement is preserved.
    # -------------------------------------------------

    relative_velocity = (
        player2.velocity
        - player1.velocity
    )

    normal_speed = (
        relative_velocity.dot(
            normal
        )
    )

    # Already separating.
    if normal_speed >= 0:
        return

    # -------------------------------------------------
    # Equal-mass elastic collision
    # -------------------------------------------------
    #
    # Each player keeps the tangential component while
    # the normal component is exchanged.
    # -------------------------------------------------

    player1_normal_velocity = (
        player1.velocity.dot(
            normal
        )
    )

    player2_normal_velocity = (
        player2.velocity.dot(
            normal
        )
    )

    player1_tangent = (
        player1.velocity
        - normal
        * player1_normal_velocity
    )

    player2_tangent = (
        player2.velocity
        - normal
        * player2_normal_velocity
    )

    player1.velocity = (
        player1_tangent
        + normal
        * player2_normal_velocity
    )

    player2.velocity = (
        player2_tangent
        + normal
        * player1_normal_velocity
    )

    # -------------------------------------------------
    # Restore each player's intended gameplay speed
    # -------------------------------------------------
    #
    # The collision changes direction but should not
    # accidentally destroy speed upgrades.
    # -------------------------------------------------

    speed1 = (
        player1.get_speed()
    )

    speed2 = (
        player2.get_speed()
    )

    if player1.velocity.length_squared() > 0:

        player1.velocity.scale_to_length(
            speed1
        )

    if player2.velocity.length_squared() > 0:

        player2.velocity.scale_to_length(
            speed2
        )


# -------------------------------------------------
# Sword collision
# -------------------------------------------------

def check_sword_player_collision(
    sword,
    player
):
    for direction in sword.get_blade_directions():

        start = sword.player.position

        end = (
            start
            + direction
            * sword.get_hitbox_length()
        )

        closest_point = closest_point_on_segment(
            player.position,
            start,
            end
        )

        distance = player.position.distance_to(
            closest_point
        )

        if distance <= (
            player.get_hitbox_radius()
            + sword.get_hitbox_width() / 2
        ):

            return True

    return False


# -------------------------------------------------
# Closest point
# -------------------------------------------------

def closest_point_on_segment(
    point,
    start,
    end
):
    segment = (
        end
        - start
    )

    if segment.length_squared() == 0:

        return start

    t = (
        (point - start).dot(segment)
        / segment.length_squared()
    )

    t = max(
        0,
        min(
            1,
            t
        )
    )

    return (
        start
        + segment * t
    )


# -------------------------------------------------
# Projectile collision
# -------------------------------------------------

def check_projectile_player_collision(
    projectile,
    player
):
    if (
        projectile.owner == player
        and not projectile.can_hit_owner
    ):

        return False

    distance = projectile.position.distance_to(
        player.position
    )

    return distance <= (
        projectile.get_hitbox_radius()
        + player.get_hitbox_radius()
    )


# -------------------------------------------------
# Beam collision
# -------------------------------------------------

def check_beam_player_collision(
    beam,
    player
):
    start = beam.position

    end = (
        beam.position
        + beam.direction
        * beam.get_hitbox_length()
    )

    closest_point = closest_point_on_segment(
        player.position,
        start,
        end
    )

    distance = player.position.distance_to(
        closest_point
    )

    return distance <= (
        beam.get_hitbox_width() / 2
        + player.get_hitbox_radius()
    )