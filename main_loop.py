import pygame
import sys
import os
from flavors import all_flavors

all_resolution_data = {
    "android": {
        "image_scale": 0.5,
        "font_size": 8
    },
    "windows": {
        "image_scale": 1,
        "font_size": 8
    },
}

pygame.init()
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(SCRIPT_DIR, "images")


class Coordinator:
    def __init__(self):
        self.font_size = None
        self.image_scale = None
        self.resolution_data = None
        self.grid = None
        self.display_info = None
        self.screen_width = 0
        self.screen_height = 0
        self.screen_dimensions = (0,0)
        self.screen = None
        self.clock = None
        self.fps = 0
        self.running = True
        self.bg_img_name = ""
        self.bg_img = None
        self.flavors = all_flavors

    def initialize(self):
        self.display_info = pygame.display.Info()
        self.screen_width = self.display_info.current_w
        self.screen_height = self.display_info.current_h
        self.screen_dimensions = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(self.screen_dimensions)
        self.set_resolution_data()
        self.scale_images()
        pygame.display.set_caption("Chicken Salad Production Software")
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True
        self.bg_img_name = "stacey_sticker.jpg"
        self.grid = Grid(self)
        self.grid.initialize_grid()
        self.load_background()

    def set_resolution_data(self):
        if "ANDROID_ROOT" in os.environ:
            self.resolution_data = all_resolution_data["android"]
        elif os.name == "nt":
            self.resolution_data = all_resolution_data["windows"]
        else:
            print("Unsupported OS")
            exit(1)
        self.image_scale = self.resolution_data["image_scale"]
        self.font_size = self.resolution_data["font_size"]
        self.scale_images()

    def scale_images(self):
        for flavor in self.flavors:
            flavor.width = flavor.width * self.image_scale
            flavor.height = flavor.height * self.image_scale
            flavor.image = pygame.transform.scale(flavor.image, (int(flavor.width), int(flavor.height)))


    def load_background(self):
        self.bg_img = pygame.image.load(os.path.join(IMAGE_DIR, self.bg_img_name))
        scaled_width = self.bg_img.get_width() * self.image_scale
        scaled_height = self.bg_img.get_height() * self.image_scale
        self.bg_img = pygame.transform.scale(self.bg_img, size = (scaled_width,scaled_height))


    def set_scaled_w_h(self, w, h):
        return w * self.image_scale, h * self.image_scale

    def blit_flavors(self):
        for i, flavor in enumerate(self.flavors):
            row = i // self.grid.cols
            col = i % self.grid.cols
            flavor.x, flavor.y = self.grid.coord[row][col]
            flavor.x += self.grid.cell_width // 2 - flavor.image.get_width() // 2
            flavor.y += self.grid.cell_height // 2 - flavor.image.get_height() // 2
            self.screen.blit(flavor.image,(flavor.x,flavor.y))

    def main_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            self.screen.fill((0,0,0))
            self.screen.blit(self.bg_img,(0,0))
            self.blit_flavors()
            pygame.display.flip()
            self.clock.tick(self.fps)


class Grid:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.cols = 4
        self.rows = 3
        self.cell_width = self.coordinator.screen_width // self.cols
        self.cell_height = self.coordinator.screen_height // self.rows
        self.coord = []

    def initialize_grid(self):
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                x = c * self.cell_width
                y = r * self.cell_height
                row.append((x, y))
            self.coord.append(row)
        return self.coord


coordinator = Coordinator()
coordinator.initialize()
coordinator.main_loop()
pygame.quit()
sys.exit()


