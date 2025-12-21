import tkinter as tk
from tkinter import font as tkfont
from prep_sheet import prep_sheet
import os


class TkManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chicken Salad Production Software")
        self.w = self.root.winfo_screenwidth()
        self.h = self.root.winfo_screenheight()
        self.root.geometry(f"{self.w}x{self.h}")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.frame = tk.Frame(self.root)
        self.frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.label = tk.Label(self.frame, text="Chicken Salad Production Software", font=("Arial", 12))
        self.label.place(relx=0.5, rely=0.05, anchor="center")
        self.buttons = []


class UiCompiler:
    def __init__(self):
        self.base_font_size = 0
        self.button_width = 0
        self.button_height = 0
        self.btn_step_y = .25
        self.btn_step_x = .4

    def initialize_ui(self, _tk_manager):
        self.assign_ui_scale()
        self.assign_dimensions(_tk_manager)

    def assign_ui_scale(self):
        if "ANDROID_ROOT" in os.environ:
            self.base_font_size = 8
            self.button_width = 7
            self.button_height = 3
            print("Running on Android")
        elif os.name == "nt":
            self.base_font_size = 15
            self.button_width = 15
            self.button_height = 2
            print("Running on Windows")
        print(self.base_font_size)
        print(self.button_width)
        print(self.button_height)

    def assign_dimensions(self, _tk_manager):
        for i, flavor in enumerate(prep_sheet.all_flavors):
            column = (self.btn_step_y * i) // 1
            btn_start_x = .05 + column * self.btn_step_x
            btn_start_y = .05 + (self.btn_step_y * i) % 1

            btn = tk.Button(_tk_manager.frame, text=flavor.name, wraplength=int(_tk_manager.w * .1),
                            width=self.button_width, height=self.button_height,
                            font=("Arial", self.base_font_size),
                            command=lambda f=flavor: on_flavor_click(f))
            btn.place(relx=btn_start_x, rely=btn_start_y, anchor="nw")
            _tk_manager.buttons.append(btn)




def fit_text_to_button(self, btn, text, max_width_px):
    f = tkfont.Font(font=btn['font'])
    size = f.actual()['size']
    while f.measure(text) > max_width_px and size > 1:
        size -= 1
        f.configure(size=size)
    btn.config(font=f)


def on_flavor_click(_flavor):
    print(f"Clicked {_flavor.name}")

tk_manager = TkManager()
ui_compiler = UiCompiler()
ui_compiler.initialize_ui(tk_manager)

tk_manager.root.mainloop()