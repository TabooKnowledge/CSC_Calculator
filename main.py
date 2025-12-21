import tkinter as tk
from tkinter import font as tkfont
from prep_sheet import prep_sheet
import os

#Testingthisout
all_resolution_data = {
    "android": {
        "base_font_size": 8,
        "btn_width": 7,
        "btn_height": 3,
        "btn_start_x": .02,
        "btn_start_y": .05,
        "btn_step_y": .25,
        "btn_step_x": .35
    },
    "windows": {
        "base_font_size": 15,
        "btn_width": 15,
        "btn_height": 2,
        "btn_start_x": .04,
        "btn_start_y": .05,
        "btn_step_y": .25,
        "btn_step_x": .4
    }
}


class TkManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chicken Salad Production Software")
        self.w = self.root.winfo_screenwidth()
        self.h = self.root.winfo_screenheight()
        self.root.geometry(f"{self.w}x{self.h}")
        self.root.columnconfigure(0, weight = 1)
        self.root.rowconfigure(0, weight = 1)
        self.frame = tk.Frame(self.root)
        self.frame.grid(row = 0, column = 0, sticky = tk.NSEW)
        self.label = tk.Label(self.frame, text = "Chicken Salad Production Software", font = ("Arial", 12))
        self.label.place(relx = 0.5, rely = 0.025, anchor = "center")
        self.buttons = []



class UiCompiler:
    def __init__(self, all_res_data):
        self.base_font_size = 0
        self.btn_width = 0
        self.btn_height = 0
        self.column = 0
        self.btn_start_x = 0
        self.btn_start_y = 0
        self.btn_step_y = 0
        self.btn_step_x = 0
        self.all_resolution_data = all_res_data
        self.resolution_data = None

    def initialize_ui(self, _tk_manager):
        self.set_resolution_data()
        self.set_ui_properties()
        self.assign_dimensions(_tk_manager)

    def set_resolution_data(self):
        if "ANDROID_ROOT" in os.environ:
            self.resolution_data = self.all_resolution_data["android"]
        elif os.name == "nt":
            self.resolution_data = self.all_resolution_data["windows"]

    def set_ui_properties(self):
        self.base_font_size = self.resolution_data["base_font_size"]
        self.btn_width = self.resolution_data["btn_width"]
        self.btn_height = self.resolution_data["btn_height"]
        self.btn_start_x = self.resolution_data["btn_start_x"]
        self.btn_start_y = self.resolution_data["btn_start_y"]
        self.btn_step_y = self.resolution_data["btn_step_y"]
        self.btn_step_x = self.resolution_data["btn_step_x"]


    def assign_dimensions(self, _tk_manager):
        for i, flavor in enumerate(prep_sheet.all_flavors):
            self.column = (self.btn_step_y * i) // 1
            current_x = self.btn_start_x + self.column * self.btn_step_x
            current_y = self.btn_start_y + (self.btn_step_y * i) % 1

            btn = tk.Button(_tk_manager.frame, text = flavor.name, wraplength = int(_tk_manager.w * .1),
                            width = self.btn_width, height= self.btn_height,
                            font = ("Arial", self.base_font_size),
                            command = lambda f = flavor: on_flavor_click(f))
            btn.place(relx = current_x, rely = current_y, anchor = "nw")
            _tk_manager.buttons.append(btn)




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
ui_compiler = UiCompiler(all_resolution_data)
ui_compiler.initialize_ui(tk_manager)

tk_manager.root.mainloop()