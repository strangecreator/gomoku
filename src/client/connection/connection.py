import time
import requests
import urllib.parse
from dataclasses import dataclass
import sys
from pathlib import Path

# base path resolving
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from config_loader import *


class Connection:
    @dataclass
    class DefaultResponse:
        status_code: int = 0

        def json(self) -> dict:
            return {"status": False}

    def __init__(self, user_id: str):
        self.closed = False
        self.user_id = user_id
        self.game_id = None

    def make_connection(self, call_back, *args, **kwargs) -> None:
        # initial request
        response = Connection.DefaultResponse()
        while not self.closed and (
                response.status_code != 200 or not response.json()["status"]):
            try:
                response = requests.get(
                    self._get_url(
                        config.connection.urls.make_connection,
                        {
                            "user_id": self.user_id
                        }
                    )
                )
            except:
                time.sleep(config.connection.delay)
        if self.closed:
            return
        # getting game_id
        return self.get_connection(call_back, *args, **kwargs)

    def get_connection(self, call_back, *args, **kwargs) -> None:
        response = Connection.DefaultResponse()
        # getting game_id
        while not self.closed and (response.status_code != 200 or
                                   not response.json()["status"] or
                                   response.json()["data"]["game_id"] is None):
            try:
                response = requests.get(
                    self._get_url(
                        config.connection.urls.get_connection,
                        {
                            "user_id": self.user_id
                        }
                    )
                )
                if (response.status_code == 200 and
                    response.json()["status"] and
                        response.json()["reconnection_required"]):
                    return self.make_connection(call_back)
            except:
                time.sleep(config.connection.delay)
        if self.closed:
            return
        self.game_id = response.json()["data"]["game_id"]
        self.get_state(call_back, *args, **kwargs)

    def make_move(
            self, move: tuple[int, int],
            call_back, *args, **kwargs) -> None:
        response = Connection.DefaultResponse()
        while not self.closed and (
                response.status_code != 200 or not response.json()["status"]):
            try:
                response = requests.post(
                    self._get_url(
                        config.connection.urls.make_move,
                        {
                            "user_id": self.user_id,
                            "game_id": self.game_id
                        }
                    ),
                    json={
                        "move": [move[0], move[1]]
                    }
                )
            except:
                time.sleep(config.connection.delay)
        if self.closed:
            return
        call_back(response.json()["data"], *args, **kwargs)

    def get_state(self, call_back, *args, **kwargs) -> None:
        response = Connection.DefaultResponse()
        while not self.closed and (
                response.status_code != 200 or not response.json()["status"]):
            try:
                response = requests.get(
                    self._get_url(
                        config.connection.urls.get_state,
                        {
                            "user_id": self.user_id,
                            "game_id": self.game_id
                        }
                    )
                )
            except:
                time.sleep(config.connection.delay)
        if self.closed:
            return
        call_back(response.json()["data"], *args, **kwargs)

    def get_state_monotonous(self, call_back, *args, **kwargs) -> None:
        while not self.closed:
            self.get_state(call_back, *args, **kwargs)
            time.sleep(config.connection.delay)

    def resign(self, call_back, *args, **kwargs) -> None:
        response = Connection.DefaultResponse()
        while not self.closed and (
                response.status_code != 200 or not response.json()["status"]):
            try:
                response = requests.post(
                    self._get_url(
                        config.connection.urls.resign,
                        {
                            "user_id": self.user_id,
                            "game_id": self.game_id
                        }
                    )
                )
            except:
                time.sleep(config.connection.delay)
        if self.closed:
            return
        call_back(*args, **kwargs)

    def close(self) -> None:
        self.closed = True

    # private methods
    def _get_url(self, url: str, query: dict) -> str:
        protocol = config.connection.protocol
        server = config.connection.server
        query_encoded = urllib.parse.urlencode(query)
        return f"{protocol}://{server}{url}?{query_encoded}"
