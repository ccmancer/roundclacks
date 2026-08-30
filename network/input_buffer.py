class InputBuffer:
    def __init__(self):
        self.inputs = {}

    # -------------------------------------------------
    # STORE
    # -------------------------------------------------

    def store(
        self,
        player_number,
        frame_input
    ):
        if player_number not in (
            1,
            2
        ):
            raise ValueError(
                "Player number must be 1 or 2."
            )

        if player_number not in self.inputs:
            self.inputs[player_number] = {}

        self.inputs[player_number][
            frame_input.frame
        ] = frame_input

    # -------------------------------------------------
    # GET
    # -------------------------------------------------

    def get(
        self,
        player_number,
        frame
    ):
        player_inputs = self.inputs.get(
            player_number,
            {}
        )

        return player_inputs.get(
            frame
        )

    # -------------------------------------------------
    # CHECK
    # -------------------------------------------------

    def has(
        self,
        player_number,
        frame
    ):
        return (
            self.get(
                player_number,
                frame
            )
            is not None
        )

    # -------------------------------------------------
    # CLEANUP
    # -------------------------------------------------

    def remove_before(
        self,
        frame
    ):
        for player_inputs in self.inputs.values():

            old_frames = [
                old_frame
                for old_frame in player_inputs
                if old_frame < frame
            ]

            for old_frame in old_frames:
                del player_inputs[
                    old_frame
                ]