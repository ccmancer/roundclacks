# game/match.py


class Match:
    WINNING_SCORE = 5

    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2

        self.player1_wins = 0
        self.player2_wins = 0

        self.round_number = 1

    # -------------------------------------------------
    # SCORE
    # -------------------------------------------------

    def record_win(self, winner):
        if winner == self.player1:
            self.player1_wins += 1

        elif winner == self.player2:
            self.player2_wins += 1

    def is_over(self):
        return (
            self.player1_wins >= self.WINNING_SCORE
            or self.player2_wins >= self.WINNING_SCORE
        )

    def get_winner(self):
        if self.player1_wins >= self.WINNING_SCORE:
            return self.player1

        if self.player2_wins >= self.WINNING_SCORE:
            return self.player2

        return None

    # -------------------------------------------------
    # RESET
    # -------------------------------------------------

    def reset(self):
        self.player1_wins = 0
        self.player2_wins = 0
        self.round_number = 1

        # Completely remove previous upgrades.
        self.player1.weapon.upgrades.clear()
        self.player2.weapon.upgrades.clear()

        # Reset weapon state.
        self.player1.weapon.reset()
        self.player2.weapon.reset()

        # Reset players.
        self.player1.reset(
            (150, 360)
        )

        self.player2.reset(
            (570, 360)
        )