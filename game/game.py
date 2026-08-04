import pygame
from entities.player import Player
from physics.collision import check_circle_collision, resolve_circle_collision

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((720, 720))
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.player1 = Player(
            150,
            360,
            40,
            "red",
            375
        )
        self.player2 = Player(
            570,
            360,
            40,
            "blue",
            375
        )
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
    def update(self):
        self.player1.update(
            self.dt,
            self.screen.get_width(),
            self.screen.get_height()
        )
        self.player2.update(
            self.dt,
            self.screen.get_width(),
            self.screen.get_height()
        )
        if check_circle_collision(self.player1, self.player2):
            resolve_circle_collision(self.player1, self.player2)
    def draw(self):
        self.screen.fill("white")
        self.player1.draw(self.screen)
        self.player2.draw(self.screen)
        pygame.display.flip()
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.dt = self.clock.tick(60) / 1000
        pygame.quit()