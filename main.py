import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk
from prep_sheet import prep_sheet
import os


all_resolution_data = {
    "android": {
        "base_font_size": 8,
        "btn_width": 7,
        "btn_height": 3,
        "btn_start_x": .02,
        "btn_start_y": .05,
        "btn_step_y": .25,
        "btn_step_x": .35,
        "btn_wraplength": .15
    },
    "windows": {
        "base_font_size": 15,
        "btn_width": 15,
        "btn_height": 2,
        "btn_start_x": .04,
        "btn_start_y": .05,
        "btn_step_y": .25,
        "btn_step_x": .4,
        "btn_wraplength": .15
    }
}


class TkManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chicken Salad Production Software")
        self.w = self.root.winfo_screenwidth()
        self.h = self.root.winfo_screenheight()
        self.root.geometry(f"{self.w}x{self.h}")
        self.canvas = -1
        self.bg_img = -1
        self.label = -1
        self.buttons = []

    def initialize(self):
        self.initialize_canvas()
        self.label = tk.Label(self.root, text="Chicken Salad Production Software", font=("Arial", 12))
        self.label.place(relx=0.5, rely=0.025, anchor="center")
        self.buttons = []

    def initialize_canvas(self):
        self.create_canvas()
        self.create_bg_img()
        self.draw_img_to_canvas()

    def create_canvas(self):
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill="both", expand=True)

    def create_bg_img(self):
        img = Image.open("stacey_sticker.jpg").resize((self.w, self.h))
        self.bg_img = ImageTk.PhotoImage(img)

    def draw_img_to_canvas(self):
        self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")
        self.canvas.photo = self.bg_img


class UiCompiler:
    def __init__(self, all_res_data, _tk_manager):
        self.tk_manager = _tk_manager
        self.base_font_size = 0
        self.btn_width = 0
        self.btn_height = 0
        self.column = 0
        self.btn_start_x = 0
        self.btn_start_y = 0
        self.btn_step_y = 0
        self.btn_step_x = 0
        self.btn_wraplength = 0
        self.all_resolution_data = all_res_data
        self.resolution_data = None

    def initialize_ui(self):
        self.set_resolution_data()
        self.set_ui_properties()
        self.assign_dimensions()

    def set_resolution_data(self):
        if "ANDROID_ROOT" in os.environ:
            self.resolution_data = self.all_resolution_data["android"]
        elif os.name == "nt":
            self.resolution_data = self.all_resolution_data["windows"]
        else:
            print("Unsupported OS")
            exit(1)

    def set_ui_properties(self):
        self.base_font_size = self.resolution_data["base_font_size"]
        self.btn_width = self.resolution_data["btn_width"]
        self.btn_height = self.resolution_data["btn_height"]
        self.btn_start_x = self.resolution_data["btn_start_x"]
        self.btn_start_y = self.resolution_data["btn_start_y"]
        self.btn_step_y = self.resolution_data["btn_step_y"]
        self.btn_step_x = self.resolution_data["btn_step_x"]
        self.btn_wraplength = self.resolution_data["btn_wraplength"]


    def assign_dimensions(self):
        for i, flavor in enumerate(prep_sheet.all_flavors):
            self.column = (self.btn_step_y * i) // 1
            current_x = self.btn_start_x + self.column * self.btn_step_x
            current_y = self.btn_start_y + (self.btn_step_y * i) % 1

            btn = tk.Button(self.tk_manager.root,
                            text = flavor.name,
                            wraplength = int(self.tk_manager.w * self.btn_wraplength),
                            width = self.btn_width,
                            height= self.btn_height,
                            font = ("Arial", self.base_font_size),
                            anchor = "center",
                            padx = 20,
                            command = lambda f = flavor: on_flavor_click(f))
            self.tk_manager.canvas.create_window(int(current_x * self.tk_manager.w),
                                 int(current_y * self.tk_manager.h),
                                 window=btn, anchor="nw")
            self.fit_text_to_button(btn, flavor.name, 300)
            self.tk_manager.buttons.append(btn)

    def fit_text_to_button(self, btn, text, max_width_px):
        f = tkfont.Font(font=btn['font'])
        size = f.actual()['size']
        while f.measure(text) > max_width_px and size > 1:
            size -= 1
            f.configure(size = size)
        btn.config(font = f)


def on_flavor_click(_flavor):
    print(f"Clicked {_flavor.name}")




tk_manager = TkManager()
tk_manager.initialize()
ui_compiler = UiCompiler(all_resolution_data, tk_manager)
ui_compiler.initialize_ui()
tk_manager.root.mainloop()