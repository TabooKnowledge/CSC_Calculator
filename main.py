import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
from prep_sheet import prep_sheet


all_resolution_data = {
    "android": {
        "base_font_size": 8,
        "font": "Arial",
        "btn_width": 7,
        "btn_height": 3,
        "btn_start_x": .02,
        "btn_start_y": .05,
        "btn_step_y": .25,
        "btn_step_x": .35,
        "btn_wraplength": .2,
        "btn_scale_ratio": 0.1
    },
    "windows": {
        "base_font_size": 15,
        "font": "Arial",
        "btn_width": 15,
        "btn_height": 2,
        "btn_start_x": .04,
        "btn_start_y": .025,
        "btn_step_y": .25,
        "btn_step_x": .4,
        "btn_wraplength": .0,
        "btn_scale_ratio": 0.125
    }
}


class TkManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chicken Salad Production Software")
        self.resolution_data = None
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
        self.label.place(relx=0.5, rely=.0125, anchor="center")

    def initialize_canvas(self):
        self.create_canvas()
        self.create_bg_img()
        self.draw_img_to_canvas()

    def create_canvas(self):
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill="both", expand=True)

    def create_bg_img(self):
        img = Image.open("images/stacey_sticker.jpg").resize((self.w, self.h))
        self.bg_img = ImageTk.PhotoImage(img)

    def draw_img_to_canvas(self):
        self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")
        self.canvas.photo = self.bg_img


class UiManager:
    def __init__(self, all_res_data, _tk_manager):
        self.tk_manager = _tk_manager
        self.base_font_size = 0
        self.font = ""
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
        #self.assign_dimensions()

    def set_resolution_data(self):
        if "ANDROID_ROOT" in os.environ:
            self.resolution_data = self.all_resolution_data["android"]
            self.tk_manager.resolution_data = self.resolution_data
        elif os.name == "nt":
            self.resolution_data = self.all_resolution_data["windows"]
            self.tk_manager.resolution_data = self.resolution_data
        else:
            print("Unsupported OS")
            exit(1)

    def set_ui_properties(self):
        self.base_font_size = self.resolution_data["base_font_size"]
        self.font = tkfont.Font(font=self.font)
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
                            command = lambda f = flavor: on_flavor_click(f))
            self.tk_manager.canvas.create_window(int(current_x * self.tk_manager.w),
                                 int(current_y * self.tk_manager.h),
                                 window=btn, anchor="nw")
           # self.fit_text_to_button(btn, flavor.name, 300)
            self.tk_manager.buttons.append(btn)

    def fit_text_to_button(self, btn, text, max_width_px):
        f = tkfont.Font(font=btn['font'])
        size = f.actual()['size']
        while f.measure(text) > max_width_px and size > 1:
            size -= 1
            f.configure(size = size)
        btn.config(font = f)


class Button:
    def __init__(self, _tk_manager, _ui_manager, canvas, data, font):
        self.tk_manager = _tk_manager
        self.ui_manager = _ui_manager
        self.resolution_data = _tk_manager.resolution_data
        self.font_path = ""
        self.index = 0
        self.x = 0
        self.y = 0
        self.w = self.resolution_data["btn_width"]
        self.h = self.resolution_data["btn_height"]
        self.text = ""
        self.font = font
        self.canvas = canvas
        self.data = data
        self.tag = data.tag
        self.image_name = data.image_name
        self.image_path = ""
        self.image = None
        self.command_func  = None
        self.tk_widget = None

    def build_paths(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.font_path = os.path.join(script_dir, "fonts", "arial", "ARIAL.ttf")
        self.image_path = os.path.join(script_dir, "images", self.image_name)

    def initialize(self, i):
        self.build_paths()
        self.text = self.data.name
        #self.command_func = self.data["command_func"]
        self.assign_position(i)
        self.make_button_image()
        self.create_widget()
        self.create_window()
        self.tk_manager.buttons.append(self)

    def make_button_image(self):
        scrn_w = self.tk_manager.w
        img_w = int(scrn_w * self.resolution_data["btn_scale_ratio"])
        img_h = int(scrn_w * self.resolution_data["btn_scale_ratio"]//1.25)
        img = Image.open(self.image_path).resize((img_w, img_h))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(self.font_path, size=20)
        bbox = draw.textbbox((0, 0), self.text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        img_w, img_h = img.size
        x = (img_w - text_w) // 2
        y = 0
        draw.text((x, y), self.text, font=font, fill="white")
        self.image = ImageTk.PhotoImage(img)

    def create_image(self):
        scrn_w = self.tk_manager.w
        img_w = int(scrn_w * self.resolution_data["btn_scale_ratio"])
        img = Image.open(self.image_name).resize((img_w, img_w))
        #img.resize(img.size)
        self.image = ImageTk.PhotoImage(img)

    def create_widget(self):
        self.tk_widget = tk.Button(
        self.canvas,
            width = self.image.width(),
            height = self.image.height(),
            command = self.on_click,
            image = self.image,
            wraplength = self.image.width(),
    )

    def assign_position(self, i):
        column = (self.ui_manager.btn_step_y * i) // 1
        self.x = (self.ui_manager.btn_start_x + column * self.ui_manager.btn_step_x) * self.tk_manager.w
        self.y = (self.ui_manager.btn_start_y + (self.ui_manager.btn_step_y * i) % 1) * self.tk_manager.h

    def create_window(self):
        self.canvas.create_window(
            self.x,
            self.y,
            window=self.tk_widget,
            anchor="nw"
        )

    def on_click(self):
        print(f"Clicked {self.text}")
        if self.command_func  is not None:
            self.command_func ()



def on_flavor_click(_flavor):
    print(f"Clicked {_flavor.name}")




tk_manager = TkManager()
tk_manager.initialize()
ui_manager = UiManager(all_resolution_data, tk_manager)
ui_manager.initialize_ui()
for i, flavor in enumerate(prep_sheet.all_flavors):
    btn = Button(tk_manager, ui_manager, tk_manager.canvas,flavor,"Arial")
    btn.initialize(i)
tk_manager.root.mainloop()