ingredient_data_list = [
    {"Name": "Cranberries",   "Weight": .28},
    {"Name": "Almonds",       "Weight": .40},
    {"Name": "Pecans",        "Weight": .27},
    {"Name": "Grapes",        "Weight": .35},
    {"Name": "Apples",        "Weight": .30},
    {"Name": "Lauryn's Mix",  "Weight": .20},
    {"Name": "Pineapples",    "Weight": .50},
    {"Name": "Bacon",         "Weight": .28},
    {"Name": "Ranch",         "Weight": .55},
    {"Name": "Cheese",        "Weight": .23},
    {"Name": "Sweet Relish",  "Weight": .65},
    {"Name": "Eggs",          "Weight": .33},
    {"Name": "Jalapenos",     "Weight": .50},
    {"Name": "Buffalo",       "Weight": .50},
    {"Name": "Barbecue",      "Weight": .50},
    {"Name": "Onions",        "Weight": .40},
    {"Name": "Classic",       "Weight": .00},
    {"Name": "Kickin'",       "Weight": .00},
]

class Ingredient:
    def __init__(self, ingredient_data):
        self.name = ingredient_data["Name"]
        self.weight = ingredient_data["Weight"]
        self.tallied_weight = 0


    def calculate_weight(self, total_weight):
        self.tallied_weight = round((total_weight / 4) * self.weight, 2)


def create_ingredient_objects(_all_ingredients_data):
    ingredients = []
    for ingredient_data in _all_ingredients_data:
        new_ingredient = Ingredient(ingredient_data)
        ingredients.append(new_ingredient)

    return ingredients


all_ingredients = create_ingredient_objects(ingredient_data_list)
ingredients_by_name = {ingredient.name: ingredient for ingredient in all_ingredients}