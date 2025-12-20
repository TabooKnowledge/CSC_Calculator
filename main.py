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

def on_flavor_click(_flavor):
    print(f"Clicked {_flavor.name}")


btn_step_y = .25
btn_step_x = .4
for i, flavor in enumerate(prep_sheet.all_flavors):
    column = (btn_step_y * i) // 1
    btn_start_x = .05 + column * btn_step_x
    btn_start_y = .05 + (btn_step_y * i) % 1

    btn = tk.Button(frame, text=flavor.name,
                    width=15, height=5,
                    font=("Arial", 10),
                    command=lambda f=flavor: on_flavor_click(f))
    btn.place(relx=btn_start_x, rely=btn_start_y, anchor="nw")
    buttons.append(btn)


root.mainloop()