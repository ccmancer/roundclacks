import pygame

from game.states.main_menu import MainMenuState


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((720, 720))
        pygame.display.set_caption("Roundclacks")

        self.clock = pygame.time.Clock()
        self.running = True

        self.state = MainMenuState(self)

    def start_weapon_select(self):
        from game.states.weapon_select import WeaponSelectState

        self.state = WeaponSelectState(self)

    def start_local_match(self, player1_weapon, player2_weapon):
        from game.states.match import MatchState

        self.state = MatchState(
            self,
            player1_weapon,
            player2_weapon
        )

    def handle_events(self):
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

        self.state.handle_events(events)

    def update(self, dt):
        self.state.update(dt)

    def draw(self):
        self.state.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()