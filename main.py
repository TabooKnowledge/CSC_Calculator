from config import ingredients_data, resolution_profiles, flavors_data, icons_data, buttons_data, CONSTANTS
import cProfile
from classes import *
from types import SimpleNamespace
import pygame
import sys
import os


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
        self.initialize_classes()
        self.running = True

    def create_classes(self):
        self.sprite_manager = SpriteManager(self)
        self.prep_sheet = PrepSheet(self)
        self.draw_manager = DrawManager(self)
        self.animation_manager = AnimationManager(self)
        self.event_manager = EventManager(self)
        self.state_manager = StateManager(self)
        self.ui_manager = UiManager(self)
        self.background = Background(self)

    def initialize_classes(self):
        self.initialize_ingredients()
        self.ui_manager.initialize()
        self.background.initialize()

    def initialize_ingredients(self):
        for name, weight in ingredients_data.items():
            ingredient = Ingredient(self, name, weight)
            self.ingredients.append(ingredient)

    def build_flavor_set(self, icon_name) -> list[Flavor]:
        if icon_name == "reach_in":
            keys = CONSTANTS.REACH_IN_ORDER
        elif icon_name == "quick":
            keys = CONSTANTS.QUICK_ORDER
        else:
            keys = CONSTANTS.WALK_IN_ORDER

        flavors = []
        sprites = []
        flavors_by_name = {v.name: v for v in vars(self.data.flavors).values()}
        for key in keys:
            attr_value = flavors_by_name.get(key)
            if not attr_value:
                continue
            f = Flavor(self, attr_value, self.ingredients)
            f.initialize()
            f.load_sprite(Sprite)
            sprites.append(f.sprite)
            flavors.append(f)
        self.ui_manager.scale_sprites(sprites)
        return flavors

    def main_loop(self):
        while self.running:
            self.state_manager.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                self.event_manager.update(event)

            self.ui_manager.update_screen()
            self.draw_manager.draw_registry()
            self.ui_manager.draw_icons()
            self.ui_manager.draw_canvas()
            #self.draw_grid()
            pygame.display.flip()
            fps = self.clock.get_fps()
            #print(f"FPS: {fps}")
            self.clock.tick(self.fps)




coordinator = Coordinator()
coordinator.initialize()
cProfile.run("coordinator.main_loop()")
#coordinator.main_loop()
pygame.quit()
sys.exit()
