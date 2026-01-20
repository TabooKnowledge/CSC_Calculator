import math
import os
from openpyxl import load_workbook
from datetime import datetime
from types import SimpleNamespace
from config import ingredients_data, CONSTANTS, SECTION_MAP, FLAVOR_ROW_MAP

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
    def __init__(self, coordinator, flavor_data):
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
        self.recalculate = False
        self.chicken_weight = 0
        self.large_quick_par = 0
        self.small_quick_par = 0
        self.line_mix_par = 0
        self.line_mix_par_lbs = 0
        self.totaled_par_weight = 0
        self.large_quick_on_hand = 0
        self.small_quick_on_hand = 0
        self.line_mix_on_hand = 0
        self.line_mix_on_hand_lbs = 0
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
            for ingredient in self.coordinator.ingredients:
                if ingredient.name == name:
                    self.ingredients.append(ingredient)
                    break

    def load_sprite(self):
        self.sprite = Sprite(self.coordinator, self.name, self.img_name)
        self.sprite.flavor = self
        self.sprite.type = "flavor"
        self.sprite.initialize()

    def calculate(self):
        self.calculate_par_weight()
        self.calculate_needed()
        self.coordinator.prep_sheet.calculate_production_numbers(output=False)
        self.recalculate = False
        self.coordinator.state_store.save_state()

    def calculate_par_weight(self):
        self.line_mix_on_hand_lbs = self.line_mix_on_hand*4
        self.line_mix_par_lbs = self.line_mix_par*4
        self.totaled_par_weight = math.ceil(self.large_quick_par + self.small_quick_par / 2 + self.line_mix_par_lbs)

    def calculate_needed(self):
        self.calculate_prep_numbers()
        self.calculate_total_mix_weight()

    def calculate_prep_numbers(self):
        self.large_quick_needed = max(0, self.large_quick_par - self.large_quick_on_hand)
        self.small_quick_needed = max(0, self.small_quick_par - self.small_quick_on_hand)
        self.line_mix_needed = max(0, self.line_mix_par_lbs - self.line_mix_on_hand_lbs)

    def calculate_total_mix_weight(self):
        on_hand = self.large_quick_on_hand + self.small_quick_on_hand / 2 + self.line_mix_on_hand_lbs
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
        self.chicken_on_hand = 160
        self.chicken_par = 160
        self.total_chicken_used = 0
        self.chicken_remaining = 0
        self.chicken_to_cook = 0
        self.all_flavors = []
        self.flavors_by_name = None
        self.kickn_flavors = ["Jalapeno Holly", "Buffalo Barclay", "Sassy Scotty"]
        self.error_not_enough_chicken = False
        self.section_map = SECTION_MAP
        self.flavor_row_map = FLAVOR_ROW_MAP
        self.xl_path = "excel/production_sheet.xlsx"
        self.save_path = "excel/production_output.xlsx"
        self.workbook = load_workbook(self.xl_path, data_only=False)
        self.worksheet = self.workbook["Production Guide"]

    def initialize(self):
        self.all_flavors = build_flavor_set(self.coordinator, None)
        self.flavors_by_name = {f.name: f for f in self.all_flavors}
        for icon in self.coordinator.ui_manager.icons_list:
            ob = icon.details_window.output_box
            ob.flavors_by_name = self.flavors_by_name

    def calculate_production_numbers(self, output=True):
        self.total_chicken_used = 0
        kickin = self.flavors_by_name["Kickin Kay Lynne"]
        kickin.calculate_total_mix_weight()
        kickin_weight = kickin.total_mix_weight

        for flavor in self.all_flavors:
            if flavor.name == "Kickin Kay Lynne":
                continue
            if flavor.name in self.kickn_flavors:
                flavor.calculate_total_mix_weight()
                flavor.total_mix_weight += kickin_weight / 3
                flavor.total_ingredient_weight()
            weight = flavor.total_mix_weight
            quarter_weight = weight / 4
            flavor.chicken_weight = round(weight - (quarter_weight * flavor.totaled_ingredient_weight), 2)
            self.total_chicken_used += flavor.chicken_weight
        if self.total_chicken_used < self.chicken_on_hand:
            self.chicken_remaining = self.chicken_on_hand - math.ceil(self.total_chicken_used)
            self.chicken_to_cook = self.chicken_par - self.chicken_remaining
        else:
            self.error_not_enough_chicken = True
        if output:
            self.print_output()
            self.export_to_excel()

    def export_to_excel(self):
        for section, cols in self.section_map.items():
            for name, flavor in self.flavors_by_name.items():
                row = self.flavor_row_map.get(name)
                if row is None:
                    continue

                if section == "small_quick_chick":
                    par_value = flavor.small_quick_par
                    on_hand_value = flavor.small_quick_on_hand
                elif section == "large_quick_chick":
                    par_value = flavor.large_quick_par
                    on_hand_value = flavor.large_quick_on_hand
                elif section == "line":
                    par_value = flavor.line_mix_par
                    on_hand_value = flavor.line_mix_on_hand
                else:
                    continue

                self.worksheet[f"{cols['par']}{row}"].value = par_value
                self.worksheet[f"{cols['on_hand']}{row}"].value = on_hand_value

        os.makedirs("exports", exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d")
        out_path = f"exports/production_{stamp}.xlsx"
        self.workbook.save(out_path)
        return out_path


    def print_output(self):
        for name, flavor in self.flavors_by_name.items():
            print(f"\n**********{flavor.name}***********")
            print(f"Total mix weight: {flavor.total_mix_weight}")
            print(f"Large Quicks Needed: {flavor.large_quick_needed}")
            print(f"Small Quicks Need: {flavor.small_quick_needed}")
            print(f"Line Mix Need: {flavor.line_mix_needed}")
            print(f"Chicken weight {flavor.chicken_weight}")
            for ingredient in flavor.ingredients:
                print(f"{ingredient.name} weight {ingredient.totaled_weight}")
        if self.error_not_enough_chicken:
            print("\n********** ERROR **********")
            print(f"Total chicken used exceeds chicken on hand!!!")
            print(f"Chicken on hand: {self.chicken_on_hand}")
            print(f"Total chicken used: {math.ceil(self.total_chicken_used)}")
            self.error_not_enough_chicken = False
        else:
            print("\n********** Summary **********")
            print(f"Total chicken used: {math.ceil(self.total_chicken_used)}")
            print(f"Chicken remaining: {self.chicken_remaining}")
            print(f"Pans to cook: {math.ceil(self.chicken_to_cook / 10)}")


def build_flavor_set(coordinator, icon_name) -> list ["Flavor"]:
    if icon_name == "reach_in":
        keys = CONSTANTS.REACH_IN_ORDER
    elif icon_name == "quick":
        keys = CONSTANTS.QUICK_ORDER
    elif icon_name == "walk_in":
        keys = CONSTANTS.WALK_IN_ORDER
    else:
        keys = CONSTANTS.REACH_IN_ORDER

    flavors = []
    sprites = []
    flavors_by_name = {v.name: v for v in vars(coordinator.data.flavors).values()}
    for key in keys:
        attr_value = flavors_by_name.get(key)
        if not attr_value:
            continue
        f = Flavor(coordinator, attr_value)
        f.initialize()
        f.load_sprite()
        f.sprite.render = False
        sprites.append(f.sprite)
        flavors.append(f)
    coordinator.ui_manager.scale_sprites(sprites)
    return flavors


