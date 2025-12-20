import math
from ingredients import ingredients_by_name as ingredients


flavor_data_list = {
    "CK": {
        "Name": "Cranberry Kelly",
        "Large Quick Par": 6,
        "Small Quick Par": 6,
        "Line Mix Par": 16,
        "Ingredients": {ingredients["Cranberries"], ingredients["Almonds"]}
    },
    "FN": {
        "Name": "Fancy Nancy",
        "Large Quick Par": 13,
        "Small Quick Par": 9,
        "Line Mix Par": 28,
        "Ingredients": {ingredients["Apples"], ingredients["Pecans"], ingredients["Grapes"]}
    },
    "LLB": {
        "Name": "Lauryn's Lemon Basil",
        "Large Quick Par": 3,
        "Small Quick Par": 3,
        "Line Mix Par": 12,
        "Ingredients": {ingredients["Lauryn's Mix"]},
    },
    "FF": {
        "Name": "Fruity France",
        "Large Quick Par": 4,
        "Small Quick Par": 4,
        "Line Mix Par": 12,
        "Ingredients": {ingredients["Pineapples"], ingredients["Pecans"], ingredients["Grapes"]},
    },
    "CC": {
        "Name": "Classic Carol",
        "Large Quick Par": 13,
        "Small Quick Par": 9,
        "Line Mix Par": 24,
        "Ingredients": {ingredients["Classic"]},
    },
    "SS": {
        "Name": "Sass Scotty",
        "Large Quick Par": 4,
        "Small Quick Par": 4,
        "Line Mix Par": 16,
        "Ingredients": {ingredients["Bacon"], ingredients["Cheese"], ingredients["Ranch"]},
    },
    "OOS": {
        "Name": "Olivia's Old South",
        "Large Quick Par": 4,
        "Small Quick Par": 4,
        "Line Mix Par": 12,
        "Ingredients": {ingredients["Sweet Relish"], ingredients["Eggs"]},
    },
    "JH": {
        "Name": "Jalapeno Holly",
        "Large Quick Par": 4,
        "Small Quick Par": 4,
        "Line Mix Par": 12,
        "Ingredients": {ingredients["Jalapenos"]},

    },
    "BB": {
        "Name": "Buffalo Barclay",
        "Large Quick Par": 3,
        "Small Quick Par": 3,
        "Line Mix Par": 16,
        "Ingredients": {ingredients["Buffalo"]},
    },
    "BBQ": {
        "Name": "Barbecue",
        "Large Quick Par": 2,
        "Small Quick Par": 2,
        "Line Mix Par": 8,
        "Ingredients": {ingredients["Barbecue"]},
    },
    "DC": {
        "Name": "Dixie Chick",
        "Large Quick Par": 3,
        "Small Quick Par": 3,
        "Line Mix Par": 12,
        "Ingredients": {ingredients["Onions"]},
    },
    "KKL": {
        "Name": "Kickin' Kay Lynne",
        "Large Quick Par": 4,
        "Small Quick Par": 4,
        "Line Mix Par": 12,
        "Ingredients": {ingredients["Kickin'"]},
    }
}


class Flavor:
    def __init__(self, flavor_data):
        self.name = flavor_data["Name"]
        self.large_quick_par = flavor_data["Large Quick Par"]
        self.small_quick_par = flavor_data["Small Quick Par"]
        self.line_mix_par = flavor_data["Line Mix Par"]
        self.totaled_par_weight = 0
        self.calculate_par_weight()
        self.large_quick_on_hand = 0
        self.small_quick_on_hand = 0
        self.line_mix_on_hand = 0
        self.large_quick_needed = 0
        self.small_quick_needed = 0
        self.line_mix_needed = 0
        self.total_mix_weight = 0
        self.ingredients = flavor_data["Ingredients"]
        self.totaled_ingredient_weight = 0


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


def create_flavor_objects(_all_flavor_data):
    flavors = []
    for flavor_data in _all_flavor_data.values():
        flavors.append(Flavor(flavor_data))
    return flavors


all_flavors = create_flavor_objects(flavor_data_list)
flavors_by_name = {flavor.name: flavor for flavor in all_flavors}
all_flavors[2].calculate_prep_numbers()