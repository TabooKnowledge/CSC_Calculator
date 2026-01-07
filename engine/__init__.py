import os
import json
import pygame
from types import SimpleNamespace
from ui import Sprite, Icon, DetailsWindow
from config import buttons_data, icons_data, resolution_profiles, CONSTANTS, STATE_FIELDS, EDIT_FIELDS
from domain import build_flavor_set


class AnimationManager:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.lerp_speed = SimpleNamespace(value=.075, move=.1, scale=.1, alpha=.1)
        self.active_animations = []

    def lerp_value(self, value, target, speed=None):
        lerp_speed = speed if speed else self.lerp_speed.value

        delta = target - value

        if abs(delta) < 5:
            return target

        value += delta * lerp_speed
        return value

    def lerp_move(self, sprite, target_x, target_y):
        lerp_speed = self.lerp_speed.move

        total_dx = target_x - sprite.origin_x
        total_dy = target_y - sprite.origin_y

        dx = target_x - sprite.x
        dy = target_y - sprite.y

        remaining_distance = (dx**2 + dy**2)**0.5
        total_distance = (total_dx ** 2 + total_dy ** 2) ** 0.5

        if remaining_distance < 10:
            sprite.x = target_x
            sprite.y = target_y
            return True
        if remaining_distance < .1 * total_distance:
            lerp_speed *= 1.5
        elif remaining_distance < .5 * total_distance:
            lerp_speed *= 1.25

        sprite.x += dx * lerp_speed
        sprite.y += dy * lerp_speed
        return False

    def lerp_scale(self, sprite, scale_x, scale_y):
        target_w = sprite.origin_w * scale_x
        target_h = sprite.origin_h * scale_y

        dw = target_w - sprite.w
        dh = target_h - sprite.h

        remaining_distance = (dw**2 + dh**2)**0.5
        total_distance = ((target_w - sprite.origin_w)**2 + (target_h - sprite.origin_h)**2)**0.5

        if remaining_distance < 5:
            sprite.w = target_w
            sprite.h = target_h
            sprite.surface = pygame.transform.scale(sprite.origin_surface, (int(sprite.w), int(sprite.h)))
            return True
        else:
            lerp_speed = self.lerp_speed.scale
            if remaining_distance < .1 * total_distance:
                lerp_speed *= 1.5
            elif remaining_distance < .5 * total_distance:
                lerp_speed *= 1.25

        sprite.w += dw * lerp_speed
        sprite.h += dh * lerp_speed
        sprite.surface = pygame.transform.scale(sprite.origin_surface, (int(sprite.w), int(sprite.h)))
        return False

    def lerp_alpha(self, sprite, target_a):
        current_alpha = sprite.surface.get_alpha()
        if current_alpha is None:
            current_alpha = 255

        new_alpha = current_alpha + (target_a - current_alpha) * self.lerp_speed.alpha
        if abs(new_alpha - target_a) <= 10:
            new_alpha = target_a
        sprite.alpha = new_alpha
        sprite.surface.set_alpha(new_alpha)


class EventManager:
    def __init__(self, coordinator):

        self.last_flavor_sprite = None
        self.coordinator = coordinator
        self.dragged_sprite = None
        self.offset_x = None
        self.offset_y = None
        self.focused_icon_sprite = None
        self.focused_flavor_sprite = None
        self.sprite_transitioning = False
        self.transition_tag = None
        self.state = "main"
        self.active_state = None
        self.event = None
        self.active_event = None
        self.event_pos = SimpleNamespace(x=0,y=0)
        self.delay_timer = 0
        self.state_dict = {
            "main": {
                "exit": self.exit,
                "pointer_down": self.check_clicked,
                "pointer_moving": self.move_sprite,
                "pointer_up": self.undrag
            },
            "container_open": {
                "exit": self.exit,
                "pointer_down": self.check_clicked,
                "pointer_moving": self.move_sprite,
                "pointer_up": self.undrag
            },
            "flavor_focused": {
                "exit": self.exit,
                "pointer_down": self.check_dragged,
                "pointer_moving": self.move_sprite,
                "pointer_up": self.undrag
            }
        }

    def update(self):
        if self.delay():
            return
        self.retrieve_pos()
        self.check_state()
        self.check_event()
        self.execute_event()
        self.active_event = None

    def delay(self):
        now = pygame.time.get_ticks()
        if self.event.type in (pygame.FINGERDOWN, pygame.FINGERUP):
            self.delay_timer = now + 1
        if now < self.delay_timer:
            return True
        return False

    def retrieve_pos(self):
        if self.event is not None:
            if hasattr(self.event, "pos"):
                self.event_pos.x, self.event_pos.y = self.event.pos
            elif hasattr(self.event, "x") and hasattr(self.event, "y"):
                self.event_pos.x = self.event.x * self.coordinator.ui_manager.screen.w
                self.event_pos.y = self.event.y * self.coordinator.ui_manager.screen.h

    def check_state(self):
        if self.state in self.state_dict:
            self.active_state = self.state_dict[self.state]
        else:
            print(f"State {self.state} not found")

    def check_event(self):
        if self.event.type == pygame.QUIT:
            self.active_event = self.active_state["exit"]
        elif self.event.type == pygame.KEYDOWN:
            if self.event.key == pygame.K_ESCAPE:
                self.active_event = self.active_state["exit"]
        elif self.event.type == pygame.MOUSEBUTTONDOWN or self.event.type == pygame.FINGERDOWN:
            for s in self.coordinator.draw_manager.registry:
                print(f"{s.name} X: {s.x}, Y: {s.y}")
            self.active_event = self.active_state["pointer_down"]
        elif self.event.type == pygame.MOUSEMOTION or self.event.type == pygame.FINGERMOTION:
            self.active_event = self.active_state["pointer_moving"]
        elif self.event.type == pygame.MOUSEBUTTONUP or self.event.type == pygame.FINGERUP:
            self.active_event = self.active_state["pointer_up"]

    def execute_event(self):
        if self.active_event is not None:
            if self.state == "main":
                self.active_event(type="icon")
            elif self.state == "container_open":
                self.active_event(type="flavor")
            elif self.state == "flavor_focused":
                self.active_event(type="modify")
        self.active_event = None

    def exit(self, *args, **kwargs):
        self.coordinator.running = False

    def check_dragged(self, *args, **kwargs):
        hits = []
        for s in self.coordinator.draw_manager.registry:
            if not isinstance(s, Sprite):
                continue
            if self.point_in_sprite(s):
                hits.append(s)

        def z_keys(_s):
            return _s.depth, self.coordinator.draw_manager.registry.index(_s)

        clicked = max(hits, key=z_keys)
        if not clicked:
            return

        self.dragged_sprite = clicked
        self.offset_x = self.event_pos.x - clicked.x
        self.offset_y = self.event_pos.y - clicked.y

    def check_clicked(self, *args, **kwargs):
        _type = kwargs.get("type")
        if _type is None:
            raise ValueError("check_clicked requires type=sprite.type")

        if self.sprite_transitioning:
            return

        if _type == "icon":
            if self.focused_icon_sprite and self.point_in_sprite(self.focused_icon_sprite):
                return
        elif _type == "flavor":
            if self.focused_flavor_sprite and self.point_in_sprite(self.focused_flavor_sprite):
                return

        hits = []
        for s in self.coordinator.draw_manager.registry:
            if not isinstance(s, Sprite):
                continue
            if _type == "modify":
                if s.type not in ("modify", "flavor"):
                    continue
            elif s.type != _type:
                continue
            if self.point_in_sprite(s):
                hits.append(s)
        if not hits:
            if _type == "icon":
                self.unfocus_current_icon()
            else:
                self.unfocus_current_flavor()
            return

        def z_keys(_s):
            return _s.depth, self.coordinator.draw_manager.registry.index(_s)

        clicked = max(hits, key=z_keys)

        if clicked.name == "excel":
            self.coordinator.prep_sheet.calculate_production_numbers(output=True)
            return
        if _type == "modify":
            if clicked.type == "modify":
                self.focused_icon_sprite.icon.details_window.output_box.on_arrow_click(
                    (self.event_pos.x, self.event_pos.y))
            else:
                self.set_focused_flavor(clicked)
        elif _type == "icon":
            self.set_focused_icon(clicked)
            self.refresh_flavors()
        elif _type == "flavor":
            self.set_focused_flavor(clicked)

    def point_in_sprite(self, s):
        if getattr(s, "arrow", None):
            hit_rect = pygame.Rect(s.x, s.y, s.w, s.h).inflate(30,30)
            return  hit_rect.collidepoint(self.event_pos.x, self.event_pos.y)
        return (s.x <= self.event_pos.x <= s.x + s.w) and (s.y <= self.event_pos.y <= s.y + s.h)

    def refresh_flavors(self):
        if self.focused_icon_sprite is None:
            return

        for sprite in list(self.coordinator.draw_manager.registry):
            if isinstance(sprite, Sprite):
                if sprite.type == "flavor":
                    self.coordinator.draw_manager.unsubscribe(sprite)

        for c in self.focused_icon_sprite.icon.contents:
            self.coordinator.draw_manager.subscribe(c.sprite)

    def set_focused_icon(self, sprite):
        if sprite.moving_home:
            return

        self.state = "container_open"

        if self.focused_icon_sprite and self.focused_icon_sprite is not sprite:
            self.focused_icon_sprite.focused = False
            self.focused_icon_sprite.moving_home = True
            self.focused_icon_sprite.depth = CONSTANTS.ICON_DEPTH
            self.focused_icon_sprite.icon.show_contents = False

        sprite.icon.details_window.active = True
        sprite.focused = True
        sprite.moving_home = False
        sprite.depth = CONSTANTS.FRONT_DEPTH
        self.focused_icon_sprite = sprite

    def unfocus_current_icon(self):
        if not self.focused_icon_sprite:
            return
        self.focused_icon_sprite.focused = False
        self.focused_icon_sprite.moving_home = True
        self.focused_icon_sprite.depth = CONSTANTS.ICON_DEPTH
        self.focused_icon_sprite.icon.show_contents = False
        self.focused_icon_sprite.icon.details_window.close = True
        self.focused_icon_sprite = None

    def set_focused_flavor(self, sprite):
        if sprite.moving_home:
            return

        self.state = "flavor_focused"

        if self.focused_flavor_sprite and self.focused_flavor_sprite is not sprite:
            self.focused_flavor_sprite.focused = False
            self.focused_flavor_sprite.moving_home = True
            self.focused_flavor_sprite.depth = self.focused_flavor_sprite.icon.sprite.depth + 1
        sprite.focused = True
        sprite.moving_home = False
        sprite.depth = CONSTANTS.FRONT_DEPTH + 10000
        self.focused_flavor_sprite = sprite

    def unfocus_current_flavor(self):
        if not self.focused_flavor_sprite:
            if self.last_flavor_sprite and self.last_flavor_sprite.moving_home:
                return
            else:
                self.reset_to_main()
                return

        self.state = "container_open"

        self.focused_flavor_sprite.focused = False
        self.focused_flavor_sprite.moving_home = True
        self.focused_flavor_sprite.depth = self.focused_flavor_sprite.icon.sprite.depth + 1
        self.last_flavor_sprite = self.focused_flavor_sprite
        self.focused_flavor_sprite = None

    def reset_to_main(self):
        self.unfocus_current_icon()
        self.active_state = self.state_dict["main"]
        self.state = "main"

    def undrag(self, *args, **kwargs):
        self.dragged_sprite = None

    def move_sprite(self, *args, **kwargs):
        if self.dragged_sprite:
            self.dragged_sprite.x = self.event_pos.x - self.offset_x
            self.dragged_sprite.y = self.event_pos.y - self.offset_y


class UiManager:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.buttons_data = buttons_data
        self.icons_data = icons_data
        self.resolution_profiles = resolution_profiles
        self.res_type = None
        self.active_profile = None

        self.icons_list = []
        self.buttons_list = []

        self.screen = SimpleNamespace(w=0, h=0, short=0, dimensions=None, short_axis=None)
        self.base_resolution = SimpleNamespace(w=0, h=0)
        self.scale = SimpleNamespace(x=0, y=0, image=1, multiplier=1, font=8)
        self.center = SimpleNamespace(x=0, y=0)

        self.pygame = SimpleNamespace(static_canvas=None, dynamic_canvas=None, screen=None, display_info=None, debug_canvas=None)
        self.font = None

        self.focused_sprite = None
        self.focused_scale = 2.125

        self.num_cells = 3
        self.cell_size = None

    def refresh_screen(self):
        self.pygame.screen.fill((0, 0, 0))
        self.pygame.debug_canvas.fill((255, 0,255))

    def update(self):
        self.update_icons()
        self.draw_canvas()

    def draw_canvas(self):
        self.pygame.screen.blit(self.pygame.static_canvas, (0, 0))
        self.pygame.screen.blit(self.pygame.dynamic_canvas, (0, 0))
        self.pygame.screen.blit(self.pygame.debug_canvas, (0, 0))

    def update_icons(self):
        for icon in self.icons_list:
            icon.toggle_show_contents()
            icon.details_window.update()

    def initialize(self):
        self.screen.display_info = pygame.display.Info()
        self.screen.w = self.screen.display_info.current_w
        self.screen.h = self.screen.display_info.current_h
        self.screen.short = min(self.screen.w, self.screen.h)
        self.screen.dimensions = (self.screen.w, self.screen.h)
        self.pygame.screen = pygame.display.set_mode(self.screen.dimensions)
        self.pygame.static_canvas = pygame.Surface(self.screen.dimensions).convert()
        self.pygame.dynamic_canvas = pygame.Surface(self.screen.dimensions).convert()
        self.pygame.dynamic_canvas.set_colorkey(CONSTANTS.TRANSPARENT)
        self.pygame.debug_canvas = pygame.Surface(self.screen.dimensions).convert()
        self.pygame.debug_canvas.set_colorkey(CONSTANTS.TRANSPARENT)
        pygame.display.set_caption("Chicken Salad Production Software")
        self.adjust_resolution()
        self.font = pygame.font.Font(None, int(self.scale.font))
        self.populate_icon_list()
        self.populate_button_list()
        self.scale_sprites()
        self.layout_icons()
        self.layout_buttons()
        self.setup_icon_grids()

    def adjust_resolution(self):
        self.retrieve_resolution_data()
        self.set_resolution_data()

    def retrieve_resolution_data(self):
        for attr, attr_value in vars(self.resolution_profiles).items():
            if self.screen.short <= attr_value.max_short:
                self.active_profile = attr_value
                self.res_type = attr
                break

    def set_resolution_data(self):
        self.base_resolution.w = self.active_profile.base_width
        self.base_resolution.h = self.active_profile.base_height
        self.scale.font = self.active_profile.font_size
        self.scale.x = self.screen.w / self.base_resolution.w
        self.scale.y = self.screen.h / self.base_resolution.h
        self.scale.multiplier = self.active_profile.scale_multiplier
        self.scale.image = min(self.scale.x, self.scale.y) * self.scale.multiplier
        self.scale.font = self.active_profile.font_size * self.scale.image
        self.screen.short_axis = "width" if self.screen.w < self.screen.h else "height"

    def populate_icon_list(self):
        ordered_keys = ["reach_in", "quick", "walk_in"]
        for key in ordered_keys:
            data = getattr(self.icons_data, key)
            icon_sprite = Sprite(self.coordinator, data.name, data.image_name)
            icon_sprite.type = "icon"
            icon_sprite.origin_depth = CONSTANTS.ICON_DEPTH
            icon = Icon(self.coordinator, icon_sprite, key)
            icon.populate_content(build_flavor_set(self.coordinator, key))
            icon_sprite.icon = icon
            icon.details_window = DetailsWindow(icon)#WINDOW CREATED
            self.icons_list.append(icon)

    def setup_icon_grids(self):
        for i in self.icons_list:
            i.setup_grid()
            i.position_content()

    def populate_button_list(self):
        ordered_keys = ["reach_in", "quick", "walk_in", "excel"]
        for key in ordered_keys:
            data = getattr(self.buttons_data, key)
            button = Sprite(self.coordinator, data.name, data.image_name)
            button.type = "button"
            button.origin_depth = CONSTANTS.BUTTON_DEPTH
            button.initialize()
            self.buttons_list.append(button)

    def scale_sprites(self, registry=None):
        registry = registry if registry is not None else self.coordinator.draw_manager.registry

        for sprite in registry:
            if isinstance(sprite, Sprite) and sprite.name != "background":
                self.assign_depth(sprite)
                w = sprite.w * self.coordinator.ui_manager.scale.image
                h = sprite.h * self.coordinator.ui_manager.scale.image
                sprite.origin_w = w
                sprite.origin_h = h
                sprite.center_x = self.coordinator.ui_manager.screen.w // 2 - int(sprite.origin_w * self.focused_scale) // 2
                sprite.center_y = self.coordinator.ui_manager.screen.h // 2 - int(sprite.origin_h * self.focused_scale) // 2
                sprite.scale(w, h)

    @staticmethod
    def assign_depth(sprite):
        if sprite.type == "button":
            sprite.depth = CONSTANTS.BUTTON_DEPTH
            sprite.origin_depth = CONSTANTS.BUTTON_DEPTH
        elif sprite.type == "icon":
            sprite.depth = CONSTANTS.ICON_DEPTH
            sprite.origin_depth = CONSTANTS.ICON_DEPTH
        elif sprite.type == "background":
            sprite.depth = CONSTANTS.BACKGROUND_DEPTH

    def layout_icons(self):
        if self.screen.short_axis == "height":
            cell_size = self.coordinator.ui_manager.screen.w // self.num_cells
            for i, icon in enumerate(self.icons_list):
                icon.details_window.init()
                icon.sprite.x = i * cell_size + cell_size // 2 - icon.sprite.w // 2
                icon.sprite.y = self.coordinator.ui_manager.screen.h // 2 - icon.sprite.h
                icon.sprite.origin_x = icon.sprite.x
                icon.sprite.origin_y = icon.sprite.y
                icon.sprite.origin_w = icon.sprite.w
                icon.sprite.origin_h = icon.sprite.h
        else:
            cell_size = self.coordinator.ui_manager.screen.h * .65 // self.num_cells
            for i, icon in enumerate(self.icons_list):
                icon.details_window.init()
                icon.sprite.x = self.coordinator.ui_manager.screen.w // 2 - icon.sprite.w // 2
                icon.sprite.y = i * cell_size + cell_size // 2 - icon.sprite.h // 2
                icon.sprite.origin_x = icon.sprite.x
                icon.sprite.origin_y = icon.sprite.y
                icon.sprite.origin_w = icon.sprite.w
                icon.sprite.origin_h = icon.sprite.h

    def layout_buttons(self):
        for i, button in enumerate(self.buttons_list):
            if button.name == "excel":
                if self.res_type == "medium":
                    button.y = self.screen.h - button.h * 2.5
                else:
                    button.y = self.screen.h - button.h - 8

                button.x = self.screen.w // 2 - button.w // 2
                button.type = "icon"
            else:
                button.x = self.icons_list[i].sprite.x
                button.y = self.icons_list[i].sprite.y + self.icons_list[i].sprite.h

            button.origin_x = button.x
            button.origin_y = button.y
            button.origin_w = button.w
            button.origin_h = button.h


class StateStore:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.flavors_by_name = {}

    def initialize(self):
        self.flavors_by_name = self.coordinator.prep_sheet.flavors_by_name
        self.load_state()

    def load_state(self):
        if not os.path.exists(CONSTANTS.SAVE_FILE):
            return False

        try:
            with open(CONSTANTS.SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return False

        if not isinstance(data, dict):
            return False

        for flavor_name, attrs in data.items():
            flavor = self.coordinator.prep_sheet.flavors_by_name.get(flavor_name)
            if flavor is None or not isinstance(attrs, dict):
                continue

            for attr, value in attrs.items():
                if attr in EDIT_FIELDS and hasattr(flavor, attr):
                    setattr(flavor, attr, value)
            flavor.calculate()
        self.coordinator.prep_sheet.calculate_production_numbers(output=False)
        return True

    def save_state(self):
        save_data = {}

        for name, flavor in self.flavors_by_name.items():
            save_data.setdefault(name, {})
            for attr in EDIT_FIELDS:
                if not hasattr(flavor, attr):
                    raise AttributeError(f"{flavor.name} has no attribute {attr}")
                save_data[name][attr] = getattr(flavor, attr)

        self.write_to_save(save_data)

    @staticmethod
    def write_to_save(data):
        os.makedirs(CONSTANTS.SAVE_DIR, exist_ok=True)
        with open(CONSTANTS.SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

