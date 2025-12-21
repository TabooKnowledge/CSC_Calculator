ingredient_data_list = [
    {"name": "cranberries",   "weight": .28},
    {"name": "almonds",       "weight": .40},
    {"name": "pecans",        "weight": .27},
    {"name": "grapes",        "weight": .35},
    {"name": "apples",        "weight": .30},
    {"name": "lauryns_mix",  "weight": .20},
    {"name": "pineapples",    "weight": .50},
    {"name": "bacon",         "weight": .28},
    {"name": "ranch",         "weight": .55},
    {"name": "cheese",        "weight": .23},
    {"name": "sweet_relish",  "weight": .65},
    {"name": "eggs",          "weight": .33},
    {"name": "jalapenos",     "weight": .50},
    {"name": "buffalo",       "weight": .50},
    {"name": "barbecue",      "weight": .50},
    {"name": "onions",        "weight": .40},
    {"name": "classic",       "weight": .00},
    {"name": "kickin",       "weight": .00},
]


class Ingredient:
    def __init__(self, ingredient_data):
        self.name = ingredient_data["name"]
        self.weight = ingredient_data["weight"]
        self.totaled_weight = 0


    def total_weight(self, mix_weight):
        self.totaled_weight = round((mix_weight / 4) * self.weight, 2)


def create_ingredient_objects(_all_ingredients_data):
    ingredients = []
    for ingredient_data in _all_ingredients_data:
        new_ingredient = Ingredient(ingredient_data)
        ingredients.append(new_ingredient)

    return ingredients


all_ingredients = create_ingredient_objects(ingredient_data_list)
ingredients_by_name = {ingredient.name: ingredient for ingredient in all_ingredients}