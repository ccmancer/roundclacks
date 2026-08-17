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