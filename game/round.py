from game.upgrade_pool import generate_upgrade_choices


class RoundManager:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2

        self.round_number = 1

        self.winner = None
        self.loser = None

        self.state = "fighting"

        self.upgrade_choices = []

    def check_round_end(self):
        if not self.player1.is_alive():
            self.winner = self.player2
            self.loser = self.player1
            return True

        if not self.player2.is_alive():
            self.winner = self.player1
            self.loser = self.player2
            return True

        return False

    def reset_round(self):
        self.round_number += 1

        self.player1.reset((150, 360))
        self.player2.reset((570, 360))

        self.winner = None
        self.loser = None

    def start_upgrade_selection(self):
        self.state = "upgrade_selection"

        self.upgrade_choices = generate_upgrade_choices(
            self.loser.weapon.upgrade_pool
        )