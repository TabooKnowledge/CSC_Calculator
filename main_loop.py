from main import setup_ui


class Coordinator:
    def __init__(self):
        self.tk_manager = None
        self.ui_manager = None
        self.button_creator = None
        self.buttons = None
        self.screen_width = 0
        self.screen_height = 0

    def initialize(self, attributes):
        self.tk_manager = attributes[0]
        self.ui_manager = attributes[1]
        self.buttons = attributes[2]
        self.screen_width = self.tk_manager.w
        self.screen_height = self.tk_manager.h

    def run(self):
        self.tk_manager.root.mainloop()

attributes = setup_ui()
coordinator = Coordinator()
coordinator.initialize(attributes)
coordinator.run()