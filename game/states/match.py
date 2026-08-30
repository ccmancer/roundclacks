import pygame

from entities.player import Player

from game.match import Match
from game.states.state import State
from game.states.upgrade_select import UpgradeSelectState
from game.states.round import RoundState
from game.states.winner import WinnerState


class MatchState(State):

    def __init__(
        self,
        game,
        player1_weapon,
        player2_weapon
    ):
        super().__init__(
            game
        )

        self.game.audio.play_music(
            "match"
        )

        settings = game.settings

        # -------------------------------------------------
        # Players
        # -------------------------------------------------

        self.player1 = Player(
            self.game,
            150,
            360,
            40,
            settings.player1_color,
            375,
            player1_weapon,
            pygame.K_SPACE,
            settings.player1_name
        )

        self.player2 = Player(
            self.game,
            570,
            360,
            40,
            settings.player2_color,
            375,
            player2_weapon,
            pygame.K_RETURN,
            settings.player2_name
        )

        self.player1.opponent = (
            self.player2
        )

        self.player2.opponent = (
            self.player1
        )

        # -------------------------------------------------
        # Match
        # -------------------------------------------------

        self.match = Match(
            self.player1,
            self.player2
        )

        # -------------------------------------------------
        # Deterministic simulation metadata
        # -------------------------------------------------

        self.player1.match = (
            self.match
        )

        self.player2.match = (
            self.match
        )

        self.player1.player_number = 1
        self.player2.player_number = 2

        self.player1.simulation_frame = 0
        self.player2.simulation_frame = 0

        # -------------------------------------------------
        # Starting upgrades
        # -------------------------------------------------

        self.starting_upgrade_player = 1

        # Explicitly initialize random namespace to round 1.
        self.match.set_round(
            1
        )

        self.current_state = (
            UpgradeSelectState(
                self,
                self.player1
            )
        )

    # -------------------------------------------------
    # STATE
    # -------------------------------------------------

    def handle_events(
        self,
        events
    ):
        self.current_state.handle_events(
            events
        )

    def update(
        self,
        dt
    ):
        self.current_state.update(
            dt
        )

    def draw(
        self,
        screen
    ):
        self.current_state.draw(
            screen
        )

    # -------------------------------------------------
    # ROUND
    # -------------------------------------------------

    def round_finished(
        self,
        winner,
        loser
    ):
        self.match.record_win(
            winner
        )

        if self.match.is_over():

            self.match_finished()

            return

        # -------------------------------------------------
        # The next upgrade belongs to the loser.
        #
        # round_number still refers to the round that just
        # finished here. It is advanced when that upgrade
        # is actually selected.
        # -------------------------------------------------

        self.current_state = (
            UpgradeSelectState(
                self,
                loser
            )
        )

    # -------------------------------------------------
    # UPGRADE SELECTION
    # -------------------------------------------------

    def upgrade_selected(
        self,
        upgrade
    ):
        # -------------------------------------------------
        # Initial P1 upgrade
        # -------------------------------------------------

        if self.starting_upgrade_player == 1:

            self.player1.weapon.add_upgrade(
                upgrade
            )

            self.starting_upgrade_player = 2

            self.current_state = (
                UpgradeSelectState(
                    self,
                    self.player2
                )
            )

            return

        # -------------------------------------------------
        # Initial P2 upgrade
        # -------------------------------------------------

        if self.starting_upgrade_player == 2:

            self.player2.weapon.add_upgrade(
                upgrade
            )

            self.starting_upgrade_player = None

            # First playable round is round 1.
            self.match.set_round(
                1
            )

            self.current_state = (
                RoundState(
                    self
                )
            )

            return

        # -------------------------------------------------
        # Later-round upgrade
        # -------------------------------------------------

        loser = (
            self.current_state.loser
        )

        loser.weapon.add_upgrade(
            upgrade
        )

        # -------------------------------------------------
        # Advance the deterministic random namespace.
        #
        # Before this call:
        #     round_number = round just completed
        #
        # After this call:
        #     round_number = new round
        # -------------------------------------------------

        self.match.round_number += 1

        self.match.set_round(
            self.match.round_number
        )

        self.current_state = (
            RoundState(
                self
            )
        )

    # -------------------------------------------------
    # MATCH END
    # -------------------------------------------------

    def match_finished(
        self
    ):
        winner = (
            self.match.get_winner()
        )

        self.current_state = (
            WinnerState(
                self,
                winner
            )
        )