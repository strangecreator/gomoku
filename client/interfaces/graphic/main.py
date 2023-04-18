import os, sys
from pathlib import Path

# base path resolving
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

print(BASE_DIR)

# dependencies
from game_logic.main import State
from connection.main import Connection
import ui, events, helper

# global configuration
import json
from types import SimpleNamespace

config = json.load(
    open(str(Path(BASE_DIR, "config.json")), 'r'),
    object_hook=lambda d: SimpleNamespace(**d)
)

# main framework
import pygame


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    fonts_loader = ui.FontsLoader(helper.to_dict(config.interface.fonts))

    page_controller = ui.PageController(
        {
            "anteroom": ui.Page(
                pygame.Color(config.interface.pages.anteroom.style.background),
                {
                    "main": ui.Window(
                        ui.Vector2D(*screen.get_size()),
                        ui.Vector2D(0, 0), {
                        "button_play_online": ui.Button(
                            config.interface.pages.anteroom.elements.button_play_online.text,
                            events.button_play_online_on_click,
                            helper.to_dict(config.interface.pages.anteroom.elements.button_play_online.style)
                        ),
                        "button_play_with_friend": ui.Button(
                            config.interface.pages.anteroom.elements.button_play_with_friend.text,
                            events.button_play_with_friend_on_click,
                            helper.to_dict(config.interface.pages.anteroom.elements.button_play_with_friend.style)
                        ),
                        "overlay": ui.Div(
                            {},
                            helper.to_dict(config.interface.pages.anteroom.elements.overlay.style)
                        ),
                        "form": ui.Div(
                            {
                                "input_field_1": ui.InputInteger(
                                    config.interface.pages.anteroom.elements.form.elements.input_field_1.value,
                                    config.interface.pages.anteroom.elements.form.elements.input_field_1.min_value,
                                    config.interface.pages.anteroom.elements.form.elements.input_field_1.max_value,
                                    helper.to_dict(config.interface.pages.anteroom.elements.form.elements.input_field_1.style)
                                ),
                                "input_field_2": ui.InputInteger(
                                    config.interface.pages.anteroom.elements.form.elements.input_field_2.value,
                                    config.interface.pages.anteroom.elements.form.elements.input_field_2.min_value,
                                    config.interface.pages.anteroom.elements.form.elements.input_field_2.max_value,
                                    helper.to_dict(config.interface.pages.anteroom.elements.form.elements.input_field_2.style)
                                ),
                                "input_field_3": ui.InputInteger(
                                    config.interface.pages.anteroom.elements.form.elements.input_field_3.value,
                                    config.interface.pages.anteroom.elements.form.elements.input_field_3.min_value,
                                    config.interface.pages.anteroom.elements.form.elements.input_field_3.max_value,
                                    helper.to_dict(config.interface.pages.anteroom.elements.form.elements.input_field_3.style)
                                ),
                                "label_field_1": ui.Text(
                                    config.interface.pages.anteroom.elements.form.elements.label_field_1.text,
                                    helper.to_dict(config.interface.pages.anteroom.elements.form.elements.label_field_1.style)
                                ),
                                "label_field_2": ui.Text(
                                    config.interface.pages.anteroom.elements.form.elements.label_field_2.text,
                                    helper.to_dict(config.interface.pages.anteroom.elements.form.elements.label_field_2.style)
                                ),
                                "label_field_3": ui.Text(
                                    config.interface.pages.anteroom.elements.form.elements.label_field_3.text,
                                    helper.to_dict(config.interface.pages.anteroom.elements.form.elements.label_field_3.style)
                                ),
                                "cancel": ui.Button(
                                    config.interface.pages.anteroom.elements.form.elements.cancel.text,
                                    events.button_anteroom_cancel,
                                    helper.to_dict(config.interface.pages.anteroom.elements.form.elements.cancel.style)
                                ),
                                "continue_button": ui.Button(
                                    config.interface.pages.anteroom.elements.form.elements.continue_button.text,
                                    events.button_anteroom_continue,
                                    helper.to_dict(config.interface.pages.anteroom.elements.form.elements.continue_button.style)
                                )
                            },
                            helper.to_dict(config.interface.pages.anteroom.elements.form.style)
                        )
                    }, 0)
                }
            ),
            "waiting_room": ui.Page(
                pygame.Color(config.interface.pages.waiting_room.style.background),
                {
                    "main": ui.Window(
                        ui.Vector2D(*screen.get_size()),
                        ui.Vector2D(0, 0),
                        {
                            "image": ui.Image(
                                BASE_DIR.parent / config.interface.pages.waiting_room.elements.loader.path,
                                helper.to_dict(config.interface.pages.waiting_room.elements.loader.style)
                            ),
                            "text": ui.Text(
                                config.interface.pages.waiting_room.elements.text.text,
                                helper.to_dict(config.interface.pages.waiting_room.elements.text.style)
                            ),
                            "leave": ui.Button(
                                config.interface.pages.waiting_room.elements.leave.text,
                                events.button_leave_waiting_room,
                                helper.to_dict(config.interface.pages.waiting_room.elements.leave.style)
                            )
                        },
                        0
                    )
                }
            ),
            "battle": ui.Page(
                pygame.Color(config.interface.pages.battle.style.background),
                {
                    "main": ui.Window(
                        ui.Vector2D(*screen.get_size()),
                        ui.Vector2D(),
                        {
                            "grid": ui.Grid(
                                ui.Vector2D(16, 16),
                                helper.to_dict(config.interface.pages.battle.elements.grid.style)
                            )
                        },
                        0
                    )
                }
            )
        },
        "anteroom",
        config.interface.fps
    )

    page_controller.change_surface(screen)
    page_controller.update_fonts(fonts_loader)
    page_controller.make_reference()

    executing = True
    while executing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                executing = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                executing = False
            page_controller.handle_event(event)

        screen.fill(page_controller.get_current_page().background)

        page_controller.check_state()
        page_controller.render()

        pygame.display.update()
        clock.tick(config.interface.fps)

    pygame.quit()