import pygame

from game.settings import GameSettings
from game.audio import AudioManager
from game.states.main_menu import MainMenuState


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(
            (720, 720)
        )

        pygame.display.set_caption(
            "Roundclacks"
        )

        self.clock = pygame.time.Clock()
        self.running = True

        # -------------------------------------------------
        # Settings
        # -------------------------------------------------

        self.settings = GameSettings()

        # -------------------------------------------------
        # Audio
        # -------------------------------------------------

        self.audio = AudioManager(
            self.settings
        )

        # -------------------------------------------------
        # State
        # -------------------------------------------------

        self.state = MainMenuState(
            self
        )

    # -------------------------------------------------
    # STATE STARTERS
    # -------------------------------------------------

    def start_weapon_select(self):
        from game.states.weapon_select import WeaponSelectState

        self.state = WeaponSelectState(
            self
        )

    def start_local_match(
        self,
        player1_weapon,
        player2_weapon
    ):
        from game.states.match import MatchState

        self.state = MatchState(
            self,
            player1_weapon,
            player2_weapon
        )

    def start_settings(self):
        from game.states.settings import SettingsState

        self.state = SettingsState(
            self
        )

    def start_card_gallery(self):
        from game.states.card_gallery import CardGalleryState

        self.state = CardGalleryState(
            self
        )

    def return_to_main_menu(self):
        self.state = MainMenuState(
            self
        )

    # -------------------------------------------------
    # EVENTS
    # -------------------------------------------------

    def handle_events(self):
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

        self.state.handle_events(
            events
        )

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(self, dt):
        self.audio.update()

        self.state.update(
            dt
        )

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------

    def draw(self):
        self.state.draw(
            self.screen
        )

        pygame.display.flip()

    # -------------------------------------------------
    # RUN
    # -------------------------------------------------

    def run(self):
        while self.running:
            dt = (
                self.clock.tick(60)
                / 1000
            )

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()