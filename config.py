import os
from types import SimpleNamespace
import os

CONSTANTS = SimpleNamespace()
CONSTANTS.SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONSTANTS.IMAGE_DIR = os.path.join(CONSTANTS.SCRIPT_DIR, "images")


ingredients_data = {
    "Cranberries": .28,
    "Almonds": .40,
    "Pecans": .27,
    "Grapes": .35,
    "Apples": .30,
    "Lauryns Mix": .20,
    "Pineapples": .50,
    "Bacon": .28,
    "Ranch": .55,
    "Cheese": .23,
    "Sweet Relish": .65,
    "Eggs": .33,
    "Jalapenos": .50,
    "Buffalo": .50,
    "Barbecue": .50,
    "Onions": .40,
    "Classic": .00,
    "Kickin": .00,
}


flavors_data = {
    "ck": {
        "tag": "flavor_dict",
        "name": "Cranberry Kelli",
        "large_quick_par": 6,
        "small_quick_par": 6,
        "line_mix_par": 16,
        "ingredients_names": ["Cranberries", "Almonds"],
        "image_name": "cranberry_kelli.png",
    },
    "fn": {
        "tag": "flavor_dict",
        "name": "Fancy Nancy",
        "large_quick_par": 13,
        "small_quick_par": 9,
        "line_mix_par": 28,
        "ingredients_names": ["Apples", "Pecans", "Grapes"],
        "image_name": "fancy_nancy.png",
    },
    "llb": {
        "tag": "flavor_dict",
        "name": "Lauryn's Lemon Basil",
        "large_quick_par": 3,
        "small_quick_par": 3,
        "line_mix_par": 12,
        "ingredients_names": ["Lauryns Mix"],
        "image_name": "lauryns_lemon_basil.png",
    },
    "ff": {
        "tag": "flavor_dict",
        "name": "Fruity Fran",
        "large_quick_par": 4,
        "small_quick_par": 4,
        "line_mix_par": 12,
        "ingredients_names": ["Pineapples", "Pecans", "Grapes"],
        "image_name": "fruity_fran.png",
    },
    "cc": {
        "tag": "flavor_dict",
        "name": "Classic Carol",
        "large_quick_par": 13,
        "small_quick_par": 9,
        "line_mix_par": 24,
        "ingredients_names": ["Classic"],
        "image_name": "classic_carol.png",
    },
    "ss": {
        "tag": "flavor_dict",
        "name": "Sassy Scotty",
        "large_quick_par": 4,
        "small_quick_par": 4,
        "line_mix_par": 16,
        "ingredients_names": ["Bacon", "Cheese", "Ranch"],
        "image_name": "sassy_scotty.png",
    },
    "oos": {
        "tag": "flavor_dict",
        "name": "Olivia's Old South",
        "large_quick_par": 4,
        "small_quick_par": 4,
        "line_mix_par": 12,
        "ingredients_names": ["Sweet Relish", "Eggs"],
        "image_name": "olivias_old_south.png",
    },
    "jh": {
        "tag": "flavor_dict",
        "name": "Jalapeno Holly",
        "large_quick_par": 4,
        "small_quick_par": 4,
        "line_mix_par": 12,
        "ingredients_names": ["Jalapenos"],
        "image_name": "jalapeno_holly.png",
    },
    "bb": {
        "tag": "flavor_dict",
        "name": "Buffalo Barclay",
        "large_quick_par": 3,
        "small_quick_par": 3,
        "line_mix_par": 16,
        "ingredients_names": ["Buffalo"],
        "image_name": "buffalo_barclay.png",

    },
    "bbq": {
        "tag": "flavor_dict",
        "name": "Barbecue",
        "large_quick_par": 2,
        "small_quick_par": 2,
        "line_mix_par": 8,
        "ingredients_names": ["Barbecue"],
        "image_name": "barbecue.png",
    },
    "dc": {
        "tag": "flavor_dict",
        "name": "Dixie Chick",
        "large_quick_par": 3,
        "small_quick_par": 3,
        "line_mix_par": 12,
        "ingredients_names": ["Onions"],
        "image_name": "dixie_chick.png",
    },
    "kkl": {
        "tag": "flavor_dict",
        "name": "Kickin' Kay Lynne",
        "large_quick_par": 4,
        "small_quick_par": 4,
        "line_mix_par": 12,
        "ingredients_names": ["Kickin"],
        "image_name": "kickin_kay_lynne.png",
    },
}


resolution_profiles = {
    "small":  {"max_short": 600,          "base_width":  360, "base_height": 640, "font_size": 8},
    "medium": {"max_short": 900,          "base_width":  768, "base_height": 640, "font_size": 12},
    "large":  {"max_short": float('inf'), "base_width": 1920, "base_height": 640, "font_size": 16},
}
