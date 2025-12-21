import math
from ingredients import ingredients_by_name as ingredients


flavor_data_list = {
    "ck": {
        "name": "Cranberry Kelly",
        "large_quick_par": 6,
        "small_quick_par": 6,
        "line_mix_par": 16,
        "ingredients": {ingredients["cranberries"], ingredients["almonds"]},
    },
    "fn": {
        "name": "Fancy Nancy",
        "large_quick_par": 13,
        "small_quick_par": 9,
        "line_mix_par": 28,
        "ingredients": {ingredients["apples"], ingredients["pecans"], ingredients["grapes"]},
    },
    "llb": {
        "name": "Lauryn's Lemon Basil",
        "large_quick_par": 3,
        "small_quick_par": 3,
        "line_mix_par": 12,
        "ingredients": {ingredients["lauryns_mix"]},
    },
    "ff": {
        "name": "Fruity Fran",
        "large_quick_par": 4,
        "small_quick_par": 4,
        "line_mix_par": 12,
        "ingredients": {ingredients["pineapples"], ingredients["pecans"], ingredients["grapes"]},
    },
    "cc": {
        "name": "Classic Carol",
        "large_quick_par": 13,
        "small_quick_par": 9,
        "line_mix_par": 24,
        "ingredients": {ingredients["classic"]},
    },
    "ss": {
        "name": "Sassy Scotty",
        "large_quick_par": 4,
        "small_quick_par": 4,
        "line_mix_par": 16,
        "ingredients": {ingredients["bacon"], ingredients["cheese"], ingredients["ranch"]},
    },
    "oos": {
        "name": "Olivia's Old South",
        "large_quick_par": 4,
        "small_quick_par": 4,
        "line_mix_par": 12,
        "ingredients": {ingredients["sweet_relish"], ingredients["eggs"]},
    },
    "jh": {
        "name": "Jalapeno Holly",
        "large_quick_par": 4,
        "small_quick_par": 4,
        "line_mix_par": 12,
        "ingredients": {ingredients["jalapenos"]},
    },
    "bb": {
        "name": "Buffalo Barclay",
        "large_quick_par": 3,
        "small_quick_par": 3,
        "line_mix_par": 16,
        "ingredients": {ingredients["buffalo"]},
    },
    "bbq": {
        "name": "Barbecue",
        "large_quick_par": 2,
        "small_quick_par": 2,
        "line_mix_par": 8,
        "ingredients": {ingredients["barbecue"]},
    },
    "dc": {
        "name": "Dixie Chick",
        "large_quick_par": 3,
        "small_quick_par": 3,
        "line_mix_par": 12,
        "ingredients": {ingredients["onions"]},
    },
    "kkl": {
        "name": "Kickin' Kay Lynne",
        "large_quick_par": 4,
        "small_quick_par": 4,
        "line_mix_par": 12,
        "ingredients": {ingredients["kickin"]},
    },
}



class Flavor:
    def __init__(self, flavor_data):
        self.name = flavor_data["name"]
        self.large_quick_par = flavor_data["large_quick_par"]
        self.small_quick_par = flavor_data["small_quick_par"]
        self.line_mix_par = flavor_data["line_mix_par"]
        self.totaled_par_weight = 0
        self.calculate_par_weight()
        self.large_quick_on_hand = 0
        self.small_quick_on_hand = 0
        self.line_mix_on_hand = 0
        self.large_quick_needed = 0
        self.small_quick_needed = 0
        self.line_mix_needed = 0
        self.total_mix_weight = 0
        self.ingredients = flavor_data["ingredients"]
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
all_flavors[2].calculate_needed()