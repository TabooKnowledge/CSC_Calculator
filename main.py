import tkinter as tk
from prep_sheet import prep_sheet
from screeninfo import get_monitors
import math


root = tk.Tk()
root.title("Chicken Salad Production Software")
w = root.winfo_screenwidth()
h = root.winfo_screenheight()
root.geometry(f"{w}x{h}")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
frame = tk.Frame(root)
frame.grid(row=0, column=0, sticky=tk.NSEW)
label = tk.Label(frame, text="Chicken Salad Production Software", font=("Arial", 12))
label.place(relx=0.5, rely=0.05, anchor="center")
buttons = []
base_font_size = max(8, int(h * .02))
button_width = max(5, int(w * .01))
button_height = max (2, int(h * .0025))
print(base_font_size)
print(button_width)
print(button_height)

def on_flavor_click(_flavor):
    print(f"Clicked {_flavor.name}")


btn_step_y = .25
btn_step_x = .4
for i, flavor in enumerate(prep_sheet.all_flavors):
    column = (btn_step_y * i) // 1
    btn_start_x = .05 + column * btn_step_x
    btn_start_y = .05 + (btn_step_y * i) % 1

    btn = tk.Button(frame, text=flavor.name,
                    width=button_width, height=button_height,
                    font=("Arial", base_font_size),
                    command=lambda f=flavor: on_flavor_click(f))
    btn.place(relx=btn_start_x, rely=btn_start_y, anchor="nw")
    buttons.append(btn)


root.mainloop()