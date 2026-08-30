import pygame
import random
import string
import socket

from game.states.state import State
from ui.button import Button

from network.server import GameServer
from network.client import GameClient

from game.states.netplay_lobby import (
    NetplayLobbyState
)


class NetplayState(State):

    PORT_START = 5000
    PORT_END = 5010

    def __init__(
        self,
        game
    ):
        super().__init__(
            game
        )

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

        self.input_font = pygame.font.Font(
            None,
            28
        )

        # -------------------------------------------------
        # Mode
        # -------------------------------------------------

        self.mode = "main"

        # -------------------------------------------------
        # Host
        # -------------------------------------------------

        self.server = None
        self.client = None

        self.room_code = None
        self.host_ip = self.get_local_ip()
        self.host_port = None

        # -------------------------------------------------
        # Join
        # -------------------------------------------------

        self.join_code = ""
        self.join_host = "127.0.0.1"
        self.join_port = "5000"

        self.join_error = ""

        self.active_input = None

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        self.host_button = Button(
            "Host Game",
            (
                210,
                400,
                300,
                60
            ),
            font_size=30,
            audio=self.game.audio
        )

        self.join_button = Button(
            "Join Game",
            (
                210,
                470,
                300,
                60
            ),
            font_size=30,
            audio=self.game.audio
        )

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

        self.host_back_button = Button(
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

        self.join_button_confirm = Button(
            "Join",
            (
                210,
                535,
                300,
                60
            ),
            font_size=30,
            audio=self.game.audio
        )

        self.join_back_button = Button(
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
    # LOCAL IP
    # -------------------------------------------------

    @staticmethod
    def get_local_ip():

        test_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        try:

            test_socket.connect(
                (
                    "8.8.8.8",
                    80
                )
            )

            return test_socket.getsockname()[0]

        except OSError:

            return "127.0.0.1"

        finally:

            test_socket.close()

    # -------------------------------------------------
    # ROOM CODE
    # -------------------------------------------------

    @staticmethod
    def generate_room_code():

        characters = (
            string.ascii_uppercase
            + string.digits
        )

        characters = (
            characters
            .replace("I", "")
            .replace("O", "")
            .replace("0", "")
            .replace("1", "")
        )

        return "".join(
            random.choice(
                characters
            )
            for _ in range(6)
        )

    # -------------------------------------------------
    # FIND AVAILABLE PORT
    # -------------------------------------------------

    @classmethod
    def find_available_port(
        cls
    ):
        for port in range(
            cls.PORT_START,
            cls.PORT_END + 1
        ):

            test_socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            try:

                test_socket.bind(
                    (
                        "0.0.0.0",
                        port
                    )
                )

                return port

            except OSError:

                pass

            finally:

                test_socket.close()

        return None

    # -------------------------------------------------
    # EVENTS
    # -------------------------------------------------

    def handle_events(
        self,
        events
    ):
        for event in events:

            if event.type == pygame.QUIT:

                self.cleanup_connections()

                self.game.running = False

                return

            # -------------------------------------------------
            # MAIN
            # -------------------------------------------------

            if self.mode == "main":

                if self.host_button.clicked(
                    event
                ):

                    self.host_game()

                    return

                if self.join_button.clicked(
                    event
                ):

                    self.mode = "join"

                    self.join_code = ""
                    self.join_host = self.get_local_ip()
                    self.join_port = "5000"
                    self.join_error = ""
                    self.active_input = "room"

                    return

                if self.back_button.clicked(
                    event
                ):

                    self.game.return_to_main_menu()

                    return

            # -------------------------------------------------
            # HOST
            # -------------------------------------------------

            elif self.mode == "host":

                if self.host_back_button.clicked(
                    event
                ):

                    self.cleanup_connections()

                    self.mode = "main"

                    return

            # -------------------------------------------------
            # JOIN
            # -------------------------------------------------

            elif self.mode == "join":

                if self.join_back_button.clicked(
                    event
                ):

                    self.active_input = None
                    self.mode = "main"
                    self.join_error = ""

                    return

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if event.button != 1:
                        continue

                    room_rect = pygame.Rect(
                        210,
                        270,
                        300,
                        50
                    )

                    host_rect = pygame.Rect(
                        210,
                        350,
                        300,
                        50
                    )

                    port_rect = pygame.Rect(
                        210,
                        430,
                        300,
                        50
                    )

                    if room_rect.collidepoint(
                        event.pos
                    ):

                        self.active_input = "room"

                    elif host_rect.collidepoint(
                        event.pos
                    ):

                        self.active_input = "host"

                    elif port_rect.collidepoint(
                        event.pos
                    ):

                        self.active_input = "port"

                    else:

                        self.active_input = None

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:

                        self.active_input = None
                        self.mode = "main"
                        self.join_error = ""

                        return

                    if event.key == pygame.K_BACKSPACE:

                        if self.active_input == "room":

                            self.join_code = (
                                self.join_code[:-1]
                            )

                        elif self.active_input == "host":

                            self.join_host = (
                                self.join_host[:-1]
                            )

                        elif self.active_input == "port":

                            self.join_port = (
                                self.join_port[:-1]
                            )

                        continue

                    if event.key == pygame.K_RETURN:

                        self.join_game()

                        continue

                    if self.active_input == "room":

                        if (
                            len(self.join_code) < 6
                            and event.unicode.isalnum()
                        ):

                            self.join_code += (
                                event.unicode.upper()
                            )

                    elif self.active_input == "host":

                        if (
                            event.unicode.isdigit()
                            or event.unicode == "."
                        ):

                            self.join_host += (
                                event.unicode
                            )

                    elif self.active_input == "port":

                        if event.unicode.isdigit():

                            if len(
                                self.join_port
                            ) < 5:

                                self.join_port += (
                                    event.unicode
                                )

                if self.join_button_confirm.clicked(
                    event
                ):

                    self.join_game()

                    return

    # -------------------------------------------------
    # HOST
    # -------------------------------------------------

    def host_game(
        self
    ):
        self.cleanup_connections()

        port = (
            self.find_available_port()
        )

        if port is None:

            print(
                "No available netplay ports "
                "between "
                f"{self.PORT_START} "
                f"and "
                f"{self.PORT_END}."
            )

            return

        room_code = (
            self.generate_room_code()
        )

        server = GameServer(
            port=port
        )

        server.room_code = (
            room_code
        )

        try:

            server.start()

        except OSError as error:

            print(
                "Could not start server:",
                error
            )

            return

        self.host_port = server.port

        client = GameClient()

        if not client.connect(
            "127.0.0.1",
            self.host_port
        ):

            server.stop()

            print(
                "Host could not connect "
                "to local server."
            )

            return

        self.server = server
        self.client = client

        # -------------------------------------------------
        # Persist host server at Game level.
        # -------------------------------------------------

        self.game.netplay_server = server

        self.room_code = room_code
        self.host_ip = self.get_local_ip()

        print(
            "Room code:",
            self.room_code
        )

        print(
            "Host IP:",
            self.host_ip
        )

        print(
            "Host port:",
            self.host_port
        )

        self.game.state = (
            NetplayLobbyState(
                self.game,
                server=self.server,
                client=self.client,
                is_host=True,
                room_code=self.room_code,
                host_ip=self.host_ip,
                host_port=self.host_port,
                awaiting_join=False
            )
        )

        self.game.simulation_accumulator = 0

    # -------------------------------------------------
    # JOIN
    # -------------------------------------------------

    def join_game(
        self
    ):
        room_code = (
            self.join_code.strip().upper()
        )

        host = (
            self.join_host.strip()
        )

        port_text = (
            self.join_port.strip()
        )

        self.join_error = ""

        if len(room_code) != 6:

            self.join_error = (
                "Room code must be 6 characters."
            )

            return

        if not host:

            self.join_error = (
                "Enter the host address."
            )

            return

        try:

            port = int(
                port_text
            )

        except ValueError:

            self.join_error = (
                "Port must be a number."
            )

            return

        if (
            port < 1
            or port > 65535
        ):

            self.join_error = (
                "Invalid port."
            )

            return

        client = GameClient()

        if not client.connect(
            host,
            port
        ):

            self.join_error = (
                "Could not connect to host."
            )

            return

        client.send(
            {
                "type": "join_room",
                "room_code": room_code
            }
        )

        self.client = client

        self.game.state = (
            NetplayLobbyState(
                self.game,
                client=client,
                is_host=False,
                room_code=room_code,
                host_ip=host,
                host_port=port,
                awaiting_join=True
            )
        )

        self.game.simulation_accumulator = 0

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(
        self,
        dt
    ):
        mouse_position = pygame.mouse.get_pos()

        self.host_button.update(
            mouse_position
        )

        self.join_button.update(
            mouse_position
        )

        self.back_button.update(
            mouse_position
        )

        self.host_back_button.update(
            mouse_position
        )

        self.join_button_confirm.update(
            mouse_position
        )

        self.join_back_button.update(
            mouse_position
        )

    # -------------------------------------------------
    # CLEANUP
    # -------------------------------------------------

    def cleanup_connections(
        self
    ):
        # -------------------------------------------------
        # Keep the server reference before destroying it.
        # -------------------------------------------------

        server = self.server

        if self.client is not None:

            self.client.close()
            self.client = None

        if server is not None:

            server.stop()

        self.server = None

        self.game.netplay_server = None

        self.room_code = None
        self.host_port = None

    # -------------------------------------------------
    # INPUT BOX
    # -------------------------------------------------

    def draw_input_box(
        self,
        screen,
        rect,
        value,
        label,
        active
    ):
        label_surface = self.small_font.render(
            label,
            True,
            "black"
        )

        label_rect = label_surface.get_rect(
            midleft=(
                rect.x,
                rect.y - 12
            )
        )

        screen.blit(
            label_surface,
            label_rect
        )

        pygame.draw.rect(
            screen,
            (245, 245, 245),
            rect
        )

        pygame.draw.rect(
            screen,
            (0, 0, 0)
            if active
            else (120, 120, 120),
            rect,
            2
        )

        text = self.input_font.render(
            value,
            True,
            "black"
        )

        text_rect = text.get_rect(
            midleft=(
                rect.x + 12,
                rect.centery
            )
        )

        screen.blit(
            text,
            text_rect
        )

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
        # MAIN
        # -------------------------------------------------

        if self.mode == "main":

            title = self.title_font.render(
                "NETPLAY",
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

            info = self.info_font.render(
                "Play online with another player",
                True,
                (100, 100, 100)
            )

            info_rect = info.get_rect(
                center=(
                    screen_width // 2,
                    200
                )
            )

            screen.blit(
                info,
                info_rect
            )

            self.host_button.draw(
                screen
            )

            self.join_button.draw(
                screen
            )

            self.back_button.draw(
                screen
            )

            return

        # -------------------------------------------------
        # HOST
        # -------------------------------------------------

        if self.mode == "host":

            title = self.title_font.render(
                "HOST GAME",
                True,
                "black"
            )

            title_rect = title.get_rect(
                center=(
                    screen_width // 2,
                    60
                )
            )

            screen.blit(
                title,
                title_rect
            )

            room_label = self.small_font.render(
                "ROOM CODE",
                True,
                (90, 90, 90)
            )

            room_label_rect = room_label.get_rect(
                center=(
                    screen_width // 2,
                    115
                )
            )

            screen.blit(
                room_label,
                room_label_rect
            )

            code = self.title_font.render(
                self.room_code or "------",
                True,
                "black"
            )

            code_rect = code.get_rect(
                center=(
                    screen_width // 2,
                    155
                )
            )

            screen.blit(
                code,
                code_rect
            )

            ip_label = self.small_font.render(
                "HOST ADDRESS",
                True,
                (90, 90, 90)
            )

            ip_label_rect = ip_label.get_rect(
                center=(
                    screen_width // 2,
                    210
                )
            )

            screen.blit(
                ip_label,
                ip_label_rect
            )

            ip_text = self.info_font.render(
                self.host_ip,
                True,
                "black"
            )

            ip_rect = ip_text.get_rect(
                center=(
                    screen_width // 2,
                    245
                )
            )

            screen.blit(
                ip_text,
                ip_rect
            )

            port_label = self.small_font.render(
                "PORT",
                True,
                (90, 90, 90)
            )

            port_label_rect = port_label.get_rect(
                center=(
                    screen_width // 2,
                    300
                )
            )

            screen.blit(
                port_label,
                port_label_rect
            )

            port_text = self.info_font.render(
                str(
                    self.host_port
                    if self.host_port is not None
                    else "-----"
                ),
                True,
                "black"
            )

            port_rect = port_text.get_rect(
                center=(
                    screen_width // 2,
                    335
                )
            )

            screen.blit(
                port_text,
                port_rect
            )

            waiting = self.info_font.render(
                "Waiting for opponent...",
                True,
                (100, 100, 100)
            )

            waiting_rect = waiting.get_rect(
                center=(
                    screen_width // 2,
                    420
                )
            )

            screen.blit(
                waiting,
                waiting_rect
            )

            self.host_back_button.draw(
                screen
            )

            return

        # -------------------------------------------------
        # JOIN
        # -------------------------------------------------

        if self.mode == "join":

            title = self.title_font.render(
                "JOIN GAME",
                True,
                "black"
            )

            title_rect = title.get_rect(
                center=(
                    screen_width // 2,
                    70
                )
            )

            screen.blit(
                title,
                title_rect
            )

            self.draw_input_box(
                screen,
                pygame.Rect(
                    210,
                    270,
                    300,
                    50
                ),
                self.join_code,
                "ROOM CODE",
                self.active_input == "room"
            )

            self.draw_input_box(
                screen,
                pygame.Rect(
                    210,
                    350,
                    300,
                    50
                ),
                self.join_host,
                "HOST ADDRESS",
                self.active_input == "host"
            )

            self.draw_input_box(
                screen,
                pygame.Rect(
                    210,
                    430,
                    300,
                    50
                ),
                self.join_port,
                "PORT",
                self.active_input == "port"
            )

            self.join_button_confirm.draw(
                screen
            )

            if self.join_error:

                error = self.small_font.render(
                    self.join_error,
                    True,
                    (180, 0, 0)
                )

                error_rect = error.get_rect(
                    center=(
                        screen_width // 2,
                        620
                    )
                )

                screen.blit(
                    error,
                    error_rect
                )

            else:

                hint = self.small_font.render(
                    "Enter room code, host address, and port",
                    True,
                    (100, 100, 100)
                )

                hint_rect = hint.get_rect(
                    center=(
                        screen_width // 2,
                        620
                    )
                )

                screen.blit(
                    hint,
                    hint_rect
                )

            self.join_back_button.draw(
                screen
            )