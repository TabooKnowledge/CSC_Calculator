from config import *
import math
from types import SimpleNamespace
import os
import pygame


class Ingredient:
    def __init__(self, coordinator, name, weight):
        self.coordinator = coordinator
        self.name = name
        self.weight = weight
        self.totaled_weight = 0

    def total_weight(self, mix_weight):
        self.totaled_weight = round((mix_weight / 4) * self.weight, 2)


class Flavor:
    def __init__(self, coordinator, flavor_data, ingredients_data):
        #Reference
        self.coordinator = coordinator
        self.data = SimpleNamespace(flavor=flavor_data, ingredients=ingredients_data)
        self.tag = None
        self.img_tag = "flavor"
        #Visuals
        self.img_name = None
        self.sprite = None
        self.name = None
        #For production
        self.large_quick_par = 0
        self.small_quick_par = 0
        self.line_mix_par = 0
        self.totaled_par_weight = 0
        self.large_quick_on_hand = 0
        self.small_quick_on_hand = 0
        self.line_mix_on_hand = 0
        self.large_quick_needed = 0
        self.small_quick_needed = 0
        self.line_mix_needed = 0
        self.total_mix_weight = 0
        self.ingredients = []
        self.totaled_ingredient_weight = 0

    def initialize(self):
        self.img_name = self.data.flavor.img_name
        self.name = self.data.flavor.name
        self.store_ingredients()

    def store_ingredients(self):
        for name in self.data.flavor.ingredients:
            for ingredient in self.data.ingredients:
                if ingredient.name == name:
                    self.ingredients.append(ingredient)
                    break

    def load_sprite(self, sprite_class):
        self.sprite = sprite_class(self.coordinator, self.name, self.img_name)
        self.sprite.initialize(self.img_tag)

    def calculate_par_weight(self):
        self.totaled_par_weight = math.ceil(self.large_quick_par + self.small_quick_par / 2 + self.line_mix_par)

    def calculate_needed(self):
        self.calculate_prep_numbers()
        self.calculate_total_mix_weight()

    def calculate_prep_numbers(self):
        self.large_quick_needed = max(0, self.large_quick_par - self.large_quick_on_hand)
        self.small_quick_needed = max(0, self.small_quick_par - self.small_quick_on_hand)
        self.line_mix_needed = max(0, self.line_mix_par - self.line_mix_on_hand)

    def calculate_total_mix_weight(self):
        on_hand = self.large_quick_on_hand + self.small_quick_on_hand / 2 + self.line_mix_on_hand
        self.total_mix_weight = math.ceil(self.totaled_par_weight - on_hand)
        self.total_ingredient_weight()

    def total_ingredient_weight(self):
        self.totaled_ingredient_weight = 0
        for ingredient in self.ingredients:
            ingredient.total_weight(self.total_mix_weight)
            self.totaled_ingredient_weight += ingredient.weight


class PrepSheet:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.chicken_on_hand = 140
        self.chicken_par = 160
        self.total_chicken_used = 0
        self.chicken_remaining = 0
        self.chicken_to_cook = 0
        self.all_flavors = None
        self.error_not_enough_chicken = -1

    def calculate_production_numbers(self):
        self.total_chicken_used = 0
        for flavor in self.all_flavors:
            weight = flavor.total_mix_weight
            quarter_weight = weight / 4
            flavor.chicken_weight = round(weight - (quarter_weight * flavor.totaled_ingredient_weight), 2)
            self.total_chicken_used += flavor.chicken_weight
        if self.total_chicken_used < self.chicken_on_hand:
            self.chicken_remaining = self.chicken_on_hand - math.ceil(self.total_chicken_used)
            self.chicken_to_cook = self.chicken_par - self.chicken_remaining
        else:
            self.error_not_enough_chicken = 1

    def print_output(self):
        for flavor in self.all_flavors:
            print(f"\n**********{flavor.name}***********")
            print(f"Total mix weight: {flavor.total_mix_weight}")
            print(f"Large Quicks Needed: {flavor.large_quick_needed}")
            print(f"Small Quicks Need: {flavor.small_quick_needed}")
            print(f"Line Mix Need: {flavor.line_mix_needed}")
            print(f"Chicken weight {flavor.chicken_weight}")
            for ingredient in flavor.ingredients:
                print(f"{ingredient.name} weight {ingredient.totaled_weight}")
        if self.error_not_enough_chicken == 1:
            print("\n********** ERROR **********")
            print(f"Total chicken used exceeds chicken on hand!!!")
            print(f"Chicken on hand: {self.chicken_on_hand}")
            print(f"Total chicken used: {math.ceil(self.total_chicken_used)}")
        else:
            print("\n********** Summary **********")
            print(f"Total chicken used: {math.ceil(self.total_chicken_used)}")
            print(f"Chicken remaining: {self.chicken_remaining}")
            print(f"Pans to cook: {math.ceil(self.chicken_to_cook / 10)}")


class Grid:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.cols = 4
        self.rows = 3
        self.cell_width = 1
        self.cell_height = 1
        self.coord = []

    def initialize(self, rows=None, cols=None):
        self.rows = rows if rows is not None else self.rows
        self.cols = cols if cols is not None else self.cols
        self.cell_width = self.coordinator.ui_manager.screen.w // self.cols
        self.cell_height = self.coordinator.ui_manager.screen.h // self.rows
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                x = c * self.cell_width
                y = r * self.cell_height
                row.append((x, y))
            self.coord.append(row)
        return self.coord


class DrawManager:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.registry = []
        self.canvas = None

    def draw_registry(self, registry=None):
        self.update_canvas()
        if registry is None:
            registry = self.registry
        for sprite in registry:
            if isinstance(sprite, list):
                self.draw_registry(sprite)
            elif validate_draw(sprite):
                sprite.draw(self.canvas)

    def update_canvas(self):
        self.canvas = self.coordinator.ui_manager.pygame.canvas
        self.canvas.fill((0,0,0))

    def subscribe_object(self, sprite):
        self.registry.append(sprite)

    def unsubscribe_sprite(self, sprite):
        for r_sprite in self.registry:
            if r_sprite == sprite:
                self.registry.remove(sprite)


class SpriteManager:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.sprites = []

    def update(self):
        for sprite in self.sprites:
            sprite.update()

    def load_namespace_sprites(self, namespace, img_tag=None):
        for attr_value in vars(namespace).values():
            sprite = Sprite(self.coordinator, attr_value.name, attr_value.image_name)
            sprite.state_tag = getattr(attr_value, "state_tag", None)
            sprite.initialize(img_tag)
            attr_value.surface = sprite.surface


class Sprite:
    def __init__(self, coordinator, name, img_name):
        self.coordinator = coordinator
        self.state_tag = None
        self.name = name
        self.img_name = img_name
        self.img_tag = None
        self.x = 0
        self.y = 0
        self.origin_x = 0
        self.origin_y = 0
        self.pos = SimpleNamespace(x=0, y=0, origin_x=0, origin_y=0, center_x=0, center_y=0)
        self.at_home_pos = True
        self.w = 0
        self.h = 0
        self.origin_w = 0
        self.origin_h = 0
        self.at_home_scale = True
        self.surface = None
        self.origin_surface = None
        alpha = 255
        render = True

    def initialize(self, img_tag):
        self.img_tag = img_tag
        self.surface = pygame.image.load(os.path.join(CONSTANTS.IMAGE_DIR, self.img_name))
        self.origin_surface = self.surface
        self.w = self.surface.get_width()
        self.h = self.surface.get_height()
        self.coordinator.draw_manager.subscribe_object(self)

    def update(self):
        print(f"{self.name} updated")

    def draw(self, canvas):
        canvas.blit(self.surface, (self.x, self.y))

    def scale(self, w, h):
        self.w = w
        self.h = h
        self.surface = pygame.transform.scale(self.origin_surface, (w, h))


class AnimationManager:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.lerp_speed = SimpleNamespace(move=.075, scale=.1, alpha=.01)
        self.active_animations = []

    def lerp_move(self, sprite, target_x, target_y):
        lerp_speed = self.lerp_speed.move
        total_dx = target_x - sprite.origin_x
        total_dy = target_y - sprite.origin_y

        dx = target_x - sprite.x
        dy = target_y - sprite.y
        remaining_distance = (dx**2 + dy**2)**0.5
        total_distance = (total_dx ** 2 + total_dy ** 2) ** 0.5

        if remaining_distance < .01 * total_distance:
            print(f"{sprite.name} reached target.")
            sprite.x = target_x
            sprite.y = target_y
            return
        else:
            lerp_speed = self.lerp_speed.move
            if remaining_distance < .1 * total_distance:
                lerp_speed *= 1.5
            elif remaining_distance < .5 * total_distance:
                lerp_speed *= 1.25

        sprite.x += dx * lerp_speed
        sprite.y += dy * lerp_speed

    def lerp_scale(self, sprite, scale):
        lerp_speed = self.lerp_speed.scale
        target_w = sprite.origin_w * scale
        target_h = sprite.origin_h * scale

        dw = target_w - sprite.w
        dh = target_h - sprite.h
        remaining_distance = (dw**2 + dh**2)**0.5
        total_distance = ((target_w - sprite.origin_w)**2 + (target_h - sprite.origin_h)**2)**0.5

        if remaining_distance < .01 * total_distance:
            sprite.w = target_w
            sprite.h = target_h
            return
        else:
            lerp_speed = self.lerp_speed.scale
            if remaining_distance < .1 * total_distance:
                lerp_speed *= 1.5
            elif remaining_distance < .5 * total_distance:
                lerp_speed *= 1.25

        sprite.w += dw * lerp_speed
        sprite.h += dh * lerp_speed
        sprite.surface = pygame.transform.scale(sprite.origin_surface, (int(sprite.w), int(sprite.h)))

    def lerp_alpha(self, sprite, target_a):
        current_alpha = sprite.surface.get_alpha()
        if current_alpha is None:
            current_alpha = 255
        new_alpha = current_alpha + (target_a - current_alpha) * self.lerp_speed.alpha
        if abs(new_alpha - target_a) <= 5:
            new_alpha = target_a
        sprite.surface.set_alpha(int(new_alpha))


class EventManager:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.dragged_sprite = None
        self.clickable_sprites = None

    def initialize(self):
        self.clickable_sprites = [s for s in self.coordinator.draw_manager.registry if hasattr(s, "name") and not isinstance(s, list)]

    def update(self, event):
        self.handle_sprite_movement(event)

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
            touch_x = event.x * self.coordinator.ui_manager.screen.w
            touch_y = event.y * self.coordinator.ui_manager.screen.h
            self.check_image_clicked(touch_x, touch_y)
        elif event.type == pygame.FINGERMOTION:
            touch_x = event.x * self.coordinator.ui_manager.screen.w
            touch_y = event.y * self.coordinator.ui_manager.screen.h
            self.move_sprite(touch_x, touch_y)
        elif event.type == pygame.FINGERUP:
            if self.dragged_sprite:
                self.dragged_sprite = None

    def check_image_clicked(self, x, y):
        for sprite in self.clickable_sprites:
            if sprite.x <= x <= sprite.x + sprite.w and sprite.y <= y <= sprite.y + sprite.h:
                if sprite.state_tag is not None:
                    self.coordinator.state_manager.state = sprite.state_tag
                self.dragged_sprite = sprite

    def move_sprite(self, x, y):
        if self.dragged_sprite:
            self.dragged_sprite.x = x - self.dragged_sprite.w // 2
            self.dragged_sprite.y = y - self.dragged_sprite.h // 2

    def check_button_click(self):
        for sprite in self.clickable_sprites:
            if hasattr(sprite, "img_tag"):
                if sprite.img_tag != "button" and self.coordinator.state_manager.state in sprite.name:
                    print(f"Name: {sprite.name}, Image Tag: {sprite.img_tag}")
                    sprite.home_x = sprite.x
                    sprite.home_y = sprite.y
                    scale = 1.75
                    center_x = self.coordinator.ui_manager.screen.w // 2 - int(sprite.origin_w * scale) // 2
                    center_y = self.coordinator.ui_manager.screen.h // 2 - int(sprite.origin_h * scale) // 2
                    self.coordinator.animation_manager.lerp_scale(sprite, scale)
                    self.coordinator.animation_manager.lerp_move(sprite, center_x, center_y)


class UiManager:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.flavors = []
        self.buttons = []
        self.icons = []
        self.scale = SimpleNamespace(x=0, y=0, image=1, multiplier=1, font=8)
        self.base_resolution = SimpleNamespace(w=0, h=0)
        self.screen = SimpleNamespace(w=0, h=0, short=None, dimensions=None)
        self.resolution_profiles = None
        self.bg = None
        self.buttons = buttons_data
        self.icons = icons_data
        self.bg = SimpleNamespace(name="", surface=None)
        self.resolution_profiles = resolution_profiles
        self.active_profile = None
        self.pygame = SimpleNamespace(canvas=None, screen=None, display_info=None)
        self.center = SimpleNamespace(x=0, y=0)

    def initialize(self):
        self.screen.display_info = pygame.display.Info()
        self.screen.w = self.screen.display_info.current_w
        self.screen.h = self.screen.display_info.current_h
        self.screen.short = min(self.screen.w, self.screen.h)
        self.screen.dimensions = (self.screen.w, self.screen.h)
        self.pygame.screen = pygame.display.set_mode(self.screen.dimensions)
        self.pygame.canvas = pygame.Surface(self.screen.dimensions)
        pygame.display.set_caption("Chicken Salad Production Software")
        self.bg.name = "rainbow_bg.jpg"
        self.load_background()
        self.adjust_resolution()
        self.load_sprites()
        self.scale_sprites()

    def load_background(self):
        self.bg.surface = pygame.image.load(os.path.join(CONSTANTS.IMAGE_DIR, self.bg.name))
        self.bg.surface = pygame.transform.scale(self.bg.surface, self.screen.dimensions)

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

    def load_sprites(self):
        self.coordinator.sprite_manager.load_namespace_sprites(self.buttons, "button")
        self.coordinator.sprite_manager.load_namespace_sprites(self.icons, "icon")

    def scale_sprites(self, registry=None):
        registry = registry if registry is not None else self.coordinator.draw_manager.registry
        for sprite in registry:
            if isinstance(sprite, list):
                self.scale_sprites(sprite)
            elif isinstance(sprite, Sprite):
                w = sprite.w * self.coordinator.ui_manager.scale.image
                h = sprite.h * self.coordinator.ui_manager.scale.image
                sprite.origin_w = w
                sprite.origin_h = h
                sprite.scale(w, h)

    def blit_flavors(self):
        for i, flavor in enumerate(self.flavors):
            row = i // self.coordinator.grid.cols
            col = i % self.coordinator.grid.cols
            flavor.x, flavor.y = self.coordinator.grid.coord[row][col]
            flavor.x += self.coordinator.grid.cell_width // 2 - flavor.image.get_width() // 2
            flavor.y += self.coordinator.grid.cell_height // 2 - flavor.image.get_height() // 2
            self.screen.blit(flavor.image, (flavor.x, flavor.y))

    def update_screen(self):
        self.pygame.screen.fill((0, 0, 0))

    def draw_canvas(self):
        self.pygame.screen.blit(self.pygame.canvas, (0, 0))

    def draw_grid(self):
        cols = self.screen.w // 30
        rows = self.screen.h // 30
        for c in range(cols):
            x = c * 30
            pygame.draw.line(self.pygame.screen, (255, 255, 255), (x, 0), (x, self.screen.h))
        for r in range(rows):
            y = r * 30
            pygame.draw.line(self.pygame.screen, (255, 255, 255), (0, y), (self.screen.w, y))


class StateManager:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.state = "main"

    def update(self):
        self.check_state()

    def check_state(self):
        if self.state == "main":
            _true = True
            # print("main")
        elif self.state == "reach_in":
            _true = True
            # print("reach_in")
        elif self.state == "walk_in":
            _true = True
            # print("walk_in")
        elif self.state == "quick":
            _true = True
            # print("quick")
        elif self.state == "production":
            _true = True
            # print("production")

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


class Background:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.img_name = "bg_border_blue.png"
        self.border_image = None
        self.nine_slice_bg = None
        self.border_thickness = 8
        self.nine_slice = None

    def initialize(self):
        self.border_image = pygame.image.load(os.path.join(CONSTANTS.IMAGE_DIR, self.img_name))
        w = self.coordinator.ui_manager.screen.w
        h = self.coordinator.ui_manager.screen.h
        self.nine_slice_bg = NineSlice(self.border_image, self.border_thickness).render(w, h)
        self.coordinator.draw_manager.subscribe_object(self)

    def draw(self, canvas):
        w = canvas.get_width()
        h = canvas.get_height()

        canvas.blit(self.nine_slice_bg, (0, 0))


class NineSlice:
    def __init__(self, source_surface, border_thickness):
        self.source = source_surface
        self.t = border_thickness
        self.w, self.h = self.source.get_size()

        self.top_left = self.source.subsurface(0, 0, self.t, self.t).copy()
        self.top_right = self.source.subsurface(self.w - self.t, 0, self.t, self.t).copy()
        self.bottom_left = self.source.subsurface(0, self.h - self.t, self.t, self.t).copy()
        self.bottom_right = self.source.subsurface(self.w - self.t, self.h - self.t, self.t, self.t).copy()

        self.top_edge = self.source.subsurface(self.t, 0, self.w - 2*self.t, self.t).copy()
        self.bottom_edge = self.source.subsurface(self.t, self.h - self.t, self.w - 2*self.t, self.t).copy()
        self.right_edge = self.source.subsurface(self.w - self.t, self.t, self.t, self.h - 2*self.t).copy()
        self.left_edge = self.source.subsurface(0, self.t, self.t, self.h - 2*self.t).copy()

        self.center = self.source.subsurface(self.t, self.t, self.w - 2*self.t, self.h - 2*self.t).copy()

    def render(self, target_w, target_h):
        surface = pygame.Surface((target_w, target_h), pygame.SRCALPHA)

        surface.blit(self.top_left, (0, 0))
        surface.blit(self.top_right, (target_w - self.t, 0))
        surface.blit(self.bottom_left, (0, target_h - self.t))
        surface.blit(self.bottom_right, (target_w - self.t, target_h - self.t))

        top_scaled = pygame.transform.scale(self.top_edge, (target_w - 2*self.t, self.t))
        bottom_scaled = pygame.transform.scale(self.bottom_edge, (target_w - 2*self.t, self.t))
        left_scaled = pygame.transform.scale(self.left_edge, (self.t,  target_h - 2*self.t))
        right_scaled = pygame.transform.scale(self.left_edge, (self.t,  target_h - 2*self.t))

        surface.blit(top_scaled, (self.t, 0))
        surface.blit(bottom_scaled, (self.t, target_h - self.t))
        surface.blit(left_scaled, (0, self.t))
        surface.blit(right_scaled, (target_w - self.t, self.t))

        center_scaled = pygame.transform.scale(self.center, (target_w - 2*self.t, target_h - 2*self.t))
        surface.blit(center_scaled, (self.t, self.t))

        return surface


def validate_draw(object):
    return hasattr(object, "draw")