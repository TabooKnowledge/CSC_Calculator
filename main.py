import pygame
import sys
from types import SimpleNamespace
from config import flavors_data, ingredients_data, icons_data, buttons_data
from domain import initialize_ingredients, PrepSheet
from ui import DrawManager, Background
from engine import EventManager, AnimationManager, UiManager, StateStore


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
        self.state_store = None
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
        self.prep_sheet = PrepSheet(self)
        self.draw_manager = DrawManager(self)
        self.animation_manager = AnimationManager(self)
        self.event_manager = EventManager(self)
        self.ui_manager = UiManager(self)
        self.background = Background(self)
        self.state_store = StateStore(self)

    def initialize_classes(self):
        self.ui_manager.initialize()
        self.prep_sheet.initialize()
        self.state_store.initialize()
        self.background.initialize()

    def main_loop(self):
        while self.running:
            for e in pygame.event.get():
                self.event_manager.event = e
                self.event_manager.update()
            self.ui_manager.refresh_screen()
            self.draw_manager.draw_registry()
            self.ui_manager.update()
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
