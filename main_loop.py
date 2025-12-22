from main import tk_manager as tk
from main import ui_manager as ui
from main import Button


class Coordinator:
    def __init__(self):
        self.tk_manager = None
        self.ui_manager = None
        self.button_creator = None
        self.screen_width = 0
        self.screen_height = 0

    def initialize(self):
        self.tk_manager = tk
        self.ui_manager = ui
        self.button_creator = Button
        self.screen_width = self.tk_manager.w
        self.screen_height = self.tk_manager.h

    def run(self):
        self.tk_manager.root.mainloop()

coordinator = Coordinator()
coordinator.initialize()
coordinator.run()