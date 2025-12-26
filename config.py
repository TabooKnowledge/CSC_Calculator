import os
from types import SimpleNamespace

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


resolution_profiles = SimpleNamespace(
    small=SimpleNamespace(max_short=600, base_width=360, base_height=640, scale_multiplier=.8, font_size=8),
    medium=SimpleNamespace(max_short=800, base_width=768, base_height=1024, scale_multiplier=.7, font_size=12),
    large=SimpleNamespace(max_short=1000, base_width=1920, base_height=1080, scale_multiplier=.8, font_size=16)
)


flavors_data = SimpleNamespace(
    cranberry_kelli=SimpleNamespace(
        name="Cranberry Kelli", ingredients=["Almonds", "Cranberries"], img_name="cranberry_kelli.png"),
    fancy_nancy=SimpleNamespace(
        name="Fancy Nancy", ingredients=["Apples", "Pecans", "Grapes"], img_name="fancy_nancy.png"),
    frutiy_fran=SimpleNamespace(
        name="Fruity Fran", ingredients=["Pineapples", "Pecans", "Grapes"], img_name="fruity_fran.png"),
    lauryns=SimpleNamespace(
        name="Lauryn's Lemon Basil", ingredients=["Apples", "Pecans", "Grapes"], img_name="lauryns_lemon_basil.png"),
    classic_carol=SimpleNamespace(
        name="Classic Carol", ingredients=["Classic"], img_name="classic_carol.png"),
    sassy_scotty=SimpleNamespace(
        name="Sassy Scotty", ingredients=["Bacon", "Cheese", "Ranch"], img_name="sassy_scotty.png"),
    olivas_old_south=SimpleNamespace(
        name="Olivia's Old South", ingredients=["Sweet Relish", "Eggs"], img_name="olivias_old_south.png"),
    jalapeno_holly=SimpleNamespace(
        name="Jalapeno Holly", ingredients=["Jalapenos"], img_name="jalapeno_holly.png"),
    buffalo_barclay=SimpleNamespace(
        name="Buffalo Barclay", ingredients=["Buffalo"], img_name="buffalo_barclay.png"),
    barbecue=SimpleNamespace(
        name="Barbecue", ingredients=["Barbecue"], img_name="barbecue.png"),
    dixie_chick=SimpleNamespace(
        name="Dixie Chick", ingredients=["Onions"], img_name="dixie_chick.png"),
    kickin_kay_lynne=SimpleNamespace(name="Kickin' Kay Lynne", ingredients=["Kickin"], img_name="kickin_kay_lynne.png"),
)


icons_data =  SimpleNamespace(
            reach_in=SimpleNamespace(name="icon_reach_in",image_name="icon_reach_in.png"),
            walk_in=SimpleNamespace(name="icon_quick", image_name="icon_quick.png"),
            quick=SimpleNamespace(name="icon_walk_in", image_name="icon_walk_in.png"),
)


buttons_data = SimpleNamespace(
            production=SimpleNamespace(name="button_production", image_name="button_production_idle.png", state_tag="production"),
            reach_in=SimpleNamespace(name="button_reach_in", image_name="button_reach_in_idle.png", state_tag="reach_in"),
            walk_in=SimpleNamespace(name="button_walk_in", image_name="button_walk_in_idle.png", state_tag="walk_in"),
            quick=SimpleNamespace(name="button_quick", image_name="button_quick_idle.png", state_tag="quick"),
)
