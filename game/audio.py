import pygame


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

    def set_volume(self, volume):
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

    def get_volume(
        self,
        category
    ):
        master = self.settings.master_volume

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

    def update(self):
        for sound in self.sounds:
            sound.update_volume()

        pygame.mixer.music.set_volume(
            self.settings.master_volume
            * self.settings.music_volume
        )