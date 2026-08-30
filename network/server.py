import socket
import threading

from network.protocol import (
    BUFFER_SIZE,
    encode_message,
    decode_messages
)


class GameServer:

    MAX_PLAYERS = 2

    def __init__(
        self,
        host="0.0.0.0",
        port=5000
    ):
        self.host = host

        # -------------------------------------------------
        # Requested port.
        #
        # If port == 0, the OS chooses one.
        # -------------------------------------------------

        self.requested_port = port
        self.port = port

        self.socket = None
        self.running = False

        self.clients = {}
        self.client_buffers = {}

        self.lock = threading.Lock()

        # -------------------------------------------------
        # Lobby
        # -------------------------------------------------

        self.room_code = None
        self.authenticated_players = set()
        self.weapon_select_started = False

        # -------------------------------------------------
        # Player
        # -------------------------------------------------

        self.player_info = {
            1: None,
            2: None
        }

        self.weapon_choices = {
            1: None,
            2: None
        }

        self.ready_players = set()

        # -------------------------------------------------
        # Match
        # -------------------------------------------------

        self.match_seed = None

        self.player1_wins = 0
        self.player2_wins = 0

        self.round_number = 1

        self.round_result_received = False

        # -------------------------------------------------
        # Upgrade
        # -------------------------------------------------

        self.upgrade_selector = None
        self.upgrade_selections = {}
        self.upgrade_phase_active = False

        # -------------------------------------------------
        # Input
        # -------------------------------------------------

        self.input_history = {
            1: {},
            2: {}
        }

        # -------------------------------------------------
        # Rematch
        # -------------------------------------------------

        self.rematch_requests = set()

    # -------------------------------------------------
    # RESET MATCH STATE
    # -------------------------------------------------

    def reset_match_state(
        self
    ):
        self.weapon_select_started = False

        self.weapon_choices = {
            1: None,
            2: None
        }

        self.ready_players.clear()

        self.match_seed = None

        self.player1_wins = 0
        self.player2_wins = 0

        self.round_number = 1

        self.round_result_received = False

        self.upgrade_selector = None
        self.upgrade_selections = {}
        self.upgrade_phase_active = False

        self.input_history = {
            1: {},
            2: {}
        }

        self.rematch_requests.clear()

    # -------------------------------------------------
    # START
    # -------------------------------------------------

    def start(
        self
    ):
        if self.running:
            return

        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        try:

            self.socket.bind(
                (
                    self.host,
                    self.requested_port
                )
            )

        except OSError:

            try:
                self.socket.close()
            except OSError:
                pass

            self.socket = None

            raise

        # -------------------------------------------------
        # Save actual bound port.
        # -------------------------------------------------

        self.port = (
            self.socket.getsockname()[1]
        )

        self.socket.listen(
            self.MAX_PLAYERS
        )

        self.socket.settimeout(
            0.5
        )

        self.running = True

        print(
            f"Server listening on "
            f"{self.host}:{self.port}"
        )

        threading.Thread(
            target=self.accept_loop,
            daemon=True
        ).start()

    # -------------------------------------------------
    # ACCEPT
    # -------------------------------------------------

    def accept_loop(
        self
    ):
        while self.running:

            try:

                client_socket, address = (
                    self.socket.accept()
                )

            except socket.timeout:

                continue

            except OSError:

                break

            with self.lock:

                if not self.running:

                    try:
                        client_socket.close()
                    except OSError:
                        pass

                    continue

                if len(
                    self.clients
                ) >= self.MAX_PLAYERS:

                    try:
                        client_socket.close()
                    except OSError:
                        pass

                    continue

                if 1 not in self.clients:

                    player_number = 1

                else:

                    player_number = 2

                self.clients[
                    player_number
                ] = client_socket

                self.client_buffers[
                    player_number
                ] = b""

                self.player_info[
                    player_number
                ] = None

                self.weapon_choices[
                    player_number
                ] = None

                self.ready_players.discard(
                    player_number
                )

                if player_number == 1:

                    self.authenticated_players.add(
                        player_number
                    )

                else:

                    self.authenticated_players.discard(
                        player_number
                    )

            print(
                f"Player {player_number} connected "
                f"from {address}"
            )

            self.send_to_player(
                player_number,
                {
                    "type": "assign_player",
                    "player": player_number
                }
            )

            self.broadcast_player_count()

            threading.Thread(
                target=self.client_loop,
                args=(
                    player_number,
                    client_socket
                ),
                daemon=True
            ).start()

    # -------------------------------------------------
    # CLIENT LOOP
    # -------------------------------------------------

    def client_loop(
        self,
        player_number,
        client_socket
    ):
        while self.running:

            try:

                data = client_socket.recv(
                    BUFFER_SIZE
                )

                if not data:
                    break

                with self.lock:

                    if self.clients.get(
                        player_number
                    ) is not client_socket:

                        break

                    self.client_buffers[
                        player_number
                    ] += data

                    messages, remaining = (
                        decode_messages(
                            self.client_buffers[
                                player_number
                            ]
                        )
                    )

                    self.client_buffers[
                        player_number
                    ] = remaining

                for message in messages:

                    self.handle_message(
                        player_number,
                        message
                    )

            except OSError:

                break

        self.disconnect_player(
            player_number,
            client_socket
        )

    # -------------------------------------------------
    # PLAYER COUNT
    # -------------------------------------------------

    def broadcast_player_count(
        self
    ):
        with self.lock:

            count = len(
                self.authenticated_players
            )

        self.broadcast(
            {
                "type": "player_count",
                "count": count
            }
        )

    # -------------------------------------------------
    # CHECK LOBBY
    # -------------------------------------------------

    def check_lobby_ready(
        self
    ):
        with self.lock:

            if not self.running:
                return

            if self.weapon_select_started:
                return

            if len(
                self.authenticated_players
            ) != 2:
                return

            if (
                self.player_info[1] is None
                or self.player_info[2] is None
            ):

                return

            self.weapon_select_started = True

            player1_info = dict(
                self.player_info[1]
            )

            player2_info = dict(
                self.player_info[2]
            )

        print(
            "LOBBY READY: both players connected."
        )

        self.broadcast(
            {
                "type": "start_weapon_select",
                "player1_info": player1_info,
                "player2_info": player2_info
            }
        )

    # -------------------------------------------------
    # MESSAGES
    # -------------------------------------------------

    def handle_message(
        self,
        player_number,
        message
    ):
        if not isinstance(
            message,
            dict
        ):
            return

        message_type = message.get(
            "type"
        )

        # -------------------------------------------------
        # PING
        # -------------------------------------------------

        if message_type == "ping":

            self.send_to_player(
                player_number,
                {
                    "type": "pong"
                }
            )

        # -------------------------------------------------
        # LEAVE ROOM
        # -------------------------------------------------

        elif message_type == "leave_room":

            self.disconnect_player(
                player_number,
                graceful=True
            )

        # -------------------------------------------------
        # JOIN ROOM
        # -------------------------------------------------

        elif message_type == "join_room":

            if player_number != 2:
                return

            room_code = message.get(
                "room_code"
            )

            if not isinstance(
                room_code,
                str
            ):
                return

            room_code = (
                room_code.strip().upper()
            )

            if (
                self.room_code is None
                or room_code != self.room_code
            ):

                print(
                    "Rejected Player 2:",
                    "invalid room code",
                    room_code,
                    "expected",
                    self.room_code,
                    "on port",
                    self.port
                )

                self.send_to_player(
                    player_number,
                    {
                        "type": "join_rejected",
                        "reason": "Invalid room code."
                    }
                )

                return

            with self.lock:

                if not self.running:
                    return

                self.authenticated_players.add(
                    player_number
                )

            print(
                "Player 2 authenticated."
            )

            self.send_to_player(
                player_number,
                {
                    "type": "join_accepted"
                }
            )

            self.broadcast_player_count()

            self.check_lobby_ready()

        # -------------------------------------------------
        # PLAYER INFO
        # -------------------------------------------------

        elif message_type == "player_info":

            with self.lock:

                if player_number not in (
                    self.authenticated_players
                ):

                    return

            name = message.get(
                "name"
            )

            color = message.get(
                "color"
            )

            if not isinstance(
                name,
                str
            ):
                return

            if (
                not isinstance(
                    color,
                    list
                )
                or len(color) != 3
                or not all(
                    isinstance(
                        value,
                        int
                    )
                    and 0 <= value <= 255
                    for value in color
                )
            ):
                return

            self.player_info[
                player_number
            ] = {
                "name": name,
                "color": list(color)
            }

            self.broadcast(
                {
                    "type": "player_info",
                    "player": player_number,
                    "name": name,
                    "color": list(color)
                }
            )

            self.check_lobby_ready()

        # -------------------------------------------------
        # WEAPON
        # -------------------------------------------------

        elif message_type == "weapon_select":

            if not self.weapon_select_started:
                return

            weapon = message.get(
                "weapon"
            )

            if not isinstance(
                weapon,
                str
            ):
                return

            self.weapon_choices[
                player_number
            ] = weapon

            self.broadcast(
                {
                    "type": "weapon_state",
                    "player": player_number,
                    "weapon": weapon
                }
            )

        # -------------------------------------------------
        # READY
        # -------------------------------------------------

        elif message_type == "ready":

            if not self.weapon_select_started:
                return

            if self.weapon_choices[
                player_number
            ] is None:
                return

            self.ready_players.add(
                player_number
            )

            self.broadcast(
                {
                    "type": "ready_state",
                    "player": player_number,
                    "ready": True
                }
            )

            if (
                len(self.ready_players) == 2
                and self.weapon_choices[1] is not None
                and self.weapon_choices[2] is not None
            ):

                self.start_match()

        # -------------------------------------------------
        # UPGRADE
        # -------------------------------------------------

        elif message_type == "upgrade_select":

            upgrade = message.get(
                "upgrade"
            )

            round_number = message.get(
                "round"
            )

            if not isinstance(
                upgrade,
                str
            ):
                return

            if not isinstance(
                round_number,
                int
            ):
                return

            if not self.upgrade_phase_active:
                return

            if round_number != self.round_number:
                return

            if player_number != self.upgrade_selector:
                return

            if player_number in self.upgrade_selections:
                return

            self.upgrade_selections[
                player_number
            ] = upgrade

            self.broadcast(
                {
                    "type": "upgrade_reveal",
                    "round": self.round_number,
                    "player": player_number,
                    "upgrade": upgrade,
                    "initial": (
                        self.round_number == 1
                    )
                }
            )

            if self.round_number == 1:

                if player_number == 1:

                    self.upgrade_selector = 2

                    self.broadcast(
                        {
                            "type": "start_upgrade_select",
                            "round": 1,
                            "player": 2,
                            "initial": True
                        }
                    )

                else:

                    self.upgrade_phase_active = False
                    self.upgrade_selector = None
                    self.upgrade_selections = {}

                    self.broadcast(
                        {
                            "type": "start_round",
                            "round": 1
                        }
                    )

            else:

                self.upgrade_phase_active = False
                self.upgrade_selector = None
                self.upgrade_selections = {}

                self.broadcast(
                    {
                        "type": "start_round",
                        "round": self.round_number
                    }
                )

        # -------------------------------------------------
        # ROUND FINISHED
        # -------------------------------------------------

        elif message_type == "round_finished":

            winner = message.get(
                "winner"
            )

            round_number = message.get(
                "round"
            )

            if winner not in (
                1,
                2
            ):
                return

            if not isinstance(
                round_number,
                int
            ):
                return

            if round_number != self.round_number:
                return

            if self.round_result_received:
                return

            self.round_result_received = True

            if winner == 1:

                self.player1_wins += 1
                loser = 2

            else:

                self.player2_wins += 1
                loser = 1

            match_over = (
                self.player1_wins >= 5
                or self.player2_wins >= 5
            )

            self.broadcast(
                {
                    "type": "round_result",
                    "round": self.round_number,
                    "winner": winner,
                    "loser": loser,
                    "player1_wins": self.player1_wins,
                    "player2_wins": self.player2_wins,
                    "match_over": match_over
                }
            )

            if match_over:
                return

            self.round_number += 1

            self.round_result_received = False

            self.upgrade_phase_active = True
            self.upgrade_selector = loser
            self.upgrade_selections = {}

            self.broadcast(
                {
                    "type": "start_upgrade_select",
                    "round": self.round_number,
                    "player": loser,
                    "initial": False
                }
            )

        # -------------------------------------------------
        # INPUT
        # -------------------------------------------------

        elif message_type == "input":

            frame = message.get(
                "frame"
            )

            attack = message.get(
                "attack"
            )

            if not isinstance(
                frame,
                int
            ):
                return

            if not isinstance(
                attack,
                bool
            ):
                return

            if frame < 0:
                return

            self.input_history[
                player_number
            ][frame] = {
                "frame": frame,
                "attack": attack
            }

            self.broadcast(
                {
                    "type": "input",
                    "player": player_number,
                    "frame": frame,
                    "attack": attack
                }
            )

        # -------------------------------------------------
        # REMATCH
        # -------------------------------------------------

        elif message_type == "rematch_request":

            if len(
                self.authenticated_players
            ) != 2:
                return

            if player_number in self.rematch_requests:
                return

            self.rematch_requests.add(
                player_number
            )

            other_player = (
                2
                if player_number == 1
                else 1
            )

            self.send_to_player(
                player_number,
                {
                    "type": "rematch_accepted"
                }
            )

            self.send_to_player(
                other_player,
                {
                    "type": "opponent_rematch"
                }
            )

            if len(
                self.rematch_requests
            ) == 2:

                self.weapon_choices = {
                    1: None,
                    2: None
                }

                self.ready_players.clear()

                self.match_seed = None

                self.player1_wins = 0
                self.player2_wins = 0

                self.round_number = 1

                self.round_result_received = False

                self.upgrade_selector = None
                self.upgrade_selections = {}
                self.upgrade_phase_active = False

                self.input_history = {
                    1: {},
                    2: {}
                }

                self.rematch_requests.clear()

                self.weapon_select_started = True

                self.broadcast(
                    {
                        "type": "rematch_weapon_select"
                    }
                )

    # -------------------------------------------------
    # START MATCH
    # -------------------------------------------------

    def start_match(
        self
    ):
        import random

        self.match_seed = random.randrange(
            0,
            2 ** 32
        )

        self.player1_wins = 0
        self.player2_wins = 0

        self.round_number = 1

        self.round_result_received = False

        self.upgrade_phase_active = True
        self.upgrade_selector = 1
        self.upgrade_selections = {}

        self.input_history = {
            1: {},
            2: {}
        }

        print(
            "START MATCH:",
            self.match_seed
        )

        self.broadcast(
            {
                "type": "start_match",
                "player1_weapon": (
                    self.weapon_choices[1]
                ),
                "player2_weapon": (
                    self.weapon_choices[2]
                ),
                "seed": self.match_seed,
                "player1_info": (
                    self.player_info[1]
                ),
                "player2_info": (
                    self.player_info[2]
                )
            }
        )

    # -------------------------------------------------
    # SEND
    # -------------------------------------------------

    def send_to_player(
        self,
        player_number,
        message
    ):
        with self.lock:

            client_socket = self.clients.get(
                player_number
            )

        if client_socket is None:
            return

        try:

            client_socket.sendall(
                encode_message(
                    message
                )
            )

        except OSError:

            self.disconnect_player(
                player_number,
                client_socket
            )

    def broadcast(
        self,
        message
    ):
        with self.lock:

            player_numbers = list(
                self.clients.keys()
            )

        for player_number in player_numbers:

            self.send_to_player(
                player_number,
                message
            )

    # -------------------------------------------------
    # DISCONNECT
    # -------------------------------------------------

    def disconnect_player(
        self,
        player_number,
        client_socket=None,
        graceful=False
    ):
        with self.lock:

            current_socket = self.clients.get(
                player_number
            )

            if (
                client_socket is not None
                and current_socket is not client_socket
            ):

                return

            removed_socket = self.clients.pop(
                player_number,
                None
            )

            self.client_buffers.pop(
                player_number,
                None
            )

            self.authenticated_players.discard(
                player_number
            )

            remaining_count = len(
                self.clients
            )

        # -------------------------------------------------
        # Clear this player's data.
        # -------------------------------------------------

        self.player_info[
            player_number
        ] = None

        self.weapon_choices[
            player_number
        ] = None

        self.ready_players.discard(
            player_number
        )

        self.rematch_requests.discard(
            player_number
        )

        self.upgrade_selections.pop(
            player_number,
            None
        )

        self.input_history[
            player_number
        ].clear()

        # -------------------------------------------------
        # If fewer than two players remain, reset the
        # match/lobby state.
        #
        # room_code intentionally remains unchanged.
        # -------------------------------------------------

        if remaining_count < 2:

            self.reset_match_state()

        # -------------------------------------------------
        # Close removed socket.
        # -------------------------------------------------

        if removed_socket is not None:

            try:

                removed_socket.shutdown(
                    socket.SHUT_RDWR
                )

            except OSError:
                pass

            try:

                removed_socket.close()

            except OSError:
                pass

        print(
            f"Player {player_number} disconnected"
        )

        if not self.running:
            return

        # -------------------------------------------------
        # One player remains.
        # -------------------------------------------------

        if remaining_count == 1:

            # -------------------------------------------------
            # Player 2 intentionally left.
            # -------------------------------------------------

            if (
                player_number == 2
                and graceful
            ):

                self.broadcast_player_count()

                return

            # -------------------------------------------------
            # Player 2 unexpectedly disconnected.
            # -------------------------------------------------

            if player_number == 2:

                self.broadcast(
                    {
                        "type": "opponent_left"
                    }
                )

                self.broadcast_player_count()

                return

            # -------------------------------------------------
            # Player 1 is the host.
            # Destroy the room.
            # -------------------------------------------------

            if player_number == 1:

                self.broadcast(
                    {
                        "type": "opponent_left"
                    }
                )

                self.broadcast_player_count()

                self.stop()

                return

        # -------------------------------------------------
        # Nobody remains.
        # -------------------------------------------------

        self.broadcast_player_count()

    # -------------------------------------------------
    # STOP
    # -------------------------------------------------

    def stop(
        self
    ):
        if not self.running:
            return

        print(
            "Stopping server on port",
            self.port
        )

        self.running = False

        # -------------------------------------------------
        # Detach listening socket first.
        # -------------------------------------------------

        server_socket = self.socket
        self.socket = None

        # -------------------------------------------------
        # Close clients.
        # -------------------------------------------------

        with self.lock:

            clients = list(
                self.clients.values()
            )

            self.clients.clear()
            self.client_buffers.clear()
            self.authenticated_players.clear()

        for client_socket in clients:

            try:

                client_socket.shutdown(
                    socket.SHUT_RDWR
                )

            except OSError:
                pass

            try:

                client_socket.close()

            except OSError:
                pass

        # -------------------------------------------------
        # Close listening socket.
        # -------------------------------------------------

        if server_socket is not None:

            try:

                server_socket.shutdown(
                    socket.SHUT_RDWR
                )

            except OSError:
                pass

            try:

                server_socket.close()

            except OSError:
                pass

        print(
            "Server stopped on port",
            self.port
        )