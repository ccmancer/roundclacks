import pygame
from entities.player import Player

from game.match import Match
from game.states.state import State
from game.states.round import RoundState


class MatchState(State):
    def __init__(self, game, player1_weapon, player2_weapon):
        super().__init__(game)

        self.player1 = Player(
            150,
            360,
            40,
            "red",
            375,
            player1_weapon,
            pygame.K_SPACE,
        )

        self.player2 = Player(
            570,
            360,
            40,
            "blue",
            375,
            player2_weapon,
            pygame.K_RETURN
        )

        self.player1.opponent = self.player2
        self.player2.opponent = self.player1

        self.match = Match(
            self.player1,
            self.player2
        )

        self.current_state = RoundState(self)

    def handle_events(self, events):
        self.current_state.handle_events(events)

    def update(self, dt):
        self.current_state.update(dt)

    def draw(self, screen):
        self.current_state.draw(screen)

    def round_finished(self, winner, loser):
        self.match.record_win(winner)

        if self.match.is_over():
            self.match_finished()
            return

        from game.states.upgrade_select import UpgradeSelectState

        self.current_state = UpgradeSelectState(
            self,
            loser
        )

    def upgrade_selected(self, upgrade):
        loser = self.current_state.loser

        loser.weapon.add_upgrade(upgrade)

        self.match.round_number += 1

        self.current_state = RoundState(self)

    def match_finished(self):
        print(
            "Match finished. Winner:",
            self.match.get_winner().color
        )