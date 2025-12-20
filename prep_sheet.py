from flavors import all_flavors
import math


class PrepSheet:
    def __init__(self):
        self.chicken_on_hand = 140
        self.chicken_par = 160
        self.total_chicken_used = 0
        self.chicken_remaining = 0
        self.chicken_to_cook = 0
        self.all_flavors = all_flavors
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


prep_sheet = PrepSheet()
prep_sheet.calculate_production_numbers()
prep_sheet.print_output()