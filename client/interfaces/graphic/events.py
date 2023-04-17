import ui


def button_play_online_on_click(document: ui.PageController, button: ui.Element) -> None:
    document.current_page = "waiting_room"

def button_play_with_friend_on_click(document: ui.PageController, button: ui.Element) -> None:
    window = document.get_page("anteroom").get_window("main")
    window.get_element("overlay").style["display"] = True
    form = window.get_element("form")
    form.style["display"] = True
    form.animation = ui.Animation(form, "open")

def button_anteroom_cancel(document: ui.PageController, button: ui.Element) -> None:
    window = document.get_page("anteroom").get_window("main")
    window.get_element("overlay").style["display"] = False
    form = window.get_element("form")
    form.animation = ui.Animation(form, "close")

def button_anteroom_continue(document: ui.PageController, button: ui.Element) -> None:
    pass

def button_leave_waiting_room(document: ui.PageController, button: ui.Element) -> None:
    document.current_page = "anteroom"