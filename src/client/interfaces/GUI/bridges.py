import sys
from pathlib import Path

# base path resolving
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

from src.client.config_loader import *

from dataclasses import dataclass
import time, copy, threading

# dependencies
from src.client.connection.connection import Connection
from src.client.game_logic.game_logic import State

import ui


class Bridge:
    @dataclass
    class MovesHandler:
        moves: tuple[set[tuple[int, int]], set[tuple[int, int]]]
        color: tuple[int, int]

    def __init__(self, amount: int, field_size: tuple[int, int], \
                 document: ui.PageController) -> None:
        self.state = State(amount, field_size)
        self.has_begun = False
        self.document = document
        self.player_index = 0
        self.last_move = None
        self.timeout = 5 * 60 # will be defined in descendant
        self.time_last_move = [time.time(), time.time()]
        self.time_remaining = [float(self.timeout), float(self.timeout)]
        #
        self.move_texts = [
            {
                "text": "Player 1's\nmove",
                "color": "message"
            },
            {
                "text": "Player 2's\nmove",
                "color": "message"
            }
        ]
        self.win_texts = [
            {
                "text": "Player 1\nhas won",
                "color": "success"
            },
            {
                "text": "Player 2\nhas won",
                "color": "success"
            }
        ]
        self.resignation_texts = [
            {
                "text": "Player 1\nhas resigned!",
                "color": "error"
            },
            {
                "text": "Player 2\nhas resigned!",
                "color": "error"
            }
        ]
        # 
        self.track = True
    
    @property
    def track_color(self) -> int:
        return self.state.turn

    def update(self) -> None:
        if not self.has_begun or self.state.over:
            return
        time_remaining_current = self._compute_current_remaining_time()
        if time_remaining_current[self.state.turn] < 0:
            self.state.over = True
            self._game_over_process()
        # update of clocks
        self._update_clocks(time_remaining_current)

    def get_moves(self) -> MovesHandler:
        return Bridge.MovesHandler(self.state.moves, (0, 1))
    
    def make_move(self, move: tuple[int, int]) -> None:
        if self.state.over:
            return
        self.state.add(move)
        self.last_move = move
        # check state
        if self.state.over:
            self._game_over_process()
        else:
            self.time_remaining[self.state.turn ^ 1] -= (time.time() - \
                self.time_last_move[self.state.turn])
            self.time_last_move[self.state.turn ^ 1] = time.time()
            # show text
            self._whose_move(self.state.turn)

    def is_move_in_field(self, move: tuple[int, int]) -> bool:
        return self.state._is_move_in_field(move)

    def is_move_done(self, move: tuple[int, int]) -> bool:
        return self.state._is_move_done(move)
    
    def resign(self) -> None:
        self.state.over = True
        self.track = False
        # show text
        self._who_resigned(self.state.turn)

    def close(self, *args, **kwargs) -> None:
        pass

    # private methods
    def _compute_current_remaining_time(self) -> list[float]:
        time_remaining_current = copy.copy(self.time_remaining)
        time_remaining_current[self.state.turn] = (
            self.time_remaining[self.state.turn] - 
                    (time.time() - self.time_last_move[self.state.turn ^ 1])
        )
        return time_remaining_current

    def _game_over_process(self) -> None:
        self.track = False
        # show text
        container = self._get_panel_container()
        message = container.get_element("text")
        if self.state.draw:
            message.text = "The game\nis a draw"
            message.style["color"] = message.style["message-color"]
        else:
            message.text = self.win_texts[self.state.turn ^ 1]["text"]
            message.style["color"] = message.style[
                f"{self.win_texts[self.state.turn ^ 1]['color']}-color"
            ]
        message.update_style()
        self._show_leave_button()

    def _whose_move(self, player_id) -> None:
        container = self._get_panel_container()
        message = container.get_element("text")
        message.text = self.move_texts[player_id]["text"]
        message.style["color"] = message.style[
            f"{self.move_texts[player_id]['color']}-color"
        ]
        message.update_style()

    def _who_resigned(self, player_id) -> None:
        container = self._get_panel_container()
        message = container.get_element("text")
        message.text = self.resignation_texts[player_id]["text"]
        message.style["color"] = message.style[
            f"{self.resignation_texts[player_id]['color']}-color"
        ]
        message.update_style()
        self._show_leave_button()

    def _get_panel_container(self) -> ui.Element:
        return self.document.get_page("battle").get_window("main") \
            .get_element("container").get_element("panel-container")
    
    def _show_leave_button(self) -> None:
        container = self._get_panel_container()
        container.get_element("leave").style["display"] = True
        container.get_element("resign").style["display"] = False

    def _add_zero(self, number: int) -> str:
        return str(number) if number > 9 else '0' + str(number)
    
    def _float_to_time(self, time: float) -> str:
        time = time if time >= 0 else 0
        minutes = self._add_zero(round(time) // 60)
        seconds = self._add_zero(round(time) % 60)
        return f"{minutes}:{seconds}"

    def _update_clocks(self, time_remaining: list[float]) -> None:
        container = self._get_panel_container()
        clocks = (
            container.get_element("player_1").get_element("time"),
            container.get_element("player_2").get_element("time")
        )
        for i, clock in enumerate(clocks):
            clock.text = self._float_to_time(time_remaining[i])
            clock.update_style()

class BridgeOffline(Bridge):
    def __init__(self, amount: int, field_size: tuple[int, int], \
                  timeout: int, document: ui.PageController) -> None:
        super().__init__(amount, field_size, document)
        self.has_begun = True
        self.timeout = timeout * 60
        self.time_remaining = [float(self.timeout), float(self.timeout)]
        

class BridgeOnline(Bridge):
    def __init__(self, amount: int, field_size: tuple[int, int], \
                  user_id: str, document: ui.PageController) -> None:
        super().__init__(amount, field_size, document)
        self.connection = Connection(user_id)
        self.user_id = user_id
        self.web_game_state = None
        self.opponent_id = None
        self.opponent_last_move = None
        #
        self.move_texts = [
            {
                "text": "Waiting for\nopponent...",
                "color": "message"
            },
            {
                "text": "Your move!",
                "color": "message"
            }
        ]
        self.win_texts = [
            {
                "text": "You've lost!",
                "color": "error"
            },
            {
                "text": "You've won!",
                "color": "success"
            }
        ]
        self.resignation_texts = [
            {
                "text": "Opponent has\nresigned!",
                "color": "success"
            },
            {
                "text": "You've\nresigned!",
                "color": "error"
            }
        ]
        # make connection
        threading.Thread(
            target=self.connection.make_connection,
            args=(self.process_game_id,)
        ).start()

    @property
    def track_color(self) -> int:
        return self.state.turn ^ self.player_index ^ 1

    def process_game_id(self, response) -> None:
        self.has_begun = True
        # get opponent id
        if response["players"][0] == self.user_id:
            self.opponent_id = response["players"][1]
        else:
            self.opponent_id = response["players"][0]
        self.timeout = response["timeout"]
        self.update_state(response, process_time=True)
        # 
        if self.web_game_state["turn"] == self.user_id:
            self.player_index = 1
            self.track = True
        else:
            self.player_index = 0
            self.track = False
        # monotonous request
        threading.Thread(
            target=self.connection.get_state_monotonous,
            args=(self.update_state,)
        ).start()
        # show board
        self._show_board()

    def update_state(self, response, process_time=False) -> None:
        self.web_game_state = response
        if process_time:
            # process timeout
            self._update_time()
        # check last move
        if self.web_game_state[
                self.opponent_id
            ]["last_move"] != self.opponent_last_move:
            self.opponent_last_move = self.web_game_state[
                self.opponent_id
            ]["last_move"]
            # process timeout
            self._update_time()
            self.make_move(
                tuple(self.opponent_last_move),
                request_to_server=False,
                process_time=False,
                track_anyway=True
            )
            self.track = True
        if self.web_game_state["is_over"]:
            if not self.state.over: # resignation
                self.resign(0)
                self.state.over = True
                self.connection.close()

    def update(self) -> None:
        if not self.has_begun or self.state.over:
            return
        time_remaining_current = self._compute_current_remaining_time()
        if time_remaining_current[self.state.turn ^ self.player_index] < 0:
            self.state.over = True
            self._game_over_process()
            self.connection.close()
        # update of clocks
        self._update_clocks(time_remaining_current)
    
    def get_moves(self) -> Bridge.MovesHandler:
        return Bridge.MovesHandler(
            self.state.moves,
            (0, 1) if self.player_index == 1 else (1, 0)
        )

    def make_move(self, move: tuple[int, int], request_to_server=True, \
                   process_time=True, track_anyway=False) -> None:
        if self.state.over:
            return
        # if it's not our turn
        if not self.track and not track_anyway:
            return
        self.state.add(move)
        self.last_move = move
        self.track = False
        # check state
        if self.state.over:
            self._game_over_process()
        else:
            if process_time:
                self.time_remaining[
                    self.state.turn ^ self.player_index ^ 1
                ] -= (time.time() - self.time_last_move[
                    self.state.turn ^ self.player_index
                ])
                self.time_last_move[
                    self.state.turn ^ self.player_index ^ 1
                ] = time.time()
            # show text
            self._whose_move(self.state.turn ^ self.player_index)
        #
        if request_to_server:
            call_back = self.close if self.state.over else self.update_state
            # request to the server
            threading.Thread(
                target=self.connection.make_move,
                args=(move, call_back, True)
            ).start()

    def resign(self, player_id=1):
        self.state.over = True
        self.track = False
        # show text
        self._who_resigned(player_id)
        # request to the server
        threading.Thread(
            target=self.connection.resign,
            args=(self.close,)
        ).start()

    def close(self, *args, **kwargs) -> None:
        self.connection.close()

    # private methods
    def _compute_current_remaining_time(self) -> list[float]:
        time_remaining_current = copy.copy(self.time_remaining)
        time_remaining_current[
            self.state.turn ^ self.player_index
        ] = (self.time_remaining[self.state.turn ^ self.player_index] - 
            (time.time() - self.time_last_move[
            self.state.turn ^ self.player_index ^ 1
        ]))
        return time_remaining_current

    def _game_over_process(self) -> None:
        self.track = False
        # show text
        container = self._get_panel_container()
        message = container.get_element("text")
        if self.state.draw:
            message.text = "The game\nis a draw"
            message.style["color"] = message.style["message-color"]
        else:
            winner_player = self.state.turn ^ self.player_index ^ 1
            message.text = self.win_texts[winner_player]["text"]
            message.style["color"] = message.style[
                f"{self.win_texts[winner_player]['color']}-color"
            ]
        message.update_style()
        self._show_leave_button()

    def _show_board(self) -> None:
        self._whose_move(self.state.turn ^ self.player_index)
        self.document.current_page = "battle"

    def _update_time(self) -> None:
        self.time_last_move = [
            self.web_game_state[self.opponent_id]["time_last_move"],
            self.web_game_state[self.user_id]["time_last_move"]
        ]
        self.time_remaining = [
            self.web_game_state[self.opponent_id]["time_remaining"],
            self.web_game_state[self.user_id]["time_remaining"]
        ]


class BridgeConnector:
    def __init__(self, bridge: Bridge):
        self.bridge = bridge

    def update(self) -> None:
        self.bridge.update()

    def close(self, *args, **kwargs) -> None:
        self.bridge.close(*args, **kwargs)

    def resign(self) -> None:
        self.bridge.resign()

    def get_moves(self) -> Bridge.MovesHandler:
        return self.bridge.get_moves()
    
    def make_move(self, move: tuple[int, int]) -> None:
        self.bridge.make_move(move)

    def is_move_in_field(self, move: tuple[int, int]) -> bool:
        return self.bridge.is_move_in_field(move)
    
    def is_move_done(self, move: tuple[int, int]) -> bool:
        return self.bridge.is_move_done(move)
    
    @property
    def track(self) -> bool:
        return self.bridge.track
    
    @property
    def track_color(self) -> int:
        return self.bridge.track_color
    
    def get_last_move(self) -> tuple[int, int]:
        return self.bridge.last_move
    
    @property
    def player_index(self) -> int:
        return self.bridge.player_index
