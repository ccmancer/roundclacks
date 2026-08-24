def check_circle_collision(
    player1,
    player2
):
    distance = player1.position.distance_to(
        player2.position
    )

    return distance <= (
        player1.get_hitbox_radius()
        + player2.get_hitbox_radius()
    )


def resolve_circle_collision(
    player1,
    player2
):
    direction = (
        player2.position
        - player1.position
    )

    if direction.length_squared() == 0:
        return

    normal = direction.normalize()

    speed1 = player1.velocity.length()
    speed2 = player2.velocity.length()

    player1.velocity = -normal * speed1
    player2.velocity = normal * speed2


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


def closest_point_on_segment(
    point,
    start,
    end
):
    segment = end - start

    if segment.length_squared() == 0:
        return start

    t = (
        (point - start).dot(segment)
        / segment.length_squared()
    )

    t = max(
        0,
        min(1, t)
    )

    return start + segment * t


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