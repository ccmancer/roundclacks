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
    return distance <= bullet.radius + player.radius
def check_sword_player_collision(sword, player):
    start = sword.player.position
    end = sword.position
    closest_point = start
    line = end - start
    line_length_squared = line.length_squared()
    if line_length_squared > 0:
        t = (player.position - start).dot(line) / line_length_squared
        t = max(0, min(1, t))
        closest_point = start + line * t
    distance = player.position.distance_to(closest_point)
    return distance <= player.radius + sword.width / 2