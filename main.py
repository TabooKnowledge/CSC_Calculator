from setuptools import namespaces

from config import ingredients_data, resolution_profiles, flavors_data, icons_data, buttons_data, CONSTANTS
from classes import Ingredient, Flavor, PrepSheet, Grid, DrawManager, Sprite, AnimationManager
from types import SimpleNamespace
import pygame
import sys
import os


pygame.init()


class Coordinator:
    def __init__(self):
        #Classes
        self.animation_manager = None
        self.draw_manager = None
        self.grid = None
        self.prep_sheet = None
        #Lists
        self.ingredients = []
        self.flavors = []
        self.buttons = []
        self.icons = []
        #Numbers
        self.scale = SimpleNamespace(x=0, y=0, image=1, multiplier=1, font=8)
        self.base_resolution = SimpleNamespace(w=0, h=0)
        self.screen = SimpleNamespace(w=0, h=0, short=None, dimensions=None)
        #self.font_size = None
        #PyGame references
        self.pygame = SimpleNamespace(canvas=None, screen=None, clock=None, fps=None, flip=pygame.display.flip, display_info=None)
        #Images
        self.bg = SimpleNamespace(name="", surface=None)
        #Data
        self.data = SimpleNamespace(buttons=buttons_data, ingredients=ingredients_data, flavors=flavors_data, menu_icons=icons_data)
        #Resolution
        self.resolution_profiles = resolution_profiles
        self.active_profile = None
        #State
        self.state = "main"
        self.running = True
        #Sprites
        self.dragged_sprite = None

    def initialize(self):
        self.create_classes()
        self.initialize_classes()
        self.initialize_self()

    def create_classes(self):
        self.prep_sheet = PrepSheet(self)
        self.grid = Grid(self)
        self.draw_manager = DrawManager(self)
        self.animation_manager = AnimationManager(self)

    def initialize_classes(self):
        self.grid.initialize()
        self.initialize_ingredients()
        self.load_sprites()
        self.initialize_flavors()

    def initialize_ingredients(self):
        for name, weight in ingredients_data.items():
            ingredient = Ingredient(self, name, weight)
            self.ingredients.append(ingredient)

    def initialize_flavors(self):
        for attr_value in vars(self.data.flavors).values():
            flavor = Flavor(self, attr_value, self.ingredients)
            flavor.initialize()
            flavor.load_sprite(Sprite)
            self.flavors.append(flavor)

    def load_sprites(self):
        self.load_namespace_sprites(self.data.buttons, "button", )
        self.load_namespace_sprites(self.data.menu_icons, "icon")

    def load_namespace_sprites(self, namespace, img_tag=None):
        for attr_value in vars(namespace).values():
            sprite = Sprite(self, attr_value.name, attr_value.image_name)
            sprite.state_tag = getattr(attr_value, "state_tag", None)
            sprite.initialize(img_tag)
            attr_value.surface = sprite.surface

    def initialize_self(self):
        self.screen.display_info = pygame.display.Info()
        self.screen.w = self.screen.display_info.current_w
        self.screen.h = self.screen.display_info.current_h
        self.screen.short = min(self.screen.w, self.screen.h)
        self.screen.dimensions = (self.screen.w, self.screen.h)
        self.pygame.screen = pygame.display.set_mode(self.screen.dimensions)
        self.pygame.canvas = pygame.Surface(self.screen.dimensions)
        pygame.display.set_caption("Chicken Salad Production Software")
        self.pygame.clock = pygame.time.Clock()
        self.pygame.fps = 60
        self.running = True
        self.bg.name = "rainbow_bg.jpg"
        self.load_background()
        self.adjust_resolution()
        self.draw_manager.draw_registry(True)

    def adjust_resolution(self):
        self.retrieve_resolution_data()
        self.set_resolution_data()

    def retrieve_resolution_data(self):
        for attr_value in vars(self.resolution_profiles).values():
            if self.screen.short <= attr_value.max_short:
                self.active_profile = attr_value
                break

    def set_resolution_data(self):
        self.base_resolution.w = self.active_profile.base_width
        self.base_resolution.h = self.active_profile.base_height
        self.scale.font = self.active_profile.font_size
        self.scale.x = self.screen.w / self.base_resolution.w
        self.scale.y = self.screen.h / self.base_resolution.h
        self.scale.multiplier = self.active_profile.scale_multiplier
        self.scale.image = min(self.scale.x, self.scale.y) * self.scale.multiplier
        self.scale.font = self.active_profile.font_size * self.scale.image

    def load_background(self):
        self.bg.surface = pygame.image.load(os.path.join(CONSTANTS.IMAGE_DIR, self.bg.name))
        self.bg.surface = pygame.transform.scale(self.bg.surface, self.screen.dimensions)

    def blit_flavors(self):
        for i, flavor in enumerate(self.flavors):
            row = i // self.grid.cols
            col = i % self.grid.cols
            flavor.x, flavor.y = self.grid.coord[row][col]
            flavor.x += self.grid.cell_width // 2 - flavor.image.get_width() // 2
            flavor.y += self.grid.cell_height // 2 - flavor.image.get_height() // 2
            self.screen.blit(flavor.image,(flavor.x,flavor.y))

    def state_main(self):
        self.pygame.screen.blit(self.bg.surface,(0,0))


    def state_walk_in(self):
        self.pygame.screen.blit(self.buttons.reach_in.surface, (0, 0))


    def state_reach_in(self):
        self.pygame.screen.blit(self.buttons.reach_in.surface, (0, 0))


    def state_quick(self):
        self.pygame.screen.blit(self.buttons.reach_in.surface, (0, 0))


    def state_production(self):
        self.pygame.screen.blit(self.buttons.reach_in.surface, (0, 0))


    def handle_sprite_movement(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            self.check_image_clicked(mouse_x, mouse_y)
        elif event.type == pygame.MOUSEMOTION:
            self.move_sprite(*event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragged_sprite:
                self.dragged_sprite = None
        elif event.type == pygame.FINGERDOWN:
            touch_x = event.x * self.screen.w
            touch_y = event.y * self.screen.h
            self.check_image_clicked(touch_x, touch_y)
        elif event.type == pygame.FINGERMOTION:
            touch_x = event.x * self.screen.w
            touch_y = event.y * self.screen.h
            self.move_sprite(touch_x, touch_y)
        elif event.type == pygame.FINGERUP:
            if self.dragged_sprite:
                self.dragged_sprite = None

    def check_image_clicked(self, x, y):
        for s in self.draw_manager.registry:
            sprite_to_check = s if isinstance(s, list) else [s]
            for sprite in sprite_to_check:
                print(f"Name: {sprite.name}, X: {sprite.x}, Y: {sprite.y}")
                if sprite.x <= x <= sprite.x + sprite.w and sprite.y <= y <= sprite.y + sprite.h:
                    if sprite.state_tag is not None:
                        self.state = sprite.state_tag
                    self.dragged_sprite = sprite

    def move_sprite(self, x, y):
        if self.dragged_sprite:
            self.dragged_sprite.x = x - self.dragged_sprite.w // 2
            self.dragged_sprite.y = y - self.dragged_sprite.h // 2

    def main_loop(self):
        while self.running:
            if self.state == "main":
                _true = True
                #print("main")
            elif self.state == "reach_in":
                _true = True
                #print("reach_in")
            elif self.state == "walk_in":
                _true = True
                #print("walk_in")
            elif self.state == "quick":
                _true = True
                #print("quick")
            elif self.state == "production":
                _true = True
                #print("production")
            for sprite in self.draw_manager.registry:
                if sprite.img_tag != "button" and self.state in sprite.name and sprite.name != "icon_quick":
                    print(f"Name: {sprite.name}, Image Tag: {sprite.img_tag}")
                    sprite.home_x = sprite.x
                    sprite.home_y = sprite.y
                    scale = 1.75
                    center_x = self.screen.w // 2 - int(sprite.origin_w * scale) // 2
                    center_y = self.screen.h // 2 - int(sprite.origin_h * scale) // 2
                    self.animation_manager.lerp_scale(sprite, scale)
                    self.animation_manager.lerp_move(sprite, center_x, center_y)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                self.handle_sprite_movement(event)

            self.pygame.screen.fill((0,0,0))
            self.pygame.screen.blit(self.bg.surface,(0,0))
            self.draw_manager.draw_registry()
            self.pygame.screen.blit(self.pygame.canvas, (0, 0))
            #self.blit_flavors()
            #self.draw_grid()
            self.pygame.flip()
            self.pygame.clock.tick(self.pygame.fps)

    def draw_grid(self):
        cols = self.screen.w // 30
        rows = self.screen.h // 30
        for c in range(cols):
            x = c * 30
            pygame.draw.line(self.pygame.screen, (255, 255, 255), (x, 0), (x, self.screen.h))
        for r in range(rows):
            y = r * 30
            pygame.draw.line(self.pygame.screen, (255, 255, 255), (0, y), (self.screen.w, y))


coordinator = Coordinator()
coordinator.initialize()
coordinator.main_loop()
pygame.quit()
sys.exit()
