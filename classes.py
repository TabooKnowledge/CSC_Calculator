from config import CONSTANTS
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
        self.cell_width = self.coordinator.screen.w // self.cols
        self.cell_height = self.coordinator.screen.h // self.rows
        self.coord = []

    def initialize(self, rows=None, cols=None):
        self.rows = rows if rows is not None else self.rows
        self.cols = cols if cols is not None else self.cols
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

    def draw_registry(self, scale=False, registry=None):
        self.update_canvas()
        if registry is None:
            registry = self.registry
        for sprite in registry:
            if isinstance(sprite, list):
                self.draw_registry( False, sprite)
            elif self.validate(sprite):
                if scale:
                    w = sprite.w * self.coordinator.scale.image
                    h = sprite.h * self.coordinator.scale.image
                    sprite.origin_w = w
                    sprite.origin_h = h
                    sprite.scale(w, h)
                else:
                    sprite.draw(self.canvas)


    def update_canvas(self):
        self.canvas = self.coordinator.pygame.canvas
        self.canvas.fill((0,0,0))

    def subscribe_sprite(self, sprite):
        self.registry.append(sprite)

    def unsubscribe_sprite(self, sprite):
        for r_sprite in self.registry:
            if r_sprite == sprite:
                self.registry.remove(sprite)



    @staticmethod
    def validate(value):
        return isinstance(value, Sprite)


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
        self.w = 0
        self.h = 0
        self.origin_w = 0
        self.origin_h = 0
        self.surface = None
        self.origin_surface = None

    def initialize(self, img_tag):
        self.img_tag = img_tag
        self.surface = pygame.image.load(os.path.join(CONSTANTS.IMAGE_DIR, self.img_name))
        self.origin_surface = self.surface
        self.w = self.surface.get_width()
        self.h = self.surface.get_height()
        self.coordinator.draw_manager.subscribe_sprite(self)

    def draw(self, canvas):
        canvas.blit(self.surface, (self.x, self.y))

    def scale(self, w, h):
        self.w = w
        self.h = h
        self.surface = pygame.transform.scale(self.surface, (w, h))

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
