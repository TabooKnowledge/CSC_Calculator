import cProfile
from classes import *
from types import SimpleNamespace
import pygame
import sys


pygame.init()


class Coordinator:
    def __init__(self):
        #Classes
        self.background = None
        self.sprite_manager = None
        self.state_manager = None
        self.event_manager = None
        self.animation_manager = None
        self.draw_manager = None
        self.grid = None
        self.prep_sheet = None
        self.ui_manager = None
        #Lists
        self.ingredients = []
        self.flavors = []
        #Data
        self.data = SimpleNamespace(buttons=buttons_data, ingredients=ingredients_data, flavors=flavors_data, menu_icons=icons_data)
        #State
        self.running = True
        #Pygame
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.delta = None

    def initialize(self):
        self.create_classes()
        initialize_ingredients(self)
        self.initialize_classes()
        self.running = True

    def create_classes(self):
        self.sprite_manager = SpriteManager(self)
        self.prep_sheet = PrepSheet(self)
        self.draw_manager = DrawManager(self)
        self.animation_manager = AnimationManager(self)
        self.event_manager = EventManager(self)
        self.ui_manager = UiManager(self)
        self.background = Background(self)

    def initialize_classes(self):
        self.ui_manager.initialize()
        self.background.initialize()

    def main_loop(self):
        while self.running:
            for e in pygame.event.get():
                self.event_manager.event = e
                self.event_manager.update()
            self.ui_manager.update_screen()
            self.draw_manager.draw_registry()
            self.ui_manager.draw_icons()
            self.ui_manager.draw_canvas()
            #self.draw_grid()
            pygame.display.flip()
            #fps = self.clock.get_fps()
            #print(f"FPS: {fps}")
            self.clock.tick(self.fps)


coordinator = Coordinator()
coordinator.initialize()
#cProfile.run("coordinator.main_loop()")
coordinator.main_loop()
pygame.quit()
sys.exit()
