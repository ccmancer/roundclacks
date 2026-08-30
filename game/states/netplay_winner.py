import pygame

from game.states.state import State
from game.states.opponent_left import OpponentLeftState
from game.states.netplay_weapon_select import (
    NetplayWeaponSelectState
)

from ui.button import Button


class NetplayWinnerState(State):

    def __init__(
        self,
        match_state,
        winner
    ):
        super().__init__(
            match_state.game
        )

        self.match_state = match_state
        self.winner = winner

        self.client = match_state.client
        self.server = match_state.server

        # -------------------------------------------------
        # Victory music
        # -------------------------------------------------

        self.game.audio.play_music(
            "victory"
        )

        # -------------------------------------------------
        # Fonts
        # -------------------------------------------------

        self.title_font = pygame.font.Font(
            None,
            55
        )

        self.info_font = pygame.font.Font(
            None,
            28
        )

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        self.rematch_button = Button(
            "Rematch",
            (
                210,
                500,
                300,
                60
            ),
            font_size=30,
            audio=self.game.audio
        )

        self.netplay_button = Button(
            "Netplay",
            (
                210,
                570,
                300,
                60
            ),
            font_size=30,
            audio=self.game.audio
        )

        # -------------------------------------------------
        # Rematch state
        # -------------------------------------------------

        self.rematch_requested = False
        self.opponent_rematch = False

    # -------------------------------------------------
    # EVENTS
    # -------------------------------------------------

    def handle_events(
        self,
        events
    ):
        for event in events:

            if event.type == pygame.QUIT:

                self.leave_netplay()

                self.game.running = False

                return

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    self.return_to_netplay()

                    return

            # -------------------------------------------------
            # Rematch
            # -------------------------------------------------

            if (
                not self.rematch_requested
                and self.rematch_button.clicked(
                    event
                )
            ):

                self.rematch_requested = True

                self.client.send(
                    {
                        "type": "rematch_request"
                    }
                )

                return

            # -------------------------------------------------
            # Netplay menu
            # -------------------------------------------------

            if self.netplay_button.clicked(
                event
            ):

                self.return_to_netplay()

                return

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(
        self,
        dt
    ):
        mouse_position = pygame.mouse.get_pos()

        self.rematch_button.update(
            mouse_position
        )

        self.netplay_button.update(
            mouse_position
        )

        if self.client is None:
            return

        messages = (
            self.client.update()
        )

        for message in messages:

            message_type = message.get(
                "type"
            )

            # -------------------------------------------------
            # Opponent left
            # -------------------------------------------------

            if message_type == "opponent_left":

                opponent = (
                    self.match_state.player2
                    if self.match_state.local_player_number == 1
                    else self.match_state.player1
                )

                is_host = (
                    self.match_state.local_player_number
                    == 1
                )

                # -------------------------------------------------
                # Host keeps the connection alive.
                # Guest no longer needs the connection.
                # -------------------------------------------------

                if not is_host:

                    self.client.close()

                self.game.state = (
                    OpponentLeftState(
                        self.game,
                        opponent.name,
                        opponent.color,
                        client=(
                            self.client
                            if is_host
                            else None
                        ),
                        is_host=is_host,
                        server=self.server
                    )
                )

                self.game.simulation_accumulator = 0

                return

            # -------------------------------------------------
            # My request accepted
            # -------------------------------------------------

            elif message_type == "rematch_accepted":

                self.rematch_requested = True

            # -------------------------------------------------
            # Opponent rematch
            # -------------------------------------------------

            elif message_type == "opponent_rematch":

                self.opponent_rematch = True

            # -------------------------------------------------
            # Both accepted
            # -------------------------------------------------

            elif message_type == "rematch_weapon_select":

                self.game.state = (
                    NetplayWeaponSelectState(
                        self.game,
                        self.client,
                        is_host=(
                            self.match_state.local_player_number
                            == 1
                        ),
                        server=self.server
                    )
                )

                self.game.simulation_accumulator = 0

                return

            # -------------------------------------------------
            # New opponent joined after one left.
            # -------------------------------------------------

            elif message_type == "start_weapon_select":

                self.game.state = (
                    NetplayWeaponSelectState(
                        self.game,
                        self.client,
                        is_host=(
                            self.match_state.local_player_number
                            == 1
                        ),
                        server=self.server
                    )
                )

                self.game.simulation_accumulator = 0

                return

    # -------------------------------------------------
    # LEAVE NETPLAY
    # -------------------------------------------------

    def leave_netplay(
        self
    ):
        is_host = (
            self.match_state.local_player_number
            == 1
        )

        if self.client is not None:

            self.client.leave_room()

            self.client = None

        if is_host:

            server = (
                self.server
                if self.server is not None
                else getattr(
                    self.game,
                    "netplay_server",
                    None
                )
            )

            if server is not None:

                server.stop()

            self.server = None
            self.game.netplay_server = None

        self.game.simulation_accumulator = 0

    # -------------------------------------------------
    # NETPLAY MENU
    # -------------------------------------------------

    def return_to_netplay(
        self
    ):
        self.leave_netplay()

        self.game.start_netplay()

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------

    def draw(
        self,
        screen
    ):
        screen.fill(
            "white"
        )

        screen_width = (
            screen.get_width()
        )

        # -------------------------------------------------
        # Title
        # -------------------------------------------------

        title = self.title_font.render(
            "WINNER!",
            True,
            self.winner.color
        )

        title_rect = title.get_rect(
            center=(
                screen_width // 2,
                100
            )
        )

        screen.blit(
            title,
            title_rect
        )

        # -------------------------------------------------
        # Winner
        # -------------------------------------------------

        winner_name = self.info_font.render(
            self.winner.name,
            True,
            self.winner.color
        )

        winner_name_rect = (
            winner_name.get_rect(
                center=(
                    screen_width // 2,
                    180
                )
            )
        )

        screen.blit(
            winner_name,
            winner_name_rect
        )

        # -------------------------------------------------
        # Score
        # -------------------------------------------------

        score = self.info_font.render(
            (
                f"{self.match_state.player1_wins}"
                f" - "
                f"{self.match_state.player2_wins}"
            ),
            True,
            "black"
        )

        score_rect = score.get_rect(
            center=(
                screen_width // 2,
                250
            )
        )

        screen.blit(
            score,
            score_rect
        )

        # -------------------------------------------------
        # Status
        # -------------------------------------------------

        if (
            self.rematch_requested
            and self.opponent_rematch
        ):

            status_text = (
                "Starting rematch..."
            )

        elif self.rematch_requested:

            status_text = (
                "Waiting for opponent..."
            )

        elif self.opponent_rematch:

            status_text = (
                "Opponent wants a rematch!"
            )

        else:

            status_text = ""

        if status_text:

            status = self.info_font.render(
                status_text,
                True,
                "black"
            )

            status_rect = status.get_rect(
                center=(
                    screen_width // 2,
                    330
                )
            )

            screen.blit(
                status,
                status_rect
            )

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        self.rematch_button.draw(
            screen
        )

        self.netplay_button.draw(
            screen
        )