import pygame
from pathlib import Path


MUSIC_FOLDER = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "audio"
    / "music"
)


class ManagedSound:
    def __init__(
        self,
        sound,
        audio_manager,
        category
    ):
        self.sound = sound
        self.audio_manager = audio_manager
        self.category = category

        self.base_volume = 1.0

        self.audio_manager.register_sound(
            self
        )

    def play(
        self,
        loops=0
    ):
        self.update_volume()

        return self.sound.play(
            loops
        )

    def stop(self):
        self.sound.stop()

    def set_volume(
        self,
        volume
    ):
        self.base_volume = volume

        self.update_volume()

    def update_volume(self):
        volume = (
            self.base_volume
            * self.audio_manager.get_volume(
                self.category
            )
        )

        self.sound.set_volume(
            volume
        )


class AudioManager:
    GAME = "game"
    UI = "ui"

    def __init__(
        self,
        settings
    ):
        self.settings = settings
        self.sounds = []

        # -------------------------------------------------
        # Music
        # -------------------------------------------------

        self.current_music = None
        self.current_music_name = None

    # -------------------------------------------------
    # SOUND MANAGEMENT
    # -------------------------------------------------

    def register_sound(
        self,
        sound
    ):
        self.sounds.append(
            sound
        )

    def load_game_sound(
        self,
        path
    ):
        sound = pygame.mixer.Sound(
            path
        )

        return ManagedSound(
            sound,
            self,
            self.GAME
        )

    def load_ui_sound(
        self,
        path
    ):
        sound = pygame.mixer.Sound(
            path
        )

        return ManagedSound(
            sound,
            self,
            self.UI
        )

    # -------------------------------------------------
    # VOLUME
    # -------------------------------------------------

    def get_volume(
        self,
        category
    ):
        master = (
            self.settings.master_volume
        )

        if category == self.GAME:
            return (
                master
                * self.settings.game_volume
            )

        if category == self.UI:
            return (
                master
                * self.settings.ui_volume
            )

        return master

    # -------------------------------------------------
    # MUSIC
    # -------------------------------------------------

    def play_music(
        self,
        name
    ):
        # Don't restart the same track.
        if (
            self.current_music_name
            == name
        ):
            return

        path = (
            MUSIC_FOLDER
            / f"{name}.mp3"
        )

        if not path.exists():
            print(
                "Music file not found:",
                path
            )
            return

        pygame.mixer.music.stop()

        try:
            pygame.mixer.music.load(
                path
            )

            pygame.mixer.music.set_volume(
                self.get_music_volume()
            )

            pygame.mixer.music.play(
                -1
            )

            self.current_music_name = name

        except pygame.error as error:
            print(
                "Could not play music:",
                error
            )

    def stop_music(self):
        pygame.mixer.music.stop()

        self.current_music = None
        self.current_music_name = None

    def get_music_volume(self):
        return (
            self.settings.master_volume
            * self.settings.music_volume
        )

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(self):
        for sound in self.sounds:
            sound.update_volume()

        pygame.mixer.music.set_volume(
            self.get_music_volume()
        )