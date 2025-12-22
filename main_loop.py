from main import TkManager, UiManager, Button, all_resolution_data
from prep_sheet import prep_sheet


class Coordinator:
    def __init__(self):
        self.tk_manager = None
        self.ui_manager = None
        self.button_creator = None
        self.screen_width = 0
        self.screen_height = 0

    def initialize(self, tk, ui):
        self.tk_manager = tk
        self.ui_manager = ui
        self.button_creator = Button
        self.screen_width = self.tk_manager.w
        self.screen_height = self.tk_manager.h

    def run(self):
        self.tk_manager.root.mainloop()

coordinator = Coordinator()
tk_manager = TkManager()
ui_manager = UiManager(all_resolution_data, tk_manager)
coordinator.initialize(tk_manager, ui_manager)
tk_manager.initialize()
ui_manager.initialize_ui()
for i, flavor in enumerate(prep_sheet.all_flavors):
    btn = Button(tk_manager, ui_manager, tk_manager.canvas,flavor)
    btn.initialize(i)
coordinator.run()