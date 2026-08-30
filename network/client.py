import socket
import time
from collections import deque

from network.protocol import (
    BUFFER_SIZE,
    encode_message,
    decode_messages
)

from network.input import FrameInput
from network.input_buffer import InputBuffer


class GameClient:

    def __init__(
        self
    ):
        self.socket = None

        self.connected = False

        # -------------------------------------------------
        # Player assignment
        # -------------------------------------------------

        self.player_number = None

        self.buffer = b""

        # -------------------------------------------------
        # Input
        # -------------------------------------------------

        self.input_buffer = InputBuffer()

        self.last_sent_frame = -1

        # -------------------------------------------------
        # Temporary rollback test delay
        # -------------------------------------------------

        self.input_delay_seconds = 0.0

        self.delayed_inputs = deque()

    # -------------------------------------------------
    # CONNECT
    # -------------------------------------------------

    def connect(
        self,
        host,
        port=5000
    ):
        if self.connected:
            return False

        try:

            self.socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            self.socket.connect(
                (
                    host,
                    port
                )
            )

            self.socket.setblocking(
                False
            )

            self.connected = True

            return True

        except OSError as error:

            print(
                "Could not connect:",
                error
            )

            self.close()

            return False

    # -------------------------------------------------
    # SEND
    # -------------------------------------------------

    def send(
        self,
        message
    ):
        if not self.connected:
            return False

        try:

            self.socket.sendall(
                encode_message(
                    message
                )
            )

            return True

        except OSError:

            self.close()

            return False

    # -------------------------------------------------
    # LEAVE ROOM
    # -------------------------------------------------

    def leave_room(
        self
    ):
        """
        Tell the server that this client is intentionally
        leaving the room.
        """

        if not self.connected:
            return

        try:

            self.socket.sendall(
                encode_message(
                    {
                        "type": "leave_room"
                    }
                )
            )

        except OSError:

            pass

        self.close()

    # -------------------------------------------------
    # INPUT
    # -------------------------------------------------

    def send_input(
        self,
        frame_input
    ):
        """
        Send one local input frame.

        Frame numbering starts at 1 for each round.
        """

        if not self.connected:
            return

        if self.player_number not in (
            1,
            2
        ):
            return

        if not isinstance(
            frame_input,
            FrameInput
        ):
            return

        if (
            frame_input.frame
            <= self.last_sent_frame
        ):
            return

        self.send(
            {
                "type": "input",
                "frame": frame_input.frame,
                "attack": frame_input.attack
            }
        )

        self.last_sent_frame = (
            frame_input.frame
        )

    # -------------------------------------------------
    # RESET INPUT SEQUENCE
    # -------------------------------------------------

    def reset_input_sequence(
        self
    ):
        self.last_sent_frame = -1

        self.input_buffer = InputBuffer()

        self.delayed_inputs.clear()

    # -------------------------------------------------
    # INPUT BUFFER
    # -------------------------------------------------

    def get_input(
        self,
        player_number,
        frame
    ):
        return self.input_buffer.get(
            player_number,
            frame
        )

    def has_input(
        self,
        player_number,
        frame
    ):
        return self.input_buffer.has(
            player_number,
            frame
        )

    def remove_inputs_before(
        self,
        frame
    ):
        self.input_buffer.remove_before(
            frame
        )

    # -------------------------------------------------
    # RECEIVE
    # -------------------------------------------------

    def update(
        self
    ):
        if not self.connected:
            return []

        messages = []

        # -------------------------------------------------
        # Receive socket data.
        # -------------------------------------------------

        try:

            while True:

                data = self.socket.recv(
                    BUFFER_SIZE
                )

                if not data:

                    self.close()

                    break

                self.buffer += data

                new_messages, self.buffer = (
                    decode_messages(
                        self.buffer
                    )
                )

                messages.extend(
                    new_messages
                )

        except BlockingIOError:
            pass

        except OSError:
            self.close()

        # -------------------------------------------------
        # Process messages.
        # -------------------------------------------------

        for message in messages:

            message_type = (
                message.get("type")
            )

            if message_type == (
                "assign_player"
            ):

                self.player_number = (
                    message.get("player")
                )

            elif message_type == "input":

                player_number = (
                    message.get("player")
                )

                frame = (
                    message.get("frame")
                )

                attack = (
                    message.get("attack")
                )

                if player_number not in (
                    1,
                    2
                ):
                    continue

                if not isinstance(
                    frame,
                    int
                ):
                    continue

                if not isinstance(
                    attack,
                    bool
                ):
                    continue

                if frame < 1:
                    continue

                frame_input = FrameInput(
                    frame,
                    attack
                )

                release_time = (
                    time.monotonic()
                    + self.input_delay_seconds
                )

                self.delayed_inputs.append(
                    (
                        release_time,
                        player_number,
                        frame_input
                    )
                )

        # -------------------------------------------------
        # Release delayed inputs.
        # -------------------------------------------------

        now = time.monotonic()

        while self.delayed_inputs:

            (
                release_time,
                player_number,
                frame_input
            ) = self.delayed_inputs[0]

            if release_time > now:
                break

            self.delayed_inputs.popleft()

            self.input_buffer.store(
                player_number,
                frame_input
            )

        return messages

    # -------------------------------------------------
    # CLOSE
    # -------------------------------------------------

    def close(
        self
    ):
        self.connected = False

        self.player_number = None

        self.last_sent_frame = -1

        if self.socket is not None:

            try:

                self.socket.close()

            except OSError:
                pass

        self.socket = None

        self.buffer = b""

        self.input_buffer = InputBuffer()

        self.delayed_inputs.clear()