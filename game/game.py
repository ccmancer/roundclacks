import pygame

from game.settings import GameSettings
from game.audio import AudioManager
from game.states.main_menu import MainMenuState


class Game:

    def __init__(
        self
    ):
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
        # Netplay server
        # -------------------------------------------------
        #
        # The host server belongs to the overall netplay
        # session, not to an individual screen/state.
        #
        # This allows the host to keep the same room alive
        # when an opponent leaves.
        # -------------------------------------------------

        self.netplay_server = None

        # -------------------------------------------------
        # Fixed simulation
        # -------------------------------------------------

        self.simulation_dt = 1 / 60
        self.simulation_accumulator = 0

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

    def start_weapon_select(
        self
    ):
        from game.states.weapon_select import (
            WeaponSelectState
        )

        self.state = WeaponSelectState(
            self
        )

        self.simulation_accumulator = 0

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

        self.simulation_accumulator = 0

    def start_netplay(
        self
    ):
        from game.states.netplay import (
            NetplayState
        )

        self.state = NetplayState(
            self
        )

        self.simulation_accumulator = 0

    def start_netplay_weapon_select(
        self,
        client,
        is_host=False,
        server=None
    ):
        from game.states.netplay_weapon_select import (
            NetplayWeaponSelectState
        )

        self.state = NetplayWeaponSelectState(
            self,
            client,
            is_host=is_host,
            server=server
        )

        self.simulation_accumulator = 0

    def start_netplay_match(
        self,
        player1_weapon,
        player2_weapon,
        seed,
        player1_info,
        player2_info,
        client,
        server=None
    ):
        from game.states.netplay_match import (
            NetplayMatchState
        )

        self.state = NetplayMatchState(
            self,
            player1_weapon,
            player2_weapon,
            seed,
            player1_info,
            player2_info,
            client,
            server
        )

        self.simulation_accumulator = 0

    def start_settings(
        self
    ):
        from game.states.settings import SettingsState

        self.state = SettingsState(
            self
        )

        self.simulation_accumulator = 0

    def start_card_gallery(
        self
    ):
        from game.states.card_gallery import CardGalleryState

        self.state = CardGalleryState(
            self
        )

        self.simulation_accumulator = 0

    def return_to_main_menu(
        self
    ):
        self.state = MainMenuState(
            self
        )

        self.simulation_accumulator = 0

    # -------------------------------------------------
    # EVENTS
    # -------------------------------------------------

    def handle_events(
        self
    ):
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

    def update(
        self,
        dt
    ):
        self.audio.update()

        if getattr(
            self.state,
            "is_simulation_state",
            False
        ):

            self.simulation_accumulator += dt

            self.simulation_accumulator = min(
                self.simulation_accumulator,
                self.simulation_dt * 5
            )

            while (
                self.simulation_accumulator
                >= self.simulation_dt
            ):

                self.state.update(
                    self.simulation_dt
                )

                self.simulation_accumulator -= (
                    self.simulation_dt
                )

                if not getattr(
                    self.state,
                    "is_simulation_state",
                    False
                ):

                    self.simulation_accumulator = 0

                    break

        else:

            self.state.update(
                dt
            )

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------

    def draw(
        self
    ):
        self.state.draw(
            self.screen
        )

        pygame.display.flip()

    # -------------------------------------------------
    # RUN
    # -------------------------------------------------

    def run(
        self
    ):
        while self.running:

            dt = (
                self.clock.tick(60)
                / 1000
            )

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()