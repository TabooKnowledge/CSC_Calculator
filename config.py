import os
from types import SimpleNamespace


CONSTANTS = SimpleNamespace()
CONSTANTS.SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONSTANTS.IMAGE_DIR = os.path.join(CONSTANTS.SCRIPT_DIR, "images")
CONSTANTS.SAVE_DIR = os.path.join(CONSTANTS.SCRIPT_DIR, "state")
CONSTANTS.SAVE_FILE = os.path.join(CONSTANTS.SAVE_DIR, "save.json")
CONSTANTS.FRONT_DEPTH = 10000
CONSTANTS.ICON_DEPTH = 2000
CONSTANTS.BUTTON_DEPTH = 1000
CONSTANTS.BACKGROUND_DEPTH = -1000
CONSTANTS.REACH_IN_ORDER = ["Olivia's Old South", "Jalapeño Holly", "Dixie Chick", "Buffalo Barclay", "Sassy Scotty", "Kickin Kay Lynne", "Cranberry Kelli", "Barbie Q", "Lauryn's L. Basil", "Classic Carol", "Fancy Nancy", "Fruity Fran"]
CONSTANTS.QUICK_ORDER = ["Olivia's Old South", "Jalapeño Holly", "Dixie Chick", "Buffalo Barclay", "Sassy Scotty", "Kickin Kay Lynne", "Cranberry Kelli", "Barbie Q", "Lauryn's L. Basil", "Classic Carol", "Fancy Nancy", "Fruity Fran"]
CONSTANTS.WALK_IN_ORDER = ["Olivia's Old South", "Jalapeño Holly", "Dixie Chick", "Buffalo Barclay", "Sassy Scotty", "Kickin Kay Lynne", "Cranberry Kelli", "Barbie Q", "Lauryn's L. Basil", "Classic Carol", "Fancy Nancy", "Fruity Fran"]
CONSTANTS.TRANSPARENT = (255, 0, 255)
CONSTANTS.WINDOW_COLOR = (110,158,179)

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


resolution_profiles = SimpleNamespace(
    small=SimpleNamespace(max_short=600, base_width=360, base_height=640, scale_multiplier=.8, font_size=8, res_type="small"),
    medium=SimpleNamespace(max_short=800, base_width=768, base_height=1024, scale_multiplier=.6, font_size=50, res_type="medium"),
    large=SimpleNamespace(max_short=1000, base_width=1920, base_height=1080, scale_multiplier=.8, font_size=40, res_type="large")
)


flavors_data = SimpleNamespace(
    cranberry_kelli=SimpleNamespace(
        name="Cranberry Kelli", ingredients=["Almonds", "Cranberries"], img_name="cranberry_kelli.png"),
    fancy_nancy=SimpleNamespace(
        name="Fancy Nancy", ingredients=["Apples", "Pecans", "Grapes"], img_name="fancy_nancy.png"),
    frutiy_fran=SimpleNamespace(
        name="Fruity Fran", ingredients=["Pineapples", "Pecans", "Grapes"], img_name="fruity_fran.png"),
    lauryns=SimpleNamespace(
        name="Lauryn's L. Basil", ingredients=["Apples", "Pecans", "Grapes"], img_name="lauryns_lemon_basil.png"),
    classic_carol=SimpleNamespace(
        name="Classic Carol", ingredients=["Classic"], img_name="classic_carol.png"),
    sassy_scotty=SimpleNamespace(
        name="Sassy Scotty", ingredients=["Bacon", "Cheese", "Ranch"], img_name="sassy_scotty.png"),
    olivas_old_south=SimpleNamespace(
        name="Olivia's Old South", ingredients=["Sweet Relish", "Eggs"], img_name="olivias_old_south.png"),
    jalapeno_holly=SimpleNamespace(
        name="Jalapeño Holly", ingredients=["Jalapenos"], img_name="jalapeno_holly.png"),
    buffalo_barclay=SimpleNamespace(
        name="Buffalo Barclay", ingredients=["Buffalo"], img_name="buffalo_barclay.png"),
    barbecue=SimpleNamespace(
        name="Barbie Q", ingredients=["Barbecue"], img_name="barbecue.png"),
    dixie_chick=SimpleNamespace(
        name="Dixie Chick", ingredients=["Onions"], img_name="dixie_chick.png"),
    kickin_kay_lynne=SimpleNamespace(
        name="Kickin Kay Lynne", ingredients=["Kickin"], img_name="kickin_kay_lynne.png"),
)


icons_data =  SimpleNamespace(
            reach_in=SimpleNamespace(name="reach_in",image_name="icon_reach_in.png", state_tag="container_open"),
            quick=SimpleNamespace(name="quick", image_name="icon_quick.png", state_tag="container_open"),
            walk_in=SimpleNamespace(name="walk_in", image_name="icon_walk_in.png", state_tag="container_open"),
)


buttons_data = SimpleNamespace(
            excel=SimpleNamespace(name="excel", image_name="excel_icon.png", state_tag="excel"),
            reach_in=SimpleNamespace(name="reach_in", image_name="button_reach_in_idle.png", state_tag="reach_in"),
            walk_in=SimpleNamespace(name="walk_in", image_name="button_walk_in_idle.png", state_tag="walk_in"),
            quick=SimpleNamespace(name="quick", image_name="button_quick_idle.png", state_tag="quick"),
)

output_box_layouts = {
    "medium":{
        "Large Quick": (118,85),
        "On Hand": (35,0),
        "large_quick_on_hand": (65, 85),
        "Par": (246,0),
        "large_quick_par": (255, 85),

        "Small Quick": (118,285),
        "_On Hand": (35,200),
        "small_quick_on_hand": (65, 290),
        "_Par": (246,200),
        "small_quick_par": (255, 290),

        "Line Pans": (118, 85),
        "__On Hand": (35, 0),
        "line_mix_on_hand": (65, 85),
        "__Par": (246, 0),
        "line_mix_par": (255, 85),
    },
    "large":{
        "Large Quick": (118,85),
        "On Hand": (35,0),
        "large_quick_on_hand": (65, 85),
        "Par": (246,0),
        "large_quick_par": (255, 85),

        "Small Quick": (118,285),
        "_On Hand": (35,200),
        "small_quick_on_hand": (65, 290),
        "_Par": (246,200),
        "small_quick_par": (255, 290),

        "Line Pans": (118, 85),
        "__On Hand": (35, 0),
        "line_mix_on_hand": (65, 85),
        "__Par": (246, 0),
        "line_mix_par": (255, 85),
    }
}

OUTPUT_SCHEMAS = {
    "quick": {
        "row_1_label": "Large Quick",
        "row_1_hand_label": "On Hand",
        "row_1_hand_value": "large_quick_on_hand",
        "row_1_par_label": "Par",
        "row_1_par_value": "large_quick_par",
        "row_2_label": "Small Quick",
        "row_2_hand_label": "_On Hand",
        "row_2_hand_value": "small_quick_on_hand",
        "row_2_par_label": "_Par",
        "row_2_par_value": "small_quick_par",
    },
    "walk_in": {
        "row_1_label": "Cooked Chicken",
        "row_1_hand_label": "cooked_on_hand",
        "row_1_hand_value": "cooked_on_hand_value",
        "row_1_par_label": "cooked_par",
        "row_1_par_value": "cooked_par_value",
        "row_2_label": "Raw Chicken",
        "row_2_hand_label": "raw_on_hand",
        "row_2_hand_value": "raw_on_hand_value",
        "row_2_par_label": "raw_par",
        "row_2_par_value": "raw_par_value",
    },
    "reach_in": {
        "row_1_label": "Line Pans",
        "row_1_hand_label": "__On Hand",
        "row_1_hand_value": "line_mix_on_hand",
        "row_1_par_label": "__Par",
        "row_1_par_value": "line_mix_par",
    },
}

ARROW_SCHEMAS = {
    "medium": {
         "quick": {
            "large_hand_incr_arrow": ((388, 256), "large_quick_on_hand", +1),
            "large_hand_decr_arrow": ((300, 256), "large_quick_on_hand", -1),
            "large_par_incr_arrow":  ((579, 256), "large_quick_par", +1),
            "large_par_decr_arrow":  ((493, 256), "large_quick_par", -1),
            "small_hand_incr_arrow": ((388, 375), "small_quick_on_hand", +1),
            "small_hand_decr_arrow": ((300, 375), "small_quick_on_hand", -1),
            "small_par_incr_arrow":  ((579, 375), "small_quick_par", +1),
            "small_par_decr_arrow":  ((493, 375), "small_quick_par", -1),
        },
        "walk_in": {

        },
        "reach_in": {
            "line_hand_incr_arrow":  ((40, 15), "line_mix_on_hand", +1),
            "line_hand_decr_arrow": ((40, 115), "line_mix_on_hand", -1),
            "line_par_incr_arrow":  ((230, 15), "line_mix_par", +1),
            "line_par_decr_arrow":  ((230, 115), "line_mix_par", -1),
        }
    },
    "large":{
        "quick": {
            "large_hand_incr_arrow": ((40, 15), "large_quick_on_hand", +1),
            "large_hand_decr_arrow": ((40, 115), "large_quick_on_hand", -1),
            "large_par_incr_arrow":  ((230, 15), "large_quick_par", +1),
            "large_par_decr_arrow":  ((230, 115), "large_quick_par", -1),
            "small_hand_incr_arrow": ((40, 218), "small_quick_on_hand", +1),
            "small_hand_decr_arrow": ((40, 318), "small_quick_on_hand", -1),
            "small_par_incr_arrow":  ((230, 218), "small_quick_par", +1),
            "small_par_decr_arrow":  ((230, 318), "small_quick_par", -1),
        },
        "walk_in": {

        },
        "reach_in": {
            "line_hand_incr_arrow":  ((40, 15), "line_mix_on_hand", +1),
            "line_hand_decr_arrow": ((40, 115), "line_mix_on_hand", -1),
            "line_par_incr_arrow":  ((230, 15), "line_mix_par", +1),
            "line_par_decr_arrow":  ((230, 115), "line_mix_par", -1),
        }
    }
}


EDIT_FIELDS = (
    "large_quick_on_hand",
    "small_quick_on_hand",
    "line_mix_on_hand",
    "large_quick_par",
    "small_quick_par",
    "line_mix_par",
)

STATE_FIELDS = {
    "quick":{
        "large_quick_on_hand",
        "small_quick_on_hand",
        "large_quick_par",
        "small_quick_par",
    },
    "reach_in":{
        "line_mix_on_hand",
        "line_mix_par",
    }
}

SECTION_MAP = {
    "small_quick_chick": {
        "flavor": "A",
        "par": "C",
        "on_hand": "D"
    },
    "large_quick_chick": {
        "flavor": "G",
        "par": "I",
        "on_hand": "J"
    },
    "line": {
        "flavor": "N",
        "par": "P",
        "on_hand": "Q"
    }
}

FLAVOR_ROW_MAP = {
    "Barbie Q": 6,
    "Buffalo Barclay": 7,
    "Classic Carol": 8,
    "Cranberry Kelli": 9,
    "Dixie Chick": 10,
    "Fancy Nancy": 11,
    "Fruity Fran": 12,
    "Jalapeño Holly": 13,
    "Kickin Kay Lynne": 14,
    "Lauryn's L. Basil": 15,
    "Olivia's Old South": 17,
    "Sassy Scotty": 18,
}