import math
from types import SimpleNamespace
from config import ingredients_data
from ui import Sprite

class Ingredient:
    def __init__(self, coordinator, name, weight):
        self.coordinator = coordinator
        self.name = name
        self.weight = weight
        self.totaled_weight = 0

    def total_weight(self, mix_weight):
        self.totaled_weight = round((mix_weight / 4) * self.weight, 2)

def initialize_ingredients(coordinator):
    for name, weight in ingredients_data.items():
        ingredient = Ingredient(coordinator, name, weight)
        coordinator.ingredients.append(ingredient)


class Flavor:
    def __init__(self, coordinator, flavor_data, ingredients_data):
        self.depth = 0
        self.origin_y = 0
        self.origin_x = 0
        self.center_y = 0
        self.center_x = 0
        self.coordinator = coordinator
        self.data = SimpleNamespace(flavor=flavor_data, ingredients=ingredients_data)
        self.tag = None
        self.type = "flavor_class"
        self.show_details = False
        #Visuals
        self.img_name = None
        self.sprite = None
        self.name = None
        self.text_surface = None
        self.details_window = None
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
        self.text_surface = self.coordinator.ui_manager.font.render(self.name, True, (0,0,0))
        self.store_ingredients()

    def store_ingredients(self):
        for name in self.data.flavor.ingredients:
            for ingredient in self.data.ingredients:
                if ingredient.name == name:
                    self.ingredients.append(ingredient)
                    break

    def load_sprite(self):
        self.sprite = Sprite(self.coordinator, self.name, self.img_name)
        self.sprite.flavor = self
        self.sprite.type = "flavor"
        self.sprite.initialize()

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