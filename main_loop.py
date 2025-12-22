from ingredients import ingredient_data_list, all_ingredients
from flavors import flavor_data_list, all_flavors
from main import TkManager, UiManager, Button, all_resolution_data
from prep_sheet import PrepSheet
from PIL import Image, ImageTk
import os


class Coordinator:
    def __init__(self):
        self.ingredients = all_ingredients
        self.all_ingredients_data = ingredient_data_list
        self.flavors = all_flavors
        self.all_flavor_data = flavor_data_list
        self.tk_manager = -1
        self.ui_manager = -1
        self.w = None
        self.h = None
        self.all_resolution_data = all_resolution_data
        self.prep_sheet = PrepSheet()
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.buttons = []
        self.canvas = -1
        self.bg_image_name = "stacey_sticker.jpg"
        self.bg_img = -1
        self.font_name = "ARIAL.ttf"
        self.font_path = ""
        self.image_path = ""

    def initialize(self):
        self.build_paths()
        self.tk_manager = TkManager()
        self.tk_manager.initialize()
        self.canvas = self.tk_manager.canvas
        self.w = self.tk_manager.w
        self.h = self.tk_manager.h
        self.load_background_image()
        self.tk_manager.initialize_canvas()
        self.ui_manager = UiManager(self.all_resolution_data, self.tk_manager)
        self.ui_manager.initialize_ui()
        self.create_buttons()

    def build_paths(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.font_path = os.path.join(script_dir, "fonts", "arial", self.font_name)
        self.image_path = os.path.join(script_dir, "images")

    def load_background_image(self):
        img = Image.open("images/stacey_sticker.jpg").resize((self.w, self.h))
        self.bg_img = ImageTk.PhotoImage(img)

    def create_buttons(self):
        for i, flavor in enumerate(self.flavors):
            btn = Button(self.tk_manager, self.ui_manager, self.canvas, flavor)
            btn.initialize(i)
            self.buttons.append(btn)

    def run(self):
        self.tk_manager.root.mainloop()


coordinator = Coordinator()
coordinator.initialize()
coordinator.run()