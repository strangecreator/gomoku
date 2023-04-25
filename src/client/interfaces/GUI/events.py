import sys
from pathlib import Path

# base path resolving
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

from src.client.config_loader import *

# dependencies
import helper, ui, bridges, uuid


# anteroom
def button_play_online_on_click(document: ui.PageController, \
                                button: ui.Element) -> None:
    document.current_page = "waiting_room"
    # creating a bridge
    # generate a new unique user key
    USER_ID = str(uuid.uuid4())
    bridge = bridges.BridgeOnline(
        config.logic.amount,
        config.logic.size,
        USER_ID,
        document
    )
    document.bridge_connector = bridges.BridgeConnector(bridge)
    # make a new grid
    make_grid(document, config.logic.size)
    # show text
    panel_container = document.get_page("battle").get_window("main")\
        .get_element("container").get_element("panel-container")
    panel_container.get_element("player_1")\
        .get_element("name").text = "Opponent"
    panel_container.get_element("player_2").get_element("name").text = "You"
    message = panel_container.get_element("text")
    message.text = "Waiting for\nthe server"
    message.style["color"] = message.style["message-color"]
    message.update_style()

def button_play_with_friend_on_click(document: ui.PageController, \
                                     button: ui.Element) -> None:
    window = document.get_page("anteroom").get_window("main")
    window.get_element("overlay").style["display"] = True
    form = window.get_element("form")
    form.style["display"] = True
    form.animation = ui.Animation(form, "open")

def button_anteroom_cancel(document: ui.PageController, \
                           button: ui.Element) -> None:
    window = document.get_page("anteroom").get_window("main")
    window.get_element("overlay").style["display"] = False
    form = window.get_element("form")
    form.animation = ui.Animation(form, "close")

def button_anteroom_continue(document: ui.PageController, \
                             button: ui.Element) -> None:
    # reading data from the form
    form = document.get_page("anteroom").get_window("main") \
        .get_element("form")
    amount = form.get_element("input_field_0").value
    field_size = (
        form.get_element("input_field_1").value,
        form.get_element("input_field_2").value
    )
    timeout = form.get_element("input_field_3").value
    #
    bridge = bridges.BridgeOffline(amount, field_size, timeout, document)
    document.bridge_connector = bridges.BridgeConnector(bridge)
    # creating a new grid
    make_grid(document, field_size)
    # change text
    panel_container = document.get_page("battle").get_window("main") \
        .get_element("container").get_element("panel-container")
    panel_container.get_element("player_1") \
        .get_element("name").text = "Player 1"
    panel_container.get_element("player_2") \
        .get_element("name").text = "Player 2"
    message = panel_container.get_element("text")
    message.text = "Player 1's move"
    message.style["color"] = message.style["message-color"]
    message.update_style()
    # revealing
    document.current_page = "battle"    

def make_grid(document: ui.PageController, field_size) -> None:
    # creating a new grid
    new_grid = ui.Grid(
        ui.Vector2D(*field_size),
        helper.to_dict(config.interface.pages.battle.elements\
            .container.elements.grid_container.elements.grid.style)
    )
    new_grid.change_surface(document.surface)
    new_grid.update_fonts(document.fonts_loader)
    new_grid.make_reference(document)
    # adding to the page
    grid_container = document.get_page("battle") \
        .get_window("main").get_element("container") \
            .get_element("grid-container")
    grid_container.elements["grid"] = new_grid
    grid_container.elements_update_bounds()

# waiting room
def button_leave_waiting_room(document: ui.PageController, \
                               button: ui.Element) -> None:
    document.bridge_connector.close()
    document.bridge_connector = None
    # revealing
    document.current_page = "anteroom"

# battle room
def button_resign(document: ui.PageController, button: ui.Element) -> None:
    document.bridge_connector.resign()

def button_leave_battle(document: ui.PageController, \
                         button: ui.Element) -> None:
    document.bridge_connector.close()
    # revealing anteroom page
    document.current_page = "anteroom"
    # changing buttons
    container = document.get_page("battle").get_window("main") \
        .get_element("container").get_element("panel-container")
    container.get_element("leave").style["display"] = False
    container.get_element("resign").style["display"] = True
    container.get_element("resign").is_hover = False
    container.get_element("text").style["color"] = container \
        .get_element("text").style["message-color"]