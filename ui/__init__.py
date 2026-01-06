import os
import pygame
from types import SimpleNamespace
from config import CONSTANTS, output_box_layouts, OUTPUT_SCHEMAS, ARROW_SCHEMAS, EDIT_FIELDS


class DrawManager:
    def __init__(self, coordinator):
        self.debug_canvas = None
        self.coordinator = coordinator
        self.registry = []
        self.canvas = None
        self.show_flavors = False

    def draw_registry(self, registry=None):
        self.update_canvas()
        registry = registry if registry is not None else self.registry
        registry.sort(key=lambda s: getattr(s, "depth", 0))
        for sprite in registry:
            if sprite.render:
                if getattr(sprite, "flavor", None):
                    self.draw_text_surface(sprite)
                sprite.update()
                sprite.draw(self.canvas)

    def update_canvas(self):
        self.coordinator.ui_manager.pygame.dynamic_canvas.fill(CONSTANTS.TRANSPARENT)
        self.canvas = self.coordinator.ui_manager.pygame.dynamic_canvas
        self.coordinator.ui_manager.pygame.debug_canvas.fill(CONSTANTS.TRANSPARENT)
        self.debug_canvas = self.coordinator.ui_manager.pygame.debug_canvas

    def draw_text_surface(self, sprite):
        sprite_center_x = sprite.x + sprite.w // 2
        t_x = sprite_center_x - sprite.flavor.text_surface.get_width() // 2
        t_y = sprite.y + sprite.h
        self.coordinator.ui_manager.pygame.dynamic_canvas.blit(sprite.flavor.text_surface, (t_x, t_y))

    def subscribe(self, sprite):
        self.registry.append(sprite)

    def unsubscribe(self, sprite):
        for r_sprite in self.registry:
            if r_sprite == sprite:
                self.registry.remove(sprite)


class Sprite:
    def __init__(self, coordinator, name, img_name):
        self.is_arrow = False
        self.arrow = None
        self.flavor = None
        self.icon = None
        self.origin_depth = 0
        self.depth = 0
        self.idle_focused = False
        self.coordinator = coordinator
        self.type = None
        self.name = name
        self.img_name = img_name
        self.img_tag = None
        self.x = 0
        self.y = 0
        self.origin_x = 0
        self.origin_y = 0
        self.center_x = 0
        self.center_y = 0
        self.pos = SimpleNamespace(x=0, y=0, origin_x=0, origin_y=0, center_x=0, center_y=0)
        self.focused = False
        self.w = 0
        self.h = 0
        self.origin_w = 0
        self.origin_h = 0
        self.focused_scale = self.coordinator.ui_manager.focused_scale
        self.surface = None
        self.origin_surface = None
        self.at_home = True
        self.moving_home = False
        self.alpha = 255
        self.render = True

    def initialize(self):
        self.surface = pygame.image.load(os.path.join(CONSTANTS.IMAGE_DIR, self.img_name)).convert()
        self.origin_surface = self.surface
        self.w = self.surface.get_width()
        self.h = self.surface.get_height()
        self.coordinator.draw_manager.subscribe(self)

    def update(self):
        if self.focused and not self.moving_home:
            self.center_self()
        elif self.moving_home:
            self.return_home()

    def center_self(self):
        if not self.idle_focused:
            self.coordinator.event_manager.sprite_transitioning = True

            scale_done = self.coordinator.animation_manager.lerp_scale(self, self.focused_scale, self.focused_scale)
            move_done = self.move_to_window()

            if scale_done and move_done:
                if self.icon is not None:
                    self.icon.show_contents = True#Altered in EventManager.unfocus_current_icon, Checked in Icon
                self.coordinator.event_manager.sprite_transitioning = False
                self.idle_focused = True
                self.at_home = False
                self.moving_home = False
                self.coordinator.event_manager.transition_tag = None

    def move_to_window(self):
        if self.type == "flavor":
            details_window = self.icon.details_window
            if self.coordinator.ui_manager.active_profile.res_type == "medium":
                y = details_window.y - details_window.max_h + self.h // 4
                x = details_window.x + self.w // 8
            else:
                x = (details_window.x - details_window.max_w + self.w // 4)
                y = self.icon.sprite.y + self.h // 8
                self.coordinator.event_manager.transition_tag = "flavor"
            return self.coordinator.animation_manager.lerp_move(self, x, y)
        else:
            self.coordinator.event_manager.transition_tag = "icon"
            return self.coordinator.animation_manager.lerp_move(self, self.center_x, self.center_y)

    def return_home(self):
        scale_done = self.coordinator.animation_manager.lerp_scale(self, 1, 1)
        move_done = self.coordinator.animation_manager.lerp_move(self, self.origin_x, self.origin_y)

        if scale_done and move_done:
            self.depth = self.origin_depth
            self.idle_focused = False
            self.at_home = True
            self.moving_home = False

    def draw(self, canvas):
        canvas.blit(self.surface, (self.x, self.y))

    def scale(self, w, h):
        self.w = w
        self.h = h
        self.surface = pygame.transform.scale(self.origin_surface, (w, h))


class Icon:
    def __init__(self, coordinator, sprite, name):
        self.coordinator = coordinator
        self.sprite = sprite
        self.name = name
        self.sprite.initialize()
        self.contents = None
        self.grid = None
        self.show_contents = False
        self.details_window = None

    def populate_content(self, content: list):
        if not isinstance(content, list):
            return
        for item in content:
            item.sprite.center_y = (self.coordinator.ui_manager.screen.h // 3 -
                                    int(item.sprite.origin_h * self.coordinator.ui_manager.focused_scale) // 2)
        self.contents = content

    def setup_grid(self):
        self.grid = Grid()
        origin_x = self.sprite.center_x
        origin_y = self.sprite.center_y
        rows = 4
        cols = 3
        cell_width = (self.sprite.origin_w * self.sprite.focused_scale // cols)
        cell_height = (self.sprite.origin_h * self.sprite.focused_scale // rows)
        self.grid.create_grid((origin_x, origin_y), cell_width, cell_height, rows, cols)

    def position_content(self):
        for i, c in enumerate(self.contents):
            s = c.sprite
            s.icon = self
            s.alpha = 0
            s.surface.set_alpha(0)
            row = i // self.grid.cols
            col = i % self.grid.cols
            s.x, s.y = self.grid.cells[row][col]
            s.x = s.x + self.grid.cell_width // 2 - s.w // 2
            s.y = s.y + self.grid.cell_height // 2 - s.h // 2
            s.origin_x, s.origin_y = s.x, s.y

    def toggle_show_contents(self):
        for c in self.contents:
            sprite = c.sprite
            if self.show_contents:
                self.details_window.output_box.render_arrows(True)
                sprite.render = True
                if sprite.alpha != 255:
                    self.coordinator.animation_manager.lerp_alpha(sprite, 255)
                sprite.depth = CONSTANTS.FRONT_DEPTH + 1
            else:
                self.details_window.output_box.render_arrows(False)
                sprite.render = False
                sprite.alpha = 0
                sprite.surface.set_alpha(sprite.alpha)


class DetailsWindow:
    def __init__(self, icon):
        self.icon = icon
        self.name = "details_window"
        self.img_name = "details_window.png"
        self.grid = Grid()
        self.w = 0
        self.max_w = 0
        self.min_w = 0
        self.h = 0
        self.max_h = 0
        self.min_h = 0
        self.x = 0
        self.y = 0
        self.thickness = 8
        self.buffer = 15
        self.sprite = None
        self.nineslice_source = None
        self.scale = .55
        self.last_size = 0
        self.active = False
        self.close = False
        self.output_box = None
        self.output_x = 0
        self.output_y = 0
        self.res_type = None
        self.depth = CONSTANTS.FRONT_DEPTH
        self.render = False

    def init(self):
        ui_manager = self.icon.coordinator.ui_manager
        sprite = self.icon.sprite
        max_window_w = sprite.w * ui_manager.focused_scale * self.scale
        max_window_h = sprite.h * ui_manager.focused_scale * self.scale
        self.res_type = ui_manager.active_profile.res_type

        if self.res_type == "medium":
            self.w = sprite.w * ui_manager.focused_scale
            self.h = self.thickness * 2
            self.max_h = max_window_h
            self.x = sprite.center_x
            self.y = sprite.center_y
        else:
            self.w = self.thickness * 2
            self.h = sprite.h * ui_manager.focused_scale
            self.max_w = max_window_w
            self.x = sprite.center_x
            self.y = sprite.center_y

        self.create_window()
        self.icon.coordinator.draw_manager.subscribe(self)

    def update(self):
        if self.active:
            self.sprite.render = True
            self.roll_window()
            if self.icon.sprite.idle_focused:
                if not self.icon.sprite.moving_home:
                    self.render = True
                    self.output_box.update()
                else:
                    self.render = False

    def create_window(self):
        self.sprite = Sprite(self.icon.coordinator, "details_window", self.img_name)
        self.sprite.initialize()
        self.nineslice_source = self.sprite.surface.convert()
        self.sprite.w = self.w
        self.sprite.h = self.h
        self.sprite.render = False
        self.min_w = self.thickness * 2
        self.min_h = self.thickness * 2
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.sprite.type = "details_window"
        self.sprite.origin_depth = CONSTANTS.FRONT_DEPTH
        self.sprite.depth = self.sprite.origin_depth
        self.init_output()

    def init_output(self):
        font = self.icon.coordinator.ui_manager.font
        self.output_box = OutputBox(self, font, self.res_type)
        self.init_output_surface()

    def init_output_surface(self):
        if self.res_type == "medium":
            self.output_x = (self.x - self.max_w if self.max_w != 0 else self.x) * 4.9
            self.output_y = (self.y - self.max_h if self.max_h != 0 else self.y) + self.buffer
            w = int(max(self.max_w, self.w) * .57)
            h = int(max(self.max_h, self.h) * .915)
        else:
            self.output_x = (self.x - self.max_w if self.max_w != 0 else self.x) + self.buffer
            self.output_y = (self.y - self.max_h if self.max_h != 0 else self.y) * 4
            w = int(max(self.max_w, self.w) * .915)
            h = int(max(self.max_h, self.h) * .57)

        self.output_box.rect.width = w
        self.output_box.rect.height = h

        self.output_box.surface = pygame.Surface((self.output_box.rect.width, self.output_box.rect.height)).convert()
        self.output_box.init()

    def draw(self, canvas):
        canvas.blit(self.output_box.surface, (self.output_x, self.output_y))

    def roll_window(self):
        ui_manager = self.icon.coordinator.ui_manager

        if ui_manager.active_profile.res_type == "medium":
            if self.close:
                new_h = self.icon.coordinator.animation_manager.lerp_value(
                    self.sprite.h, self.min_h, .2)
            else:
                new_h = self.icon.coordinator.animation_manager.lerp_value(
                    self.sprite.h, self.max_h, .25)

            new_w = self.icon.sprite.w
            self.sprite.x = self.icon.sprite.x
            self.sprite.y = self.icon.sprite.y - new_h
            self.sprite.w = new_w
            self.sprite.h = new_h

        else:
            if self.close:
                new_w = self.icon.coordinator.animation_manager.lerp_value(
                    self.sprite.w, self.min_w, .2)
            else:
                new_w = self.icon.coordinator.animation_manager.lerp_value(
                    self.sprite.w, self.max_w, .1)

            new_h = self.icon.sprite.h
            self.sprite.x = self.icon.sprite.x - new_w
            self.sprite.y = self.icon.sprite.y
            self.sprite.w = new_w
            self.sprite.h = new_h

        w = max(int(self.sprite.w), self.min_w)
        h = max(int(self.sprite.h), self.min_h)

        if w <= self.min_w or h <= self.min_h:
            self.active = False
            self.close = False
            self.reset_window()
            return

        size = (w, h)
        if size != getattr(self, "last_size", None):
            self.sprite.surface = NineSlice(
                self.nineslice_source, self.thickness).render(w, h)
            self.last_size = size

    def reset_window(self):
        self.sprite.render = False
        self.sprite.w = self.w
        self.sprite.h = self.h
        self.sprite.x = self.x
        self.sprite.y = self.y


class OutputBox:
    def __init__(self, window, font, res_type):
        self.flavors_by_name = None
        self.click_targets = []
        self.res_type = res_type
        self.sprite_type = "modify"
        self.window = window
        self.font = font
        self.rect = pygame.Rect(0,0,0,0)
        self.bg = SimpleNamespace(img_name=None, surface=None)
        self.decr_arrow = SimpleNamespace(img_name="decr_arrow.png", surface=None, rect=pygame.Rect(0,0,0,0))
        self.incr_arrow = SimpleNamespace(img_name="incr_arrow.png", surface=None, rect=pygame.Rect(0,0,0,0))
        self.decr_arrow_left = SimpleNamespace(img_name="decr_arrow_left.png", surface=None, rect=pygame.Rect(0,0,0,0))
        self.incr_arrow_right = SimpleNamespace(img_name="incr_arrow_right.png", surface=None, rect=pygame.Rect(0,0,0,0))
        self.arrows = []
        self.current_flavor = None
        self.layout = None
        self.dirty = True
        self.surface = None
        self.layout_schema = OUTPUT_SCHEMAS[window.icon.name]
        self.arrow_schema = ARROW_SCHEMAS[res_type][window.icon.name]

    def init(self):
        self.decr_arrow.surface = pygame.image.load(os.path.join(CONSTANTS.IMAGE_DIR, "decr_arrow.png")).convert()
        self.incr_arrow.surface = pygame.image.load(os.path.join(CONSTANTS.IMAGE_DIR, "incr_arrow.png")).convert()
        self.decr_arrow_left.surface = pygame.image.load(os.path.join(CONSTANTS.IMAGE_DIR,"decr_arrow_left.png")).convert()
        self.incr_arrow_right.surface = pygame.image.load(os.path.join(CONSTANTS.IMAGE_DIR,"incr_arrow_right.png")).convert()
        if self.res_type == "medium":
            self.layout = output_box_layouts["medium"]
            w = self.decr_arrow.surface.get_width() // 6
            h = self.decr_arrow.surface.get_height() // 6
        else:
            self.layout = output_box_layouts["large"]
            w = self.decr_arrow.surface.get_width() // 6
            h = self.decr_arrow.surface.get_height() // 6

        self.decr_arrow.rect.width = w
        self.decr_arrow.rect.height = h
        self.decr_arrow.surface = pygame.transform.scale(self.decr_arrow.surface, (w, h))

        self.incr_arrow.rect.width = w
        self.incr_arrow.rect.height = h
        self.incr_arrow.surface = pygame.transform.scale(self.incr_arrow.surface, (w, h))

        self.build_arrows()

    def update(self):
        focused_flavor_sprite = self.window.icon.coordinator.event_manager.focused_flavor_sprite

        if focused_flavor_sprite is None:
            self.current_flavor = None
            self.dirty = True
        else:
            canonical = self.window.icon.coordinator.prep_sheet.flavors_by_name[focused_flavor_sprite.flavor.name]
            if self.current_flavor is not canonical:
                self.current_flavor = canonical
                self.dirty = True
        self.render()

    def render(self):
        if not self.dirty:
            return

        self.surface.fill(CONSTANTS.WINDOW_COLOR)

        for slot, token in self.layout_schema.items():
            if self.current_flavor and hasattr(self.current_flavor, token):
                text = getattr(self.current_flavor, token, 0)
            else:
                if token.startswith("_"):
                    text = token.lstrip("_")
                elif "_" in token:
                    text = 0
                else:
                    text = token

            x, y = self.layout[token]
            surf = self.font.render(str(text), True, (0,0,0))
            self.surface.blit(surf, (x, y))

        self.dirty = False


    def on_arrow_click(self, m_pos):
        if self.current_flavor is None:
            return

        mx, my = m_pos
        wx = self.window.output_x
        wy = self.window.output_y
        lx = mx - wx
        ly = my - wy
        for arrow in self.arrows:
            arrow.hit_rect = arrow.rect.inflate(30,30)
            if arrow.hit_rect.collidepoint(lx, ly):
                value = getattr(self.current_flavor, arrow.attr, 0)
                value += arrow.delta
                value = max(0, min(15, value))
                setattr(self.current_flavor, arrow.attr, value)
                self.current_flavor.calculate()
                self.dirty = True
                return

    def build_arrows(self):
        coordinator = self.window.icon.coordinator
        w = self.decr_arrow.surface.get_width()
        h = self.decr_arrow.surface.get_height()
        def generate_arrow(_label, schema):
            x = schema[0][0]
            y = schema[0][1]
            rect = pygame.Rect(x, y, w, h)
            attr = schema[1]
            delta = schema[2]
            if self.res_type == "medium":
                if "incr" in _label:
                    img_name = "incr_arrow_right.png"
                    surface = self.incr_arrow.surface
                else:
                    img_name = "decr_arrow_left.png"
                    surface = self.decr_arrow.surface
            else:
                if "incr" in _label:
                    img_name = "incr_arrow.png"
                    surface = self.incr_arrow.surface
                else:
                    img_name = "decr_arrow.png"
                    surface = self.decr_arrow.surface
            arrow = Arrow(self, rect, attr, delta, coordinator, label, img_name, surface)
            arrow.sprite.type = self.sprite_type
            self.arrows.append(arrow)

        for label, tup in self.arrow_schema.items():
            generate_arrow(label, tup)

    def render_arrows(self, flag):
        for arrow in self.arrows:
            arrow.sprite.render = flag


class Arrow:
    def __init__(self, output_box, rect, attr, delta, coord, name, image_name, surface):
        self.output_box = output_box
        self.rect = rect
        self.hit_rect = None
        self.x = rect.left + self.output_box.window.output_x
        self.y = rect.top + self.output_box.window.output_y
        self.w = rect.width
        self.h = rect.height
        self.attr = attr
        self.delta = delta
        self.sprite = None
        self.init_sprite(coord, name, image_name, surface)

    def init_sprite(self, coord, name, image_name, surface):
        self.sprite = Sprite(coord, name, image_name)
        self.sprite.is_arrow = True
        self.sprite.arrow = self
        self.sprite.surface = surface.copy()
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.sprite.w = self.w
        self.sprite.h = self.h
        self.hit_rect = pygame.Rect(self.sprite.x, self.sprite.y, self.sprite.w, self.sprite.h)
        self.sprite.depth = CONSTANTS.FRONT_DEPTH+1
        self.sprite.origin_depth = self.sprite.depth
        coord.draw_manager.subscribe(self.sprite)


class NineSlice:
    def __init__(self, source_surface, border_thickness):
        self.source = source_surface
        self.t = border_thickness
        self.w, self.h = self.source.get_size()

        self.top_left = self.source.subsurface(0, 0, self.t, self.t).copy()
        self.top_right = self.source.subsurface(self.w - self.t, 0, self.t, self.t).copy()
        self.bottom_left = self.source.subsurface(0, self.h - self.t, self.t, self.t).copy()
        self.bottom_right = self.source.subsurface(self.w - self.t, self.h - self.t, self.t, self.t).copy()

        self.top_edge = self.source.subsurface(self.t, 0, self.w - 2*self.t, self.t).copy()
        self.bottom_edge = self.source.subsurface(self.t, self.h - self.t, self.w - 2*self.t, self.t).copy()
        self.right_edge = self.source.subsurface(self.w - self.t, self.t, self.t, self.h - 2*self.t).copy()
        self.left_edge = self.source.subsurface(0, self.t, self.t, self.h - 2*self.t).copy()

        self.center = self.source.subsurface(self.t, self.t, self.w - 2*self.t, self.h - 2*self.t).copy()

    def render(self, target_w, target_h):
        surface = pygame.Surface((target_w, target_h)).convert()
        surface.set_colorkey(CONSTANTS.TRANSPARENT)
        surface.fill(CONSTANTS.TRANSPARENT)

        surface.blit(self.top_left, (0, 0))
        surface.blit(self.top_right, (target_w - self.t, 0))
        surface.blit(self.bottom_left, (0, target_h - self.t))
        surface.blit(self.bottom_right, (target_w - self.t, target_h - self.t))

        top_scaled = pygame.transform.scale(self.top_edge, (target_w - 2*self.t, self.t))
        bottom_scaled = pygame.transform.scale(self.bottom_edge, (target_w - 2*self.t, self.t))
        left_scaled = pygame.transform.scale(self.left_edge, (self.t,  target_h - 2*self.t))
        right_scaled = pygame.transform.scale(self.right_edge, (self.t,  target_h - 2*self.t))

        surface.blit(top_scaled, (self.t, 0))
        surface.blit(bottom_scaled, (self.t, target_h - self.t))
        surface.blit(left_scaled, (0, self.t))
        surface.blit(right_scaled, (target_w - self.t, self.t))

        center_scaled = pygame.transform.scale(self.center, (target_w - 2*self.t, target_h - 2*self.t))
        surface.blit(center_scaled, (self.t, self.t))

        return surface


class Background:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.border_name = "bg_border_blue.png"
        self.border_image = None
        self.nine_slice_bg = None
        self.border_thickness = 8
        self.nine_slice = None
        self.bg_surface = None
        self.bg_name = "background.png"

    def initialize(self):
        self.bg_surface = pygame.image.load(os.path.join(CONSTANTS.IMAGE_DIR, self.bg_name)).convert()
        self.border_image = pygame.image.load(os.path.join(CONSTANTS.IMAGE_DIR, self.border_name)).convert_alpha()
        w = self.coordinator.ui_manager.screen.w
        h = self.coordinator.ui_manager.screen.h
        self.bg_surface = pygame.transform.scale(self.bg_surface, (w, h))
        self.nine_slice_bg = NineSlice(self.border_image, self.border_thickness).render(w, h)
        self.coordinator.ui_manager.pygame.static_canvas.blit(self.bg_surface, (0, 0))
        self.coordinator.ui_manager.pygame.static_canvas.blit(self.nine_slice_bg, (0, 0))


class Grid:
    def __init__(self):
        self.top_left = (0,0)
        self.cols = 1
        self.rows = 1
        self.cell_width = 1
        self.cell_height = 1
        self.cells = []

    def create_grid(self, top_left: tuple, cell_width: int, cell_height: int, rows: int, cols: int) -> None:
        self.top_left = top_left
        self.rows = rows
        self.cols = cols
        self.cell_width = cell_width
        self.cell_height = cell_height
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                x = top_left[0] + c * self.cell_width
                y = top_left[1] + r * self.cell_height
                row.append((x, y))
            self.cells.append(row)