import json
from pathlib import Path


SETTINGS_FILE = (
    Path(__file__).resolve().parent.parent
    / "save"
    / "settings.json"
)


class GameSettings:
    def __init__(
        self
    ):
        # -------------------------------------------------
        # Defaults
        # -------------------------------------------------

        self.master_volume = 1.0
        self.game_volume = 1.0
        self.ui_volume = 1.0
        self.music_volume = 1.0

        self.player1_name = "Player 1"
        self.player2_name = "Player 2"

        self.player1_color = (
            255,
            0,
            0
        )

        self.player2_color = (
            0,
            0,
            255
        )

        # Set by Game after AudioManager is created.
        self.audio = None

        # -------------------------------------------------
        # Load
        # -------------------------------------------------

        self.load()

    # -------------------------------------------------
    # RESET
    # -------------------------------------------------

    def reset(self):
        self.master_volume = 1.0
        self.game_volume = 1.0
        self.ui_volume = 1.0
        self.music_volume = 1.0

        self.player1_name = "Player 1"
        self.player2_name = "Player 2"

        self.player1_color = (
            255,
            0,
            0
        )

        self.player2_color = (
            0,
            0,
            255
        )

        self.save()

        self.update_audio()

    # -------------------------------------------------
    # AUDIO UPDATE
    # -------------------------------------------------

    def update_audio(self):
        if self.audio is not None:
            self.audio.update()

    # -------------------------------------------------
    # VOLUME
    # -------------------------------------------------

    def set_master_volume(
        self,
        value
    ):
        self.master_volume = max(
            0,
            min(
                1,
                value
            )
        )

        self.save()
        self.update_audio()

    def set_game_volume(
        self,
        value
    ):
        self.game_volume = max(
            0,
            min(
                1,
                value
            )
        )

        self.save()
        self.update_audio()

    def set_ui_volume(
        self,
        value
    ):
        self.ui_volume = max(
            0,
            min(
                1,
                value
            )
        )

        self.save()
        self.update_audio()

    def set_music_volume(
        self,
        value
    ):
        self.music_volume = max(
            0,
            min(
                1,
                value
            )
        )

        self.save()
        self.update_audio()

    # -------------------------------------------------
    # SAVE
    # -------------------------------------------------

    def save(self):
        SETTINGS_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        data = {
            "master_volume": self.master_volume,
            "game_volume": self.game_volume,
            "ui_volume": self.ui_volume,
            "music_volume": self.music_volume,

            "player1_name": self.player1_name,
            "player2_name": self.player2_name,

            "player1_color": list(
                self.player1_color
            ),

            "player2_color": list(
                self.player2_color
            )
        }

        try:
            with open(
                SETTINGS_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    data,
                    file,
                    indent=4
                )

        except OSError as error:

            print(
                "Could not save settings:",
                error
            )

    # -------------------------------------------------
    # LOAD
    # -------------------------------------------------

    def load(self):
        if not SETTINGS_FILE.exists():
            self.save()
            return

        try:

            with open(
                SETTINGS_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(
                    file
                )

        except (
            OSError,
            json.JSONDecodeError
        ):

            print(
                "Could not load settings. "
                "Using defaults."
            )

            self.save()
            return

        # -------------------------------------------------
        # Audio
        # -------------------------------------------------

        self.master_volume = (
            self.get_number(
                data,
                "master_volume",
                self.master_volume
            )
        )

        self.game_volume = (
            self.get_number(
                data,
                "game_volume",
                self.game_volume
            )
        )

        self.ui_volume = (
            self.get_number(
                data,
                "ui_volume",
                self.ui_volume
            )
        )

        self.music_volume = (
            self.get_number(
                data,
                "music_volume",
                self.music_volume
            )
        )

        # -------------------------------------------------
        # Names
        # -------------------------------------------------

        player1_name = data.get(
            "player1_name",
            self.player1_name
        )

        player2_name = data.get(
            "player2_name",
            self.player2_name
        )

        if isinstance(
            player1_name,
            str
        ) and player1_name.strip():

            self.player1_name = (
                player1_name.strip()
            )

        if isinstance(
            player2_name,
            str
        ) and player2_name.strip():

            self.player2_name = (
                player2_name.strip()
            )

        # -------------------------------------------------
        # Colours
        # -------------------------------------------------

        self.player1_color = (
            self.get_color(
                data,
                "player1_color",
                self.player1_color
            )
        )

        self.player2_color = (
            self.get_color(
                data,
                "player2_color",
                self.player2_color
            )
        )

        # -------------------------------------------------
        # Keep volume values valid
        # -------------------------------------------------

        self.master_volume = max(
            0,
            min(
                1,
                self.master_volume
            )
        )

        self.game_volume = max(
            0,
            min(
                1,
                self.game_volume
            )
        )

        self.ui_volume = max(
            0,
            min(
                1,
                self.ui_volume
            )
        )

        self.music_volume = max(
            0,
            min(
                1,
                self.music_volume
            )
        )

    # -------------------------------------------------
    # HELPERS
    # -------------------------------------------------

    @staticmethod
    def get_number(
        data,
        key,
        default
    ):
        value = data.get(
            key,
            default
        )

        if not isinstance(
            value,
            (int, float)
        ):
            return default

        return float(
            value
        )

    @staticmethod
    def get_color(
        data,
        key,
        default
    ):
        value = data.get(
            key,
            default
        )

        if (
            not isinstance(
                value,
                (list, tuple)
            )
            or len(value) != 3
        ):
            return default

        try:

            color = tuple(
                int(component)
                for component in value
            )

        except (
            TypeError,
            ValueError
        ):

            return default

        if any(
            component < 0
            or component > 255
            for component in color
        ):
            return default

        return color