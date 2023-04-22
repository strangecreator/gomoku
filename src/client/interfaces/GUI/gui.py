import sys
from pathlib import Path

# base path resolving
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

from src.client.config_loader import *

# dependencies
import ui, events, helper

# global configuration
import uuid

# main framework
import pygame


if __name__ == "__main__":
    # framework initialization
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    # load fonts
    fonts_loader = ui.FontsLoader(helper.to_dict(config.interface.fonts))
    # perform initial ui configuration (before)
    ui.apply_initial_configuration_before(config, helper.Vector2D(*screen.get_size()))
    # pages creation and initialization
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
                                "input_field_0": ui.InputInteger(
                                    config.interface.pages.anteroom.elements.form.elements.input_field_0.value,
                                    config.interface.pages.anteroom.elements.form.elements.input_field_0.min_value,
                                    config.interface.pages.anteroom.elements.form.elements.input_field_0.max_value,
                                    helper.to_dict(config.interface.pages.anteroom.elements.form.elements.input_field_0.style)
                                ),
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
                                "label_field_0": ui.Text(
                                    config.interface.pages.anteroom.elements.form.elements.label_field_0.text,
                                    helper.to_dict(config.interface.pages.anteroom.elements.form.elements.label_field_0.style)
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
                                BASE_DIR / config.interface.pages.waiting_room.elements.loader.path,
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
                            "container": ui.Div(
                                {
                                    "grid-container": ui.Div(
                                        {
                                            "grid": ui.Grid(
                                                ui.Vector2D(19, 18),
                                                helper.to_dict(config.interface.pages.battle.elements.container.elements.grid_container.elements.grid.style)
                                            )
                                        },
                                        helper.to_dict(config.interface.pages.battle.elements.container.elements.grid_container.style)
                                    ),
                                    "panel-container": ui.Div(
                                        {
                                            "player_1": ui.Div(
                                                {
                                                    "time": ui.Button(
                                                        config.interface.pages.battle.elements.container.elements.panel_container.elements.player_1.elements.time.text,
                                                        lambda document, element: None,
                                                        helper.to_dict(config.interface.pages.battle.elements.container.elements.panel_container.elements.player_1.elements.time.style)
                                                    ),
                                                    "name": ui.Text(
                                                        config.interface.pages.battle.elements.container.elements.panel_container.elements.player_1.elements.name.text,
                                                        helper.to_dict(config.interface.pages.battle.elements.container.elements.panel_container.elements.player_1.elements.name.style)
                                                    )
                                                },
                                                helper.to_dict(config.interface.pages.battle.elements.container.elements.panel_container.elements.player_1.style)
                                            ),
                                            "player_2": ui.Div(
                                                {
                                                    "time": ui.Button(
                                                        config.interface.pages.battle.elements.container.elements.panel_container.elements.player_2.elements.time.text,
                                                        lambda document, element: None,
                                                        helper.to_dict(config.interface.pages.battle.elements.container.elements.panel_container.elements.player_2.elements.time.style)
                                                    ),
                                                    "name": ui.Text(
                                                        config.interface.pages.battle.elements.container.elements.panel_container.elements.player_2.elements.name.text,
                                                        helper.to_dict(config.interface.pages.battle.elements.container.elements.panel_container.elements.player_2.elements.name.style)
                                                    )
                                                },
                                                helper.to_dict(config.interface.pages.battle.elements.container.elements.panel_container.elements.player_2.style)
                                            ),
                                            "resign": ui.Button(
                                                config.interface.pages.battle.elements.container.elements.panel_container.elements.resign.text,
                                                events.button_resign,
                                                helper.to_dict(config.interface.pages.battle.elements.container.elements.panel_container.elements.resign.style)
                                            ),
                                            "leave": ui.Button(
                                                config.interface.pages.battle.elements.container.elements.panel_container.elements.leave.text,
                                                events.button_leave_battle,
                                                helper.to_dict(config.interface.pages.battle.elements.container.elements.panel_container.elements.leave.style)
                                            ),
                                            "text": ui.Text(
                                                config.interface.pages.battle.elements.container.elements.panel_container.elements.text.text,
                                                helper.to_dict(config.interface.pages.battle.elements.container.elements.panel_container.elements.text.style)
                                            )
                                        },
                                        helper.to_dict(config.interface.pages.battle.elements.container.elements.panel_container.style)
                                    )
                                },
                                helper.to_dict(config.interface.pages.battle.elements.container.style)
                            ),
                        },
                        0
                    )
                }
            )
        },
        current_page="anteroom",
        fps=config.interface.fps
    )
    
    page_controller.change_surface(screen)
    page_controller.update_fonts(fonts_loader)
    page_controller.make_reference()
    # perform initial ui configuration (after)
    ui.apply_initial_configuration_after(page_controller)
    # game loop
    executing = True
    while executing:
        # events checking
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                executing = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                executing = False
            page_controller.handle_event(event)
        # setting background of the screen
        screen.fill(page_controller.get_current_page().background)
        # checking mouse (hover + other mouse positions) and rendering
        page_controller.check_state()
        page_controller.render()
        # update of main framework
        pygame.display.update()
        clock.tick(config.interface.fps)

    if page_controller.bridge_connector is not None:
        page_controller.bridge_connector.close()
    pygame.quit()