def check_circle_collision(player1, player2):
    distance = player1.position.distance_to(player2.position)
    return distance <= player1.radius + player2.radius
def resolve_circle_collision(player1, player2):
    direction = player2.position - player1.position
    if direction.length() == 0:
        return
    normal = direction.normalize()
    speed1 = player1.velocity.length()
    speed2 = player2.velocity.length()
    player1.velocity = -normal * speed1
    player2.velocity = normal * speed2
def check_bullet_player_collision(bullet, player):
    distance = bullet.position.distance_to(player.position)
    return distance <= bullet.radius + player.get_radius()
def check_sword_player_collision(sword, player):
    for direction in sword.get_blade_directions():

        start = sword.player.position

        end = (
            start
            + direction * sword.get_length()
        )

        closest_point = closest_point_on_segment(
            player.position,
            start,
            end
        )

        distance = player.position.distance_to(
            closest_point
        )

        if distance <= player.get_radius() + sword.width / 2:
            return True

    return False
def closest_point_on_segment(point, start, end):
    segment = end - start

    if segment.length_squared() == 0:
        return start

    t = (
        (point - start).dot(segment)
        / segment.length_squared()
    )

    t = max(0, min(1, t))

    return start + segment * t