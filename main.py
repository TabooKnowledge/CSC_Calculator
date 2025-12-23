from config import ingredients_data, flavors_data, resolution_profiles
from classes import Ingredient, Flavor, PrepSheet, Grid, DrawManager, Sprite
from types import SimpleNamespace
import pygame
import sys
import os


pygame.init()
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(SCRIPT_DIR, "images")


class Coordinator:
    def __init__(self):
        #Classes
        self.draw_manager = None
        self.grid = None
        self.prep_sheet = None
        self.ingredients = []
        self.flavors = []
        #Numbers
        self.scale = SimpleNamespace(x=0, y=0, image=1, font=8)
        self.base_resolution = SimpleNamespace(w=0, h=0)
        self.screen = SimpleNamespace(w=0, h=0, short=None, dimensions=None)
        #self.font_size = None
        #PyGame references
        self.pygame = SimpleNamespace(canvas=None, screen=None, clock=None, fps=None, flip=pygame.display.flip, display_info=None)
        #Images
        self.bg = SimpleNamespace(name="", surface=None)
        self.buttons_img = SimpleNamespace(
            reach_in=SimpleNamespace(name="reach_in.png", surface=None),
            walk_in=SimpleNamespace(name="walk_in.png", surface=None),
            quick=SimpleNamespace(name="quick.png", surface=None))
        #Resolution
        self.resolution_profiles = resolution_profiles
        self.active_profile = None
        #State
        self.running = True

    def initialize(self):
        self.initialize_classes()
        self.initialize_self()

    def initialize_classes(self):
        self.prep_sheet = PrepSheet(self)
        self.grid = Grid(self)
        self.grid.initialize()
        self.draw_manager = DrawManager(self)
        self.initialize_ingredients()
        self.initialize_flavors()

    def initialize_ingredients(self):
        for name, weight in ingredients_data.items():
            ingredient = Ingredient(self, {"name": name, "weight": weight})
            self.ingredients.append(ingredient)

    def initialize_flavors(self):
        for flavor in flavors_data.values():
            flavor = Flavor(self, flavor, ingredients_data)
            flavor.initialize()
            flavor.load_sprite(Sprite, pygame, IMAGE_DIR)
            self.flavors.append(flavor)

    def initialize_self(self):
        self.screen.display_info = pygame.display.Info()
        self.screen.w = self.screen.display_info.current_w
        self.screen.h = self.screen.display_info.current_h
        self.screen.short = min(self.screen.w, self.screen.h)
        self.screen.dimensions = (self.screen.w, self.screen.h)
        self.pygame.screen = pygame.display.set_mode(self.screen.dimensions)
        self.pygame.canvas = pygame.Surface(self.screen.dimensions)
        self.adjust_resolution()
        pygame.display.set_caption("Chicken Salad Production Software")
        self.pygame.clock = pygame.time.Clock()
        self.pygame.fps = 60
        self.running = True
        self.bg.name = "rainbow_bg.jpg"
        self.load_background()

    def adjust_resolution(self):
        self.retrieve_resolution_data()
        self.set_resolution_data()
        self.scale_images()

    def retrieve_resolution_data(self):
        for name, profile in self.resolution_profiles.items():
            if self.screen.short <= profile["max_short"]:
                self.active_profile =  profile
                break

    def set_resolution_data(self):
        self.base_resolution.w = self.active_profile["base_width"]
        self.base_resolution.h = self.active_profile["base_height"]
        self.scale.font = self.active_profile["font_size"]
        self.scale.x = self.screen.w / self.base_resolution.w
        self.scale.y = self.screen.h / self.base_resolution.h
        self.scale.image = min(self.scale.x, self.scale.y)
        self.scale.font = self.active_profile["font_size"] * self.scale.image

    def scale_images(self):
        for flavor in self.flavors:
            w = flavor.sprite.w * self.scale.image
            h = flavor.sprite.h * self.scale.image
            flavor.sprite.scale(pygame, w, h)

    def load_background(self):
        self.bg.surface = pygame.image.load(os.path.join(IMAGE_DIR, self.bg.name))
        self.bg.surface = pygame.transform.scale(self.bg.surface, self.screen.dimensions)

    def set_scaled_w_h(self, w, h):
        return w * self.scale.image, h * self.scale.image

    def blit_flavors(self):
        for i, flavor in enumerate(self.flavors):
            row = i // self.grid.cols
            col = i % self.grid.cols
            flavor.x, flavor.y = self.grid.coord[row][col]
            flavor.x += self.grid.cell_width // 2 - flavor.image.get_width() // 2
            flavor.y += self.grid.cell_height // 2 - flavor.image.get_height() // 2
            self.screen.blit(flavor.image,(flavor.x,flavor.y))

    def main_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            self.pygame.screen.fill((0,0,0))
            self.pygame.screen.blit(self.bg.surface,(0,0))
            #self.blit_flavors()
            self.pygame.flip()
            self.pygame.clock.tick(self.pygame.fps)


coordinator = Coordinator()
coordinator.initialize()
coordinator.main_loop()
pygame.quit()
sys.exit()
