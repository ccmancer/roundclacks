import pygame

from game.states.state import State
from ui.button import Button


class NetplayLobbyState(State):

    def __init__(
        self,
        game,
        server=None,
        client=None,
        is_host=False,
        room_code=None,
        host_ip=None,
        host_port=None,
        awaiting_join=False
    ):
        super().__init__(
            game
        )

        self.server = server
        self.client = client

        self.is_host = is_host

        self.room_code = room_code
        self.host_ip = host_ip
        self.host_port = host_port

        self.awaiting_join = awaiting_join

        self.game.audio.play_music(
            "netplay"
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

        self.small_font = pygame.font.Font(
            None,
            22
        )

        # -------------------------------------------------
        # Back
        # -------------------------------------------------

        self.back_button = Button(
            "Back",
            (
                20,
                650,
                120,
                45
            ),
            font_size=25,
            audio=self.game.audio
        )

        # -------------------------------------------------
        # Lobby
        # -------------------------------------------------

        self.player2_connected = False
        self.weapon_select_started = False

        self.join_accepted = (
            not awaiting_join
        )

        # -------------------------------------------------
        # Opponent
        # -------------------------------------------------

        self.remote_name = "Opponent"

        self.remote_color = (
            100,
            100,
            100
        )

        # -------------------------------------------------
        # Host immediately sends identity.
        # -------------------------------------------------

        if self.join_accepted:

            self.send_player_info()

    # -------------------------------------------------
    # LOCAL NETPLAY IDENTITY
    # -------------------------------------------------

    def get_local_name(
        self
    ):
        return (
            self.game.settings.player1_name
        )

    def get_local_color(
        self
    ):
        return tuple(
            self.game.settings.player1_color
        )

    # -------------------------------------------------
    # SEND PLAYER INFO
    # -------------------------------------------------

    def send_player_info(
        self
    ):
        if self.client is None:
            return

        self.client.send(
            {
                "type": "player_info",
                "name": self.get_local_name(),
                "color": list(
                    self.get_local_color()
                )
            }
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

            if self.back_button.clicked(
                event
            ):

                self.close()

                return

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

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

        self.back_button.update(
            mouse_position
        )

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
            # Assignment
            # -------------------------------------------------

            if message_type == "assign_player":

                player = message.get(
                    "player"
                )

                if player in (
                    1,
                    2
                ):

                    self.client.player_number = (
                        player
                    )

            # -------------------------------------------------
            # Join accepted
            # -------------------------------------------------

            elif message_type == "join_accepted":

                self.join_accepted = True
                self.awaiting_join = False

                self.send_player_info()

            # -------------------------------------------------
            # Join rejected
            # -------------------------------------------------

            elif message_type == "join_rejected":

                reason = message.get(
                    "reason",
                    "Could not join room."
                )

                print(
                    "Join rejected:",
                    reason
                )

                self.close_connection_only()

                self.game.start_netplay()

                self.game.simulation_accumulator = 0

                return

            # -------------------------------------------------
            # Player count
            # -------------------------------------------------

            elif message_type == "player_count":

                count = message.get(
                    "count",
                    0
                )

                self.player2_connected = (
                    count >= 2
                )

            # -------------------------------------------------
            # Player info
            # -------------------------------------------------

            elif message_type == "player_info":

                player = message.get(
                    "player"
                )

                local_player = (
                    self.client.player_number
                )

                remote_player = (
                    2
                    if local_player == 1
                    else 1
                )

                if player != remote_player:
                    continue

                name = message.get(
                    "name"
                )

                color = message.get(
                    "color"
                )

                if isinstance(
                    name,
                    str
                ):

                    self.remote_name = name

                if (
                    isinstance(
                        color,
                        list
                    )
                    and len(color) == 3
                    and all(
                        isinstance(
                            value,
                            int
                        )
                        and 0 <= value <= 255
                        for value in color
                    )
                ):

                    self.remote_color = tuple(
                        color
                    )

            # -------------------------------------------------
            # Start weapon select
            # -------------------------------------------------

            elif message_type == "start_weapon_select":

                if self.weapon_select_started:
                    continue

                self.weapon_select_started = True

                self.game.start_netplay_weapon_select(
                    self.client,
                    is_host=self.is_host,
                    server=self.server
                )

                return

            # -------------------------------------------------
            # Opponent left
            # -------------------------------------------------

            elif message_type == "opponent_left":

                from game.states.opponent_left import (
                    OpponentLeftState
                )

                is_host = (
                    self.client.player_number
                    == 1
                )

                # -------------------------------------------------
                # Host keeps its client and server alive.
                # Guest closes its connection.
                # -------------------------------------------------

                if is_host:

                    self.game.state = OpponentLeftState(
                        self.game,
                        self.remote_name,
                        self.remote_color,
                        client=self.client,
                        is_host=True,
                        server=self.server
                    )

                else:

                    self.close_connection_only()

                    self.game.state = OpponentLeftState(
                        self.game,
                        self.remote_name,
                        self.remote_color,
                        client=None,
                        is_host=False,
                        server=None
                    )

                self.game.simulation_accumulator = 0

                return

    # -------------------------------------------------
    # CLOSE CONNECTION
    # -------------------------------------------------

    def close_connection_only(
        self
    ):
        if self.client is not None:

            self.client.leave_room()
            self.client = None

        if (
            self.is_host
            and self.server is not None
        ):

            self.server.stop()
            self.server = None

        self.game.netplay_server = None

    # -------------------------------------------------
    # CLOSE
    # -------------------------------------------------

    def close(
        self
    ):
        self.close_connection_only()

        self.game.return_to_main_menu()

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
        # TITLE
        # -------------------------------------------------

        title = self.title_font.render(
            "NETPLAY LOBBY",
            True,
            "black"
        )

        title_rect = title.get_rect(
            center=(
                screen_width // 2,
                55
            )
        )

        screen.blit(
            title,
            title_rect
        )

        # -------------------------------------------------
        # ROOM CODE
        # -------------------------------------------------

        if self.room_code is not None:

            room_label = self.small_font.render(
                "ROOM CODE",
                True,
                (90, 90, 90)
            )

            screen.blit(
                room_label,
                room_label.get_rect(
                    center=(
                        screen_width // 2,
                        100
                    )
                )
            )

            room = self.info_font.render(
                self.room_code,
                True,
                "black"
            )

            screen.blit(
                room,
                room.get_rect(
                    center=(
                        screen_width // 2,
                        135
                    )
                )
            )

        # -------------------------------------------------
        # HOST CONNECTION INFO
        # -------------------------------------------------

        if self.is_host:

            address_label = self.small_font.render(
                "HOST ADDRESS",
                True,
                (90, 90, 90)
            )

            screen.blit(
                address_label,
                address_label.get_rect(
                    center=(
                        screen_width // 2,
                        180
                    )
                )
            )

            address = self.info_font.render(
                str(
                    self.host_ip
                ),
                True,
                "black"
            )

            screen.blit(
                address,
                address.get_rect(
                    center=(
                        screen_width // 2,
                        215
                    )
                )
            )

            port_label = self.small_font.render(
                "PORT",
                True,
                (90, 90, 90)
            )

            screen.blit(
                port_label,
                port_label.get_rect(
                    center=(
                        screen_width // 2,
                        255
                    )
                )
            )

            port = self.info_font.render(
                str(
                    self.host_port
                ),
                True,
                "black"
            )

            screen.blit(
                port,
                port.get_rect(
                    center=(
                        screen_width // 2,
                        290
                    )
                )
            )

        # -------------------------------------------------
        # YOU
        # -------------------------------------------------

        local_name = (
            self.get_local_name()
        )

        local_color = (
            self.get_local_color()
        )

        local_y = (
            350
            if self.is_host
            else 250
        )

        local_text = self.info_font.render(
            local_name,
            True,
            local_color
        )

        screen.blit(
            local_text,
            local_text.get_rect(
                center=(
                    screen_width // 2,
                    local_y
                )
            )
        )

        local_label = self.small_font.render(
            "YOU",
            True,
            (90, 90, 90)
        )

        screen.blit(
            local_label,
            local_label.get_rect(
                center=(
                    screen_width // 2,
                    local_y + 35
                )
            )
        )

        # -------------------------------------------------
        # OPPONENT
        # -------------------------------------------------

        opponent_y = (
            440
            if self.is_host
            else 340
        )

        if self.player2_connected:

            opponent_text = self.info_font.render(
                self.remote_name,
                True,
                self.remote_color
            )

            screen.blit(
                opponent_text,
                opponent_text.get_rect(
                    center=(
                        screen_width // 2,
                        opponent_y
                    )
                )
            )

            opponent_label = self.small_font.render(
                "OPPONENT",
                True,
                (90, 90, 90)
            )

            screen.blit(
                opponent_label,
                opponent_label.get_rect(
                    center=(
                        screen_width // 2,
                        opponent_y + 35
                    )
                )
            )

        else:

            waiting_text = (
                "Verifying room..."
                if self.awaiting_join
                else
                "Waiting for opponent..."
            )

            waiting = self.info_font.render(
                waiting_text,
                True,
                (100, 100, 100)
            )

            screen.blit(
                waiting,
                waiting.get_rect(
                    center=(
                        screen_width // 2,
                        opponent_y
                    )
                )
            )

        # -------------------------------------------------
        # NETWORK ROLE
        # -------------------------------------------------

        role = (
            "HOST • NETWORK PLAYER 1"
            if self.is_host
            else
            "JOINED • NETWORK PLAYER 2"
        )

        role_y = (
            530
            if self.is_host
            else 435
        )

        role_text = self.small_font.render(
            role,
            True,
            "black"
        )

        screen.blit(
            role_text,
            role_text.get_rect(
                center=(
                    screen_width // 2,
                    role_y
                )
            )
        )

        # -------------------------------------------------
        # BACK
        # -------------------------------------------------

        self.back_button.draw(
            screen
        )