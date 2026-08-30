import pygame

from game.states.state import State

from ui.button import Button


class OpponentLeftState(State):

    def __init__(
        self,
        game,
        opponent_name="Opponent",
        opponent_color=(100, 100, 100),
        client=None,
        is_host=False,
        server=None
    ):
        super().__init__(
            game
        )

        self.opponent_name = opponent_name
        self.opponent_color = opponent_color

        self.client = client
        self.is_host = is_host
        self.server = server

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
        # Button
        # -------------------------------------------------

        self.netplay_button = Button(
            "Netplay",
            (
                210,
                500,
                300,
                60
            ),
            font_size=30,
            audio=self.game.audio
        )

    # -------------------------------------------------
    # EVENTS
    # -------------------------------------------------

    def handle_events(
        self,
        events
    ):
        for event in events:

            if event.type == pygame.QUIT:

                self.close()

                self.game.running = False

                return

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    self.close()

                    return

            if self.netplay_button.clicked(
                event
            ):

                self.close()

                return

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(
        self,
        dt
    ):
        mouse_position = pygame.mouse.get_pos()

        self.netplay_button.update(
            mouse_position
        )

        # -------------------------------------------------
        # Only the host stays connected and waits for
        # another player.
        # -------------------------------------------------

        if not self.is_host:
            return

        if self.client is None:
            return

        messages = (
            self.client.update()
        )

        for message in messages:

            if not isinstance(
                message,
                dict
            ):
                continue

            message_type = message.get(
                "type"
            )

            # -------------------------------------------------
            # A new opponent joined.
            #
            # Import locally to avoid:
            #
            # netplay_weapon_select
            #     -> opponent_left
            #     -> netplay_weapon_select
            # -------------------------------------------------

            if message_type == "start_weapon_select":

                from game.states.netplay_weapon_select import (
                    NetplayWeaponSelectState
                )

                self.game.state = (
                    NetplayWeaponSelectState(
                        self.game,
                        self.client,
                        is_host=True,
                        server=self.server
                    )
                )

                self.game.simulation_accumulator = 0

                return

    # -------------------------------------------------
    # CLOSE
    # -------------------------------------------------

    def close(
        self
    ):
        # -------------------------------------------------
        # Tell the server this client is intentionally
        # leaving.
        # -------------------------------------------------

        if self.client is not None:

            self.client.leave_room()

            self.client = None

        # -------------------------------------------------
        # If this is the host, explicitly destroy the room.
        # -------------------------------------------------

        if self.is_host:

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
            "OPPONENT LEFT",
            True,
            "black"
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
        # Opponent
        # -------------------------------------------------

        opponent = self.info_font.render(
            self.opponent_name,
            True,
            self.opponent_color
        )

        opponent_rect = opponent.get_rect(
            center=(
                screen_width // 2,
                180
            )
        )

        screen.blit(
            opponent,
            opponent_rect
        )

        # -------------------------------------------------
        # Message
        # -------------------------------------------------

        if self.is_host:

            message_text = (
                "Waiting for another opponent..."
            )

        else:

            message_text = (
                "Your opponent has disconnected."
            )

        message = self.info_font.render(
            message_text,
            True,
            "black"
        )

        message_rect = message.get_rect(
            center=(
                screen_width // 2,
                250
            )
        )

        screen.blit(
            message,
            message_rect
        )

        # -------------------------------------------------
        # Netplay menu
        # -------------------------------------------------

        self.netplay_button.draw(
            screen
        )