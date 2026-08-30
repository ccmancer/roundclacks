import json

from network.input import FrameInput


class InputPacket:
    def __init__(
        self,
        player_number,
        frame_input
    ):
        self.player_number = player_number
        self.frame_input = frame_input

    # -------------------------------------------------
    # SERIALIZE
    # -------------------------------------------------

    def to_bytes(self):
        data = {
            "type": "input",
            "player": self.player_number,
            "frame": self.frame_input.frame,
            "attack": self.frame_input.attack
        }

        return (
            json.dumps(data)
            .encode("utf-8")
        )

    # -------------------------------------------------
    # DESERIALIZE
    # -------------------------------------------------

    @staticmethod
    def from_bytes(data):
        message = json.loads(
            data.decode("utf-8")
        )

        if message.get("type") != "input":
            raise ValueError(
                "Invalid input packet type."
            )

        frame_input = FrameInput(
            message["frame"],
            message["attack"]
        )

        return InputPacket(
            message["player"],
            frame_input
        )