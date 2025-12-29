from config import *
import math
from types import SimpleNamespace
import os
import pygame


class Ingredient:
    def __init__(self, coordinator, name, weight):
        self.coordinator = coordinator
        self.name = name
        self.weight = weight
        self.totaled_weight = 0

    def total_weight(self, mix_weight):
        self.totaled_weight = round((mix_weight / 4) * self.weight, 2)


class Flavor:
    def __init__(self, coordinator, flavor_data, ingredients_data):
        self.depth = 0
        self.origin_y = 0
        self.origin_x = 0
        self.center_y = 0
        self.center_x = 0
        self.coordinator = coordinator
        self.data = SimpleNamespace(flavor=flavor_data, ingredients=ingredients_data)
        self.tag = None
        self.img_tag = "flavor"
        #Visuals
        self.img_name = None
        self.sprite = None
        self.name = None
        self.text_surface = None
        #For production
        self.large_quick_par = 0
        self.small_quick_par = 0
        self.line_mix_par = 0
        self.totaled_par_weight = 0
        self.large_quick_on_hand = 0
        self.small_quick_on_hand = 0
        self.line_mix_on_hand = 0
        self.large_quick_needed = 0
        self.small_quick_needed = 0
        self.line_mix_needed = 0
        self.total_mix_weight = 0
        self.ingredients = []
        self.totaled_ingredient_weight = 0

    def initialize(self):
        self.img_name = self.data.flavor.img_name
        self.name = self.data.flavor.name
        self.text_surface = self.coordinator.ui_manager.font.render(self.name, True, (0,0,0))
        self.store_ingredients()

    def store_ingredients(self):
        for name in self.data.flavor.ingredients:
            for ingredient in self.data.ingredients:
                if ingredient.name == name:
                    self.ingredients.append(ingredient)
                    break

    def load_sprite(self, sprite_class):
        self.sprite = sprite_class(self.coordinator, self.name, self.img_name)
        self.sprite.flavor = self
        self.sprite.initialize(self.img_tag)

    def calculate_par_weight(self):
        self.totaled_par_weight = math.ceil(self.large_quick_par + self.small_quick_par / 2 + self.line_mix_par)

    def calculate_needed(self):
        self.calculate_prep_numbers()
        self.calculate_total_mix_weight()

    def calculate_prep_numbers(self):
        self.large_quick_needed = max(0, self.large_quick_par - self.large_quick_on_hand)
        self.small_quick_needed = max(0, self.small_quick_par - self.small_quick_on_hand)
        self.line_mix_needed = max(0, self.line_mix_par - self.line_mix_on_hand)

    def calculate_total_mix_weight(self):
        on_hand = self.large_quick_on_hand + self.small_quick_on_hand / 2 + self.line_mix_on_hand
        self.total_mix_weight = math.ceil(self.totaled_par_weight - on_hand)
        self.total_ingredient_weight()

    def total_ingredient_weight(self):
        self.totaled_ingredient_weight = 0
        for ingredient in self.ingredients:
            ingredient.total_weight(self.total_mix_weight)
            self.totaled_ingredient_weight += ingredient.weight


class PrepSheet:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.chicken_on_hand = 140
        self.chicken_par = 160
        self.total_chicken_used = 0
        self.chicken_remaining = 0
        self.chicken_to_cook = 0
        self.all_flavors = None
        self.error_not_enough_chicken = -1

    def calculate_production_numbers(self):
        self.total_chicken_used = 0
        for flavor in self.all_flavors:
            weight = flavor.total_mix_weight
            quarter_weight = weight / 4
            flavor.chicken_weight = round(weight - (quarter_weight * flavor.totaled_ingredient_weight), 2)
            self.total_chicken_used += flavor.chicken_weight
        if self.total_chicken_used < self.chicken_on_hand:
            self.chicken_remaining = self.chicken_on_hand - math.ceil(self.total_chicken_used)
            self.chicken_to_cook = self.chicken_par - self.chicken_remaining
        else:
            self.error_not_enough_chicken = 1

    def print_output(self):
        for flavor in self.all_flavors:
            print(f"\n**********{flavor.name}***********")
            print(f"Total mix weight: {flavor.total_mix_weight}")
            print(f"Large Quicks Needed: {flavor.large_quick_needed}")
            print(f"Small Quicks Need: {flavor.small_quick_needed}")
            print(f"Line Mix Need: {flavor.line_mix_needed}")
            print(f"Chicken weight {flavor.chicken_weight}")
            for ingredient in flavor.ingredients:
                print(f"{ingredient.name} weight {ingredient.totaled_weight}")
        if self.error_not_enough_chicken == 1:
            print("\n********** ERROR **********")
            print(f"Total chicken used exceeds chicken on hand!!!")
            print(f"Chicken on hand: {self.chicken_on_hand}")
            print(f"Total chicken used: {math.ceil(self.total_chicken_used)}")
        else:
            print("\n********** Summary **********")
            print(f"Total chicken used: {math.ceil(self.total_chicken_used)}")
            print(f"Chicken remaining: {self.chicken_remaining}")
            print(f"Pans to cook: {math.ceil(self.chicken_to_cook / 10)}")


class Grid:
    def __init__(self):
        self.origin = (0,0)
        self.cols = 1
        self.rows = 1
        self.cell_width = 1
        self.cell_height = 1
        self.cells = []

    def create_grid(self, origin: tuple, cell_width: int, cell_height: int, rows: int, cols: int) -> None:
        self.origin = origin
        self.rows = rows
        self.cols = cols
        self.cell_width = cell_width
        self.cell_height = cell_height
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                x = origin[0] + c * self.cell_width
                y = origin[1] + r * self.cell_height
                row.append((x, y))
            self.cells.append(row)


class DrawManager:
    def __init__(self, coordinator):
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
                if sprite.flavor is not None:
                    self.draw_text_surface(sprite)
                sprite.draw(self.canvas)
                sprite.update()


    def update_canvas(self):
        self.coordinator.ui_manager.pygame.dynamic_canvas.fill(CONSTANTS.TRANSPARENT)
        self.canvas = self.coordinator.ui_manager.pygame.dynamic_canvas

    def draw_text_surface(self, sprite):
        sprite_center_x = sprite.x + sprite.w // 2
        t_x = sprite_center_x - sprite.flavor.text_surface.get_width() // 2
        t_y = sprite.y + sprite.h
        self.coordinator.ui_manager.pygame.dynamic_canvas.blit(sprite.flavor.text_surface, (t_x, t_y))

    def subscribe_object(self, sprite):
        self.registry.append(sprite)

    def unsubscribe_sprite(self, sprite):
        for r_sprite in self.registry:
            if r_sprite == sprite:
                self.registry.remove(sprite)


class SpriteManager:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.sprites = []

    def update(self):
        for sprite in self.sprites:
            sprite.update()


class Sprite:
    def __init__(self, coordinator, name, img_name):
        self.flavor = None
        self.icon = None
        self.origin_depth = None
        self.depth = 0
        self.idle_focused = False
        self.coordinator = coordinator
        self.state_tag = None
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

    def initialize(self, img_tag):
        self.img_tag = img_tag
        self.surface = pygame.image.load(os.path.join(CONSTANTS.IMAGE_DIR, self.img_name)).convert()
        self.origin_surface = self.surface
        self.w = self.surface.get_width()
        self.h = self.surface.get_height()
        self.coordinator.draw_manager.subscribe_object(self)

    def update(self):
        if self.focused and not self.moving_home:
            self.center_self()
        elif self.moving_home:
            self.return_home()

    def center_self(self):
        if not self.idle_focused:
            self.coordinator.event_manager.sprite_transitioning = True
            scale_done = self.coordinator.animation_manager.lerp_scale(self, self.focused_scale)
            move_done = self.coordinator.animation_manager.lerp_move(self, self.center_x, self.center_y)

            if scale_done and move_done:
                if self.icon is not None:
                    self.icon.show_contents = True
                self.coordinator.event_manager.sprite_transitioning = False
                self.idle_focused = True
                self.at_home = False
                self.moving_home = False

    def return_home(self):
        scale_done = self.coordinator.animation_manager.lerp_scale(self, 1)
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


class AnimationManager:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.lerp_speed = SimpleNamespace(move=.075, scale=.1, alpha=.1)
        self.active_animations = []

    def lerp_move(self, sprite, target_x, target_y):
        lerp_speed = self.lerp_speed.move

        total_dx = target_x - sprite.origin_x
        total_dy = target_y - sprite.origin_y

        dx = target_x - sprite.x
        dy = target_y - sprite.y
        remaining_distance = (dx**2 + dy**2)**0.5
        total_distance = (total_dx ** 2 + total_dy ** 2) ** 0.5
        if remaining_distance < 5:
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

    def lerp_scale(self, sprite, scale):
        lerp_speed = self.lerp_speed.scale
        target_w = sprite.origin_w * scale
        target_h = sprite.origin_h * scale

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
        self.coordinator = coordinator
        self.dragged_sprite = None
        self.focused_icon_sprite = None
        self.focused_flavor_sprite = None
        self.sprite_transitioning = False
        self.state = "main"
        self.active_state = None
        self.event = None
        self.active_event = None
        self.event_pos = SimpleNamespace(x=0,y=0)
        self.delay_timer = 0
        self.state_dict = {
            "main": {
                "exit": self.exit,
                "pointer_down": self.check_icon_clicked,
                "pointer_up": self.update_dragged_sprite,
                "pointer_moving": self.move_sprite,

            },
            "reach_in": {
                "exit": self.exit,
                "pointer_down": self.check_flavor_clicked,
                "pointer_up": self.update_dragged_sprite,
                "pointer_moving": self.move_sprite,
            },
            "quick": {
                "exit": self.exit,
                "pointer_down": self.check_flavor_clicked,
                "pointer_up": self.update_dragged_sprite,
                "pointer_moving": self.move_sprite,
            },
            "walk_in": {
                "exit": self.exit,
                "pointer_down": self.check_flavor_clicked,
                "pointer_up": self.update_dragged_sprite,
                "pointer_moving": self.move_sprite,
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
        if self.event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
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
            self.active_event = self.active_state["pointer_down"]
        elif self.event.type == pygame.MOUSEMOTION or self.event.type == pygame.FINGERMOTION:
            self.active_event = self.active_state["pointer_moving"]
        elif self.event.type == pygame.MOUSEBUTTONUP or self.event.type == pygame.FINGERUP:
            self.active_event = self.active_state["pointer_up"]

    def execute_event(self):
        if self.active_event is not None:
            self.active_event()
        self.active_event = None

    def exit(self):
        self.coordinator.running = False

    def update_dragged_sprite(self):
        self.dragged_sprite = None

    def check_icon_clicked(self):
        if self.sprite_transitioning:
            return
        if self.focused_icon_sprite and self.point_in_sprite(self.focused_icon_sprite):
            return

        hits = []
        for s in self.coordinator.draw_manager.registry:
            if not isinstance(s, Sprite):
                continue
            if s.img_tag != "icon":
                continue
            if self.point_in_sprite(s):
                hits.append(s)
        if not hits:
            self.unfocus_current_icon()
            return

        def z_keys(s):
            return s.depth, self.coordinator.draw_manager.registry.index(s)

        clicked = max(hits, key=z_keys)

        self.set_focused_icon(clicked)
        if clicked.state_tag is not None:
            print(f"State set to: {clicked.state_tag}")
            self.state = clicked.state_tag

    def check_flavor_clicked(self):
        if self.sprite_transitioning:
            return
        if self.focused_flavor_sprite and self.point_in_sprite(self.focused_flavor_sprite):
            return
        hits = []
        for s in self.coordinator.draw_manager.registry:
            if not isinstance(s, Sprite):
                continue
            if s.img_tag != "flavor" or s.render == False:
                continue
            if self.point_in_sprite(s):
                hits.append(s)
        if not hits:
            print("No flavor found")
            self.unfocus_current_flavor()
            return

        def z_keys(s):
            return s.depth, self.coordinator.draw_manager.registry.index(s)

        clicked = max(hits, key=z_keys)
        self.set_focused_flavor(clicked)
        print(f"Focused flavor was set to {clicked.name}")

    def point_in_sprite(self, s,):
            return (s.x <= self.event_pos.x <= s.x + s.w) and (s.y <= self.event_pos.y <= s.y + s.h)

    def set_focused_icon(self, sprite):
        if sprite.moving_home:
            return
        if self.focused_icon_sprite and self.focused_icon_sprite is not sprite:
            self.focused_icon_sprite.focused = False
            self.focused_icon_sprite.moving_home = True
            self.focused_icon_sprite.depth = self.focused_icon_sprite.origin_depth
            self.focused_icon_sprite.icon.show_contents = False
        sprite.focused = True
        sprite.moving_home = False
        sprite.depth = CONSTANTS.FRONT_DEPTH
        self.focused_icon_sprite = sprite

    def unfocus_current_icon(self):
        if not self.focused_icon_sprite:
            self.reset_to_main()
            print("No icon to unfocus")
            return
        self.focused_icon_sprite.focused = False
        self.focused_icon_sprite.moving_home = True
        self.focused_icon_sprite.depth = self.focused_icon_sprite.origin_depth
        self.focused_icon_sprite.icon.show_contents = False
        self.focused_icon_sprite = None

    def set_focused_flavor(self, sprite):
        if sprite.moving_home:
            return
        if self.focused_flavor_sprite and self.focused_flavor_sprite is not sprite:
            self.focused_flavor_sprite.focused = False
            self.focused_flavor_sprite.moving_home = True
            self.focused_flavor_sprite.depth = self.focused_flavor_sprite.icon.sprite.depth + 1
        sprite.focused = True
        sprite.moving_home = False
        sprite.depth = sprite.icon.sprite.depth + 2
        self.focused_flavor_sprite = sprite

    def unfocus_current_flavor(self):
        if not self.focused_flavor_sprite:
            self.reset_to_main()
            print("No flavor to unfocus")
            return
        self.focused_flavor_sprite.focused = False
        self.focused_flavor_sprite.moving_home = True
        self.focused_flavor_sprite.depth = self.focused_flavor_sprite.icon.sprite.depth + 1
        self.focused_flavor_sprite = None

    def reset_to_main(self):
        self.unfocus_current_icon()
        self.active_state = self.state_dict["main"]
        self.state = "main"

    def move_sprite(self):
        if self.dragged_sprite:
            self.dragged_sprite.x = self.event_pos.x - self.dragged_sprite.w // 2
            self.dragged_sprite.y = self.event_pos.y - self.dragged_sprite.h // 2


class UiManager:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.buttons_data = buttons_data
        self.icons_data = icons_data
        self.resolution_profiles = resolution_profiles
        self.active_profile = None

        self.icons_list = []
        self.buttons_list = []

        self.screen = SimpleNamespace(w=0, h=0, short=0, dimensions=None, short_axis=None)
        self.base_resolution = SimpleNamespace(w=0, h=0)
        self.scale = SimpleNamespace(x=0, y=0, image=1, multiplier=1, font=8)
        self.center = SimpleNamespace(x=0, y=0)

        self.pygame = SimpleNamespace(static_canvas=None, dynamic_canvas=None, screen=None, display_info=None)
        self.font = None

        self.focused_sprite = None
        self.focused_scale = 2.125

        self.num_cells = 3
        self.cell_size = None

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
        for attr_value in vars(self.resolution_profiles).values():
            if self.screen.short <= attr_value.max_short:
                self.active_profile = attr_value
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
            icon_sprite.state_tag = key
            icon = Icon(self.coordinator, icon_sprite, key)
            icon.populate_content(self.coordinator.build_flavor_set(key))
            icon_sprite.icon = icon
            self.icons_list.append(icon)

    def setup_icon_grids(self):
        for i in self.icons_list:
            i.setup_grid()
            i.position_content()

    def populate_button_list(self):
        ordered_keys = ["reach_in", "quick", "walk_in"]
        for key in ordered_keys:
            data = getattr(self.buttons_data, key)
            button = Sprite(self.coordinator, data.name, data.image_name)
            button.initialize("button")
            self.buttons_list.append(button)

    def scale_sprites(self, registry=None):
        registry = registry if registry is not None else self.coordinator.draw_manager.registry

        for sprite in registry:
            if isinstance(sprite, list):
                self.scale_sprites(sprite)
            elif isinstance(sprite, Sprite) and sprite.name != "background":
                self.assign_depth(sprite)
                w = sprite.w * self.coordinator.ui_manager.scale.image
                h = sprite.h * self.coordinator.ui_manager.scale.image
                sprite.origin_w = w
                sprite.origin_h = h
                sprite.center_x = self.coordinator.ui_manager.screen.w // 2 - int(sprite.origin_w * self.focused_scale) // 2
                sprite.center_y = self.coordinator.ui_manager.screen.h // 2 - int(sprite.origin_h * self.focused_scale) // 2
                sprite.scale(w, h)

    def assign_depth(self, sprite):
        if sprite.img_tag == "button":
            sprite.depth = CONSTANTS.BUTTON_DEPTH
            sprite.origin_depth = CONSTANTS.BUTTON_DEPTH
        elif sprite.img_tag == "icon":
            sprite.depth = CONSTANTS.ICON_DEPTH
            sprite.origin_depth = CONSTANTS.ICON_DEPTH
        elif sprite.img_tag == "background":
            sprite.depth = CONSTANTS.BACKGROUND_DEPTH

    def update_screen(self):
        self.pygame.screen.fill((0, 0, 0))

    def draw_canvas(self):
        self.pygame.screen.blit(self.pygame.static_canvas, (0, 0))
        self.pygame.screen.blit(self.pygame.dynamic_canvas, (0, 0))

    def draw_icons(self):
        for icon in self.icons_list:
            icon.draw_contents()

    def layout_icons(self):
        if self.screen.short_axis == "height":
            cell_size = self.coordinator.ui_manager.screen.w // self.num_cells
            for i, icon in enumerate(self.icons_list):
                icon.sprite.x = i * cell_size + cell_size // 2 - icon.sprite.w // 2
                icon.sprite.y = self.coordinator.ui_manager.screen.h // 2 - icon.sprite.h
                icon.sprite.origin_x = icon.sprite.x
                icon.sprite.origin_y = icon.sprite.y
                icon.sprite.origin_w = icon.sprite.w
                icon.sprite.origin_h = icon.sprite.h
        else:
            cell_size = self.coordinator.ui_manager.screen.h * .65 // self.num_cells
            for i, icon in enumerate(self.icons_list):
                icon.sprite.x = self.coordinator.ui_manager.screen.w // 2 - icon.sprite.w // 2
                icon.sprite.y = i * cell_size + cell_size // 2 - icon.sprite.h // 2
                icon.sprite.origin_x = icon.sprite.x
                icon.sprite.origin_y = icon.sprite.y
                icon.sprite.origin_w = icon.sprite.w
                icon.sprite.origin_h = icon.sprite.h

    def layout_buttons(self):
        for i, button in enumerate(self.buttons_list):
            button.x = self.icons_list[i].sprite.x
            button.y = self.icons_list[i].sprite.y + self.icons_list[i].sprite.h - button.h // 2
            button.origin_x = button.x
            button.origin_y = button.y
            button.origin_w = button.w
            button.origin_h = button.h

    def draw_grid(self):
        cols = self.screen.w // 30
        rows = self.screen.h // 30
        for c in range(cols):
            x = c * 30
            pygame.draw.line(self.pygame.screen, (255, 255, 255), (x, 0), (x, self.screen.h))
        for r in range(rows):
            y = r * 30
            pygame.draw.line(self.pygame.screen, (255, 255, 255), (0, y), (self.screen.w, y))


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
        surface = pygame.Surface((target_w, target_h), pygame.SRCALPHA)

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

class Icon:
    def __init__(self, coordinator, sprite, name):
        depth = 0
        self.coordinator = coordinator
        self.sprite = sprite
        self.name = name
        self.sprite.initialize("icon")
        self.contents = None
        self.grid = None
        self.show_contents = False

    def populate_content(self, content: list):
        if not isinstance(content, list):
            return
        else:
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
            c.sprite.icon = self
            c.sprite.alpha = 0
            c.sprite.surface.set_alpha(0)
            row = i // self.grid.cols
            col = i % self.grid.cols
            c.sprite.x, c.sprite.y = self.grid.cells[row][col]
            c.sprite.x = c.sprite.x  +self.grid.cell_width // 2 - c.sprite.w // 2
            c.sprite.y = c.sprite.y + self.grid.cell_height // 2 - c.sprite.h // 2
            c.sprite.origin_x, c.sprite.origin_y = c.sprite.x, c.sprite.y

    def draw_contents(self):
        for c in self.contents:
            sprite = c.sprite
            if self.show_contents:
                sprite.render = True
                if sprite.alpha != 255:
                    self.coordinator.animation_manager.lerp_alpha(sprite, 255)
                #self.coordinator.ui_manager.pygame.dynamic_canvas.blit(sprite.surface, (sprite.x, sprite.y))
                sprite.depth = sprite.icon.sprite.depth + 1
                sprite_center_x = sprite.x + sprite.w // 2
                t_x = sprite_center_x - c.text_surface.get_width() // 2
                t_y = sprite.y + sprite.h
                #self.coordinator.ui_manager.pygame.dynamic_canvas.blit(c.text_surface, (t_x, t_y))
            else:
                sprite.render = False
                sprite.alpha = 0
                sprite.surface.set_alpha(sprite.alpha)




def validate_draw(object):
    return hasattr(object, "draw")