from dataclasses import dataclass
from collections.abc import Callable
import numbers, copy

# main framework
import pygame


@dataclass
class Vector2D:
    x: int = 0
    y: int = 0

    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, index):
        return self.x if index == 0 else self.y
    
    def __add__(self, vector):
        return Vector2D(self.x + vector.x, self.y + vector.y)
    
    def __mul__(self, vector):
        return Vector2D(self.x * vector.x, self.y * vector.y)

@dataclass
class Rect:
    p1: Vector2D = Vector2D()
    p2: Vector2D = Vector2D()

    def __iter__(self):
        yield self.p1
        yield self.p2

    @property
    def x1(self) -> int:
        return self.p1.x
    
    @property
    def x2(self) -> int:
        return self.p2.x
    
    @property
    def y1(self) -> int:
        return self.p1.y
    
    @property
    def y2(self) -> int:
        return self.p2.y


class FontsLoader:
    def __init__(self, fonts: dict[str, str]) -> None:
        self.fonts = fonts
        self.cached : dict[tuple[str, int], pygame.font.Font] = {}

    def get(self, name: str, font_weight: int) -> pygame.font.Font:
        if (name, font_weight) not in self.cached:
            self.cached[(name, font_weight)] = pygame.font.Font(self.fonts[name], font_weight)
        return self.cached[(name, font_weight)]


class StyleProcessor:
    @classmethod
    def process(cls, window_size: Vector2D, window_offset: Vector2D, style: dict, style_names: list[str]) -> dict:
        for style_name in style_names:
            style = getattr(cls, style_name)(window_size, window_offset, style)
        return style
    
    @staticmethod
    def procent(value, max_value: float):
        if isinstance(value, str) and len(value) > 0 and value[len(value) - 1] == '%':
            return (float(value[:len(value) - 1]) * max_value) / 100
        return value
    
    @classmethod
    def size(cls, window_size: Vector2D, window_offset: Vector2D, style: dict) -> dict:
        size = style.get("size", [0, 0])
        style["processed"]["size"] = [
            round(cls.procent(size[0], window_size.x)),
            round(cls.procent(size[1], window_size.y))
        ]
        return style
    
    @classmethod
    def margin(cls, window_size: Vector2D, window_offset: Vector2D, style: dict) -> dict:
        margin = style.get("margin", [0, 0])
        style["processed"]["margin"] = [
            round(cls.procent(margin[0], window_size.x)),
            round(cls.procent(margin[1], window_size.y))
        ]
        return style

    @classmethod
    def offset(cls, window_size: Vector2D, window_offset: Vector2D, style: dict) -> dict:
        offset = style.get("offset", [0, 0])
        offset = [
            cls.procent(offset[0], window_size.x),
            cls.procent(offset[1], window_size.y)
        ]
        margin = style["processed"]["margin"]
        size = style["processed"]["size"]
        result = []
        for i in range(2):
            value = offset[i]
            if offset[i] == "left":
                value = 0
            elif offset[i] == "center":
                value = (window_size[i] - size[i]) // 2
            elif offset[i] == "right":
                value = window_size[i] - size[i]
            value += margin[i] + window_offset[i]
            result.append(value)
        style["processed"]["offset"] = result
        return style
    
    @classmethod
    def font_offset(cls, window_size: Vector2D, window_offset: Vector2D, style: dict) -> dict:
        offset = style["processed"]["offset"]
        font_size = style["processed"]["font-size"]
        size = style["processed"]["size"]
        result = []
        for i in range(2):
            result.append(offset[i] + (size[i] - font_size[i]) // 2)
        style["processed"]["font-offset"] = result
        return style
    
    @classmethod
    def font_weight(cls, window_size: Vector2D, window_offset: Vector2D, style: dict) -> dict:
        font_weight = style.get("font-weight", 0)
        style["processed"]["font-weight"] = round(cls.procent(font_weight, window_size.y))
        return style
    

class PageController: pass


class Animation: pass


class Element:
    def __init__(self, z_index : int = 0) -> None:
        self.z_index = z_index
        self.surface = None
        self.fonts_loader = None
        self.document = None
        self.rect = Rect()
        self.window_size : Vector2D = Vector2D()
        self.window_offset : Vector2D = Vector2D()
        self.animation = None
    
    def change_surface(self, surface: pygame.surface.Surface) -> None:
        self.surface = surface

    def update_fonts(self, fonts_loader: FontsLoader) -> None:
        self.fonts_loader = fonts_loader

    def make_reference(self, page_controller: PageController) -> None:
        self.document = page_controller

    def update_bounds(self, window_size: Vector2D, window_offset: Vector2D) -> None:
        self.window_size = window_size
        self.window_offset = window_offset

    def check_state(self, already_caught=False) -> bool:
        return False

    def render(self, events=True) -> None:
        if not self.animation is None:
            self.animation.animate()

    def handle_event(self, event: pygame.event.Event) -> bool:
        return False

    def is_point_in(self, point: Vector2D) -> bool:
        return self.rect.x1 <= point.x <= self.rect.x2 and self.rect.y1 <= point.y <= self.rect.y2
    
class StyledElement(Element):
    class StyleProcessor(StyleProcessor): pass

    def __init__(self, style : dict, *args, **kwargs) -> None:
        super().__init__(*args, z_index=style.get("z-index", 0), **kwargs)
        self.style = style
        self.is_hover = False
        # make processed styles containers
        self.style["processed"] = {}
        if "hover" not in self.style:
            self.style["hover"] = {"processed": {}}
        else:
            self.style["hover"]["processed"] = {}

    def update_style(self) -> None:
        pass

    def process_styles(self, style_names: list[str]) -> None:
        self.style = self.__class__.StyleProcessor.process(
            self.window_size,
            self.window_offset,
            self.style,
            style_names
        )

    def get_style(self, name: str, default=None):
        if self.is_hover:
            if name in self.style["hover"]["processed"]:
                return self.style["hover"]["processed"][name]
            elif name in self.style["hover"]:
                return self.style["hover"][name]
        if name in self.style["processed"]:
            return self.style["processed"][name]
        return self.style.get(name, default)

class Div(StyledElement):
    class StyleProcessor(StyleProcessor): pass

    def __init__(self, elements: dict[str, StyledElement], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.elements = elements
        self.is_hover = False
    
    def update_style(self) -> None:
        super().update_style()
        self.process_styles(["size", "margin", "offset"])
        self.rect = Rect(
            Vector2D(*self.get_style("offset")),
            Vector2D(*self.get_style("offset")) + Vector2D(*self.get_style("size"))
        )
        # create a blending surface (for rounded borders and transparency)
        self.original_image = pygame.Surface(self.get_style("size"))
        self.original_image.set_alpha(self.get_style("alpha", 256))
        self.original_image.fill(pygame.color.Color(self.get_style("background", "black")))

        self.rect_image = pygame.Surface(self.original_image.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(
            self.rect_image,
            (255, 255, 255),
            (0, 0, *self.original_image.get_size()),
            border_radius=self.get_style("border-radius", 0)
        )

        self.image_for_render = self.original_image.copy().convert_alpha()
        self.image_for_render.blit(self.rect_image, (0, 0), None, pygame.BLEND_RGBA_MIN)
        # update chidren
        self.elements_update_bounds()

    def update_bounds(self, window_size: Vector2D, window_offset: Vector2D) -> None:
        super().update_bounds(window_size, window_offset)
        self.update_style()
        self.elements_update_bounds()

    def elements_update_bounds(self) -> None:
        for element in self.elements.values():
            element.update_bounds(
                Vector2D(*self.get_style("size", [0, 0])),
                Vector2D(*self.get_style("offset", [0, 0]))
            )

    def make_reference(self, page_controller: PageController) -> None:
        super().make_reference(page_controller)
        for element in self.elements.values():
            element.make_reference(page_controller)

    def check_state(self, already_caught=False) -> bool:
        if already_caught or not self.get_style("display", True):
            return False
        result = False
        for element in sorted(self.elements.values(), key=lambda element: element.z_index, reverse=True):
            result |= element.check_state(result)
        pos = pygame.mouse.get_pos()
        if self.is_point_in(Vector2D(*pos)):
            self.is_hover = True
            result = True
        else:
            self.is_hover = False
        return result

    def render(self) -> None:
        super().render()
        if not self.get_style("display", True):
            return
        # render to the surface
        self.surface.blit(self.image_for_render, self.get_style("offset", [0, 0]))
        # render other elements
        for element in sorted(self.elements.values(), key=lambda element: element.z_index):
            element.render()

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.get_style("display", True):
            return False
        for element in sorted(self.elements.values(), key=lambda element: element.z_index, reverse=True):
            if element.handle_event(event):
                return True
        pos = pygame.mouse.get_pos()
        if self.is_point_in(Vector2D(*pos)):
            return True
        return False
    
    def get_element(self, element_name: str) -> Element:
        return self.elements[element_name]

    def change_surface(self, surface: pygame.surface.Surface) -> None:
        super().change_surface(surface)
        for element in self.elements.values():
            element.change_surface(surface)

    def update_fonts(self, fonts_loader: FontsLoader) -> None:
        super().update_fonts(fonts_loader)
        for element in self.elements.values():
            element.update_fonts(fonts_loader)

class Button(StyledElement):
    class StyleProcessor(StyleProcessor): pass

    def __init__(self, text: str, on_click: Callable[[PageController, Element], None], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._text = text
        self.on_click = on_click

    @property
    def text(self) -> str:
        return self._text
    
    @text.setter
    def text(self, new_text: str) -> None:
        self._text = new_text
        self.update_style()

    def update_style(self) -> None:
        super().update_style()
        self.process_styles(["size", "margin", "offset", "font_weight"])
        if self.fonts_loader is not None:
            self.text_surface = self.fonts_loader.get(self.get_style("font"), self.get_style("font-weight")).render(
                self.text,
                True,
                pygame.color.Color(self.style.get("color", "white"))
            )
            self.style["processed"]["font-size"] = list(self.text_surface.get_size())
            self.process_styles(["font_offset"])
        # create a rectangle
        self.rect = Rect(
            Vector2D(*self.get_style("offset")),
            Vector2D(*self.get_style("offset")) + Vector2D(*self.get_style("size"))
        )

    def update_bounds(self, window_size: Vector2D, window_offset: Vector2D) -> None:
        super().update_bounds(window_size, window_offset)
        self.update_style()

    def update_fonts(self, fonts_loader: FontsLoader) -> None:
        super().update_fonts(fonts_loader)
        self.update_style()

    def check_state(self, already_caught=False) -> bool:
        if not self.get_style("display", True):
            return False
        # detect mouse
        pos = pygame.mouse.get_pos()
        if not already_caught and self.is_point_in(Vector2D(*pos)):
            if not self.is_hover:
                self.is_hover = True
                pygame.mouse.set_cursor(
                    getattr(pygame, self.get_style("cursor", "SYSTEM_CURSOR_ARROW"))
                )
            return True
        else:
            if self.is_hover:
                self.is_hover = False
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            return False

    def render(self) -> None:
        super().render()
        if not self.get_style("display", True):
            return
        # render to the surface
        if self.get_style("border-width") is not None:
            width = self.get_style("border-width")
            offset = self.get_style("offset")
            size = self.get_style("size")
            pygame.draw.rect(
                self.surface,
                pygame.color.Color(self.get_style("border-color")),
                pygame.Rect(
                    offset[0] - width,
                    offset[1] - width,
                    size[0] + width * 2,
                    size[1] + width * 2
                ),
                width * 2,
                border_radius=self.style.get("border-rect-radius", 0)
            )
        pygame.draw.rect(
            self.surface,
            pygame.color.Color(
                self.get_style("background", "black")
            ),
            pygame.Rect(
                *self.get_style("offset"),
                *self.get_style("size")
            ),
            border_radius=self.style.get("border-radius", 0)
        )
        self.surface.blit(self.text_surface, self.get_style("font-offset"))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.get_style("display", True):
            return False
        if event.type == pygame.MOUSEBUTTONUP:
            if self.is_point_in(Vector2D(*event.pos)):
                self.on_click(self.document, self)
                return True
        return False

class Image(StyledElement):
    class StyleProcessor(StyleProcessor): pass

    def __init__(self, path: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.path = path
        self.angle = 0

    def update_style(self) -> None:
        super().update_style()
        self.process_styles(["size", "margin", "offset"])
        self.rect = Rect(
            Vector2D(*self.get_style("offset")),
            Vector2D(*self.get_style("offset")) + Vector2D(*self.get_style("size"))
        )
        self.image_surface = pygame.image.load(self.path)
        self.image_rect = self.image_surface.get_rect(topleft=self.get_style("offset"))
    
    def update_bounds(self, window_size: Vector2D, window_offset: Vector2D) -> None:
        super().update_bounds(window_size, window_offset)
        self.update_style()

    def render(self) -> None:
        super().render()
        if not self.get_style("display", True):
            return
        period: int = self.get_style("rotation-period", None)
        if period is not None:
            image_surface = pygame.transform.rotate(self.image_surface, self.angle)
            image_rect = image_surface.get_rect(center=self.image_rect.center)
            self.surface.blit(image_surface, image_rect)
            self.angle -= 360 // (period * self.document.fps)
        else:
            self.surface.blit(self.image_surface, self.image_rect)

class Text(StyledElement):
    class StyleProcessor(StyleProcessor): pass

    def __init__(self, text: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._text = text

    @property
    def text(self) -> str:
        return self._text
    
    @text.setter
    def text(self, new_text: str) -> None:
        self._text = new_text
        self.update_style()

    def update_style(self) -> None:
        super().update_style()
        self.process_styles(["font_weight"])
        if self.fonts_loader is not None:
            self.text_surface = self.fonts_loader.get(self.get_style("font"), self.get_style("font-weight")).render(
                self.text,
                True,
                pygame.color.Color(self.get_style("color", "white"))
            )
            self.style["processed"]["font-size"] = list(self.text_surface.get_size())
            self.style["processed"]["size"] = self.style["processed"]["font-size"]
            self.process_styles(["margin", "offset", "font_offset"])
            self.rect = Rect(
                Vector2D(*self.get_style("offset")),
                Vector2D(*self.get_style("offset")) + Vector2D(*self.get_style("size"))
            )
    
    def update_bounds(self, window_size: Vector2D, window_offset: Vector2D) -> None:
        super().update_bounds(window_size, window_offset)
        self.update_style()

    def update_fonts(self, fonts_loader: FontsLoader) -> None:
        super().update_fonts(fonts_loader)
        self.update_style()

    def render(self) -> None:
        super().render()
        if not self.get_style("display", True):
            return
        self.surface.blit(self.text_surface, self.get_style("font-offset"))

class Grid(StyledElement):
    class StyleProcessor(StyleProcessor):
        pass

    def __init__(self, size: Vector2D, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.size = size
        self.rect = Rect()

    def update_style(self) -> None:
        super().update_style()
        self.style["processed"]["size"] = list(self.size * Vector2D(*self.get_style("cell-size", [0, 0])) + Vector2D(1, 1))
        self.process_styles(["margin", "offset"])
        self.rect = Rect(
            Vector2D(*self.get_style("offset")),
            Vector2D(*self.get_style("offset")) + Vector2D(*self.get_style("size"))
        )
    
    def update_bounds(self, window_size: Vector2D, window_offset: Vector2D) -> None:
        super().update_bounds(window_size, window_offset)
        self.update_style()

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.get_style("display", True):
            return False
        return False

    def render(self) -> None:
        super().render()
        if not self.get_style("display", True):
            return
        pygame.draw.rect(
            self.surface,
            pygame.color.Color(
                self.get_style("background", "black")
            ),
            pygame.Rect(
                *self.get_style("offset"),
                *self.get_style("size")
            )
        )
        # draw the grid
        # horizontal lines
        for i in range(self.size[0] + 1):
            offset = Vector2D(*self.get_style("offset")) + Vector2D(i * self.style["cell-size"][0], 0)
            pygame.draw.rect(
                self.surface,
                pygame.color.Color(
                    self.get_style("color", "white")
                ),
                pygame.Rect(
                    offset.x, offset.y,
                    1, self.get_style("size")[1]
                )
            )
        # vertical lines
        for i in range(self.size[1] + 1):
            offset = Vector2D(*self.get_style("offset")) + Vector2D(0, i * self.style["cell-size"][1])
            pygame.draw.rect(
                self.surface,
                pygame.color.Color(
                    self.get_style("color", "white")
                ),
                pygame.Rect(
                    offset.x, offset.y,
                    self.get_style("size")[0], 1
                )
            )
        # draw move
        self.render_expected_move()

    def render_expected_move(self):
        # pygame.draw.circle(self.surface, self., (x, y), R, w)
        pass

class InputInteger(StyledElement):
    class StyleProcessor(StyleProcessor):
        @classmethod
        def font_margin(cls, window_size: Vector2D, window_offset: Vector2D, style: dict) -> dict:
            window_size = Vector2D(*style["processed"]["size"])
            window_offset = Vector2D(*style["processed"]["offset"])
            margin = style.get("font-margin", [0, 0])
            style["processed"]["font-margin"] = [
                round(cls.procent(margin[0], window_size.x)),
                round(cls.procent(margin[1], window_size.y))
            ]
            return style

        @classmethod
        def font_offset(cls, window_size: Vector2D, window_offset: Vector2D, style: dict) -> dict:
            window_size = Vector2D(*style["processed"]["size"])
            window_offset = Vector2D(*style["processed"]["offset"])
            offset = style.get("font-offset", [0, 0])
            offset = [
                cls.procent(offset[0], window_size.x),
                cls.procent(offset[1], window_size.y)
            ]
            margin = style["processed"]["font-margin"]
            size = style["processed"]["font-size"]
            result = []
            for i in range(2):
                value = offset[i]
                if offset[i] == "left":
                    value = 0
                elif offset[i] == "center":
                    value = (window_size[i] - size[i]) // 2
                elif offset[i] == "right":
                    value = window_size[i] - size[i]
                value += margin[i] + window_offset[i]
                result.append(value)
            style["processed"]["font-offset"] = result
            return style

    def __init__(self, value: int, min_value: int, max_value: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._value = value
        self.min_value = min_value
        self.max_value = max_value

    @property
    def value(self) -> int:
        return self._value
    
    @value.setter
    def value(self, new_value: int) -> None:
        self._value = new_value
        self.update_style()

    def update_style(self) -> None:
        super().update_style()
        self.process_styles(["size", "margin", "offset", "font_weight"])
        if self.fonts_loader is not None:
            self.text_surface = self.fonts_loader.get(self.get_style("font"), self.get_style("font-weight")).render(
                str(self.value),
                True,
                pygame.color.Color(self.style.get("color", "white"))
            )
            self.style["processed"]["font-size"] = list(self.text_surface.get_size())
            self.process_styles(["font_margin", "font_offset"])
        # create a rectangle
        self.rect = Rect(
            Vector2D(*self.get_style("offset")),
            Vector2D(*self.get_style("offset")) + Vector2D(*self.get_style("size"))
        )

    def update_bounds(self, window_size: Vector2D, window_offset: Vector2D) -> None:
        super().update_bounds(window_size, window_offset)
        self.update_style()

    def update_fonts(self, fonts_loader: FontsLoader) -> None:
        super().update_fonts(fonts_loader)
        self.update_style()

    def check_state(self, already_caught=False) -> bool:
        if not self.get_style("display", True):
            return False
        # detect mouse
        pos = pygame.mouse.get_pos()
        if not already_caught and self.is_point_in(Vector2D(*pos)):
            if not self.is_hover:
                self.is_hover = True
                pygame.mouse.set_cursor(
                    getattr(pygame, self.get_style("cursor", "SYSTEM_CURSOR_ARROW"))
                )
            return True
        else:
            if self.is_hover:
                self.is_hover = False
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            return False

    def render(self) -> None:
        super().render()
        if not self.get_style("display", True):
            return
        # render to the surface
        if self.get_style("border-width") is not None:
            width = self.get_style("border-width")
            offset = self.get_style("offset")
            size = self.get_style("size")
            pygame.draw.rect(
                self.surface,
                pygame.color.Color(self.get_style("border-color")),
                pygame.Rect(
                    offset[0] - width,
                    offset[1] - width,
                    size[0] + width * 2,
                    size[1] + width * 2
                ),
                width * 2,
                border_radius=self.style.get("border-rect-radius", 0)
            )
        pygame.draw.rect(
            self.surface,
            pygame.color.Color(
                self.get_style("background", "black")
            ),
            pygame.Rect(
                *self.get_style("offset"),
                *self.get_style("size")
            ),
            border_radius=self.style.get("border-radius", 0)
        )
        self.surface.blit(self.text_surface, self.get_style("font-offset"))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.get_style("display", True):
            return False
        if event.type == pygame.MOUSEWHEEL and self.is_point_in(Vector2D(*pygame.mouse.get_pos())):
            if event.y < 0:
                self.value = max(self.min_value, self.value - 1)
            elif event.y > 0:
                self.value = min(self.max_value, self.value + 1)
        return False


class Animation(object):
    def __init__(self, element: Element, animation_name: str) -> None:
        self.element = element
        self.animation_name = animation_name
        self.done = False
        self.fps = self.element.document.fps
        self.frames = round(self.fps * self.get_animation_style("duration"))

    def animate(self) -> None:
        if self.done:
            return
        for style_name in self.get_animation_style("styles"):
            self.element.style[style_name] = self.animate_style(
                self.get_style(style_name),
                self.get_animation_style(style_name)
            )
        self.element.update_style()
        self.frames -= 1
        if self.frames == 0:
            self.done = True
            # change accroding to the config
            for key, value in self.get_animation_style("on_done").items():
                self.element.style[key] = value

    def animate_style(self, style, new_style):
        if isinstance(style, list):
            result = []
            for style_el, new_style_el in zip(style, new_style):
                result.append(self.animate_style(style_el, new_style_el))
            return result
        if isinstance(style, numbers.Number):
            return style + (new_style - style) // self.frames
        raise TypeError("Animate error, style is not a number!")

    def get_style(self, style_name: str):
        return self.element.get_style(style_name)
    
    def get_animation_style(self, style_name: str):
        return self.element.style["animation"][self.animation_name][style_name]


class Window:
    def __init__(self, size: Vector2D, offset: Vector2D, elements: dict[str, Element], z_index: int = 0) -> None:
        self.size = size
        self.offset = offset
        self.elements = elements
        self.z_index = z_index
        self.surface = None

        self.update_bounds()

    def change_surface(self, surface: pygame.surface.Surface) -> None:
        self.surface = surface
        for element in self.elements.values():
            element.change_surface(surface)

    def update_fonts(self, fonts_loader: FontsLoader) -> None:
        for element in self.elements.values():
            element.update_fonts(fonts_loader)

    def make_reference(self, page_controller: PageController) -> None:
        for element in self.elements.values():
            element.make_reference(page_controller)

    def render(self) -> None:
        for element in sorted(self.elements.values(), key=lambda element: element.z_index): # TODO
            element.render()
        
    def check_state(self, already_caught=False) -> bool:
        result = False
        for element in sorted(self.elements.values(), key=lambda element: element.z_index, reverse=True):
            result |= element.check_state(result)
        return result

    def handle_event(self, event: pygame.event.Event) -> bool:
        for element in sorted(self.elements.values(), key=lambda element: element.z_index, reverse=True):
            if element.handle_event(event):
                return True
        return False

    def update_bounds(self) -> None:
        for element in self.elements.values():
            element.update_bounds(self.size, self.offset)

    def get_element(self, element_name: str) -> Element:
        return self.elements[element_name]


class Page:
    def __init__(self, background: pygame.Color, windows: dict[str, Window]) -> None:
        self.background = background
        self.windows =  windows
        self.surface = None

    def change_surface(self, surface: pygame.surface.Surface) -> None:
        self.surface = surface
        for window in self.windows.values():
            window.change_surface(surface)

    def update_fonts(self, fonts_loader: FontsLoader) -> None:
        for window in self.windows.values():
            window.update_fonts(fonts_loader)

    def make_reference(self, page_controller: PageController) -> None:
        for window in self.windows.values():
            window.make_reference(page_controller)

    def render(self) -> None:
        for window in sorted(self.windows.values(), key=lambda window: window.z_index): # TODO
            window.render()

    def check_state(self) -> bool:
        result = False
        for window in sorted(self.windows.values(), key=lambda window: window.z_index, reverse=True):
            result |= window.check_state(result)
        return result

    def handle_event(self, event: pygame.event.Event) -> None:
        for window in sorted(self.windows.values(), key=lambda window: window.z_index, reverse=True):
            if window.handle_event(event):
                break

    def get_window(self, window_name: str) -> Window:
        return self.windows[window_name]


class PageController(object):
    def __init__(self, pages: dict[str, Page], current_page: str, fps: int) -> None:
        self.pages = pages
        self._current_page = current_page
        self.fps = fps
        self.surface = None

    @property
    def current_page(self) -> str:
        return self._current_page
    
    @current_page.setter
    def current_page(self, new_page_name: str) -> None:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        self._current_page = new_page_name

    def change_surface(self, surface: pygame.surface.Surface) -> None:
        self.surface = surface
        for page in self.pages.values():
            page.change_surface(surface)

    def update_fonts(self, fonts_loader: FontsLoader) -> None:
        for page in self.pages.values():
            page.update_fonts(fonts_loader)

    def make_reference(self) -> None:
        for page in self.pages.values():
            page.make_reference(self)

    def check_state(self) -> None:
        self.get_current_page().check_state()

    def render(self) -> None:
        self.get_current_page().render()

    def handle_event(self, event: pygame.event.Event) -> None:
        self.pages[self.current_page].handle_event(event)

    def get_page(self, page_name: str) -> Page:
        return self.pages[page_name]
    
    def get_current_page(self) -> Page:
        return self.get_page(self.current_page)