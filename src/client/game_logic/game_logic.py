import copy
import json
from types import SimpleNamespace


class State:
    """
    Main class that implements game logic
    """

    # ----------------------- public methods
    def __init__(
            self, amount: int, field_size: tuple[int, int] = (0, 0),
            moves:
            tuple[set[tuple[int, int]],
                  set[tuple[int, int]]] = (set(),
                                           set())) -> None:
        """
        amount [int]:                           amount chips in a row to win
        field_size [tuple[int, int]]:           field size, 0 represents \
            unlimited field by this axis
        moves [tuple[set[tuple], set[tuple]]]:  moves for each player
        """

        if 0 < amount:
            self.amount = amount
        else:
            raise ValueError("Amount must be a positive value!")

        if self.check_field_size(field_size):
            self.field_size = field_size
            self.w, self.h = self.field_size
        else:
            raise ValueError("Field size is not valid!")

        self.turn = 0
        self.moves = (set(), set())
        self.over, self.points = False, set()
        self.draw = False

        self.add_many(moves)

    # checking input data
    @staticmethod
    def check_field_size(field_size: tuple[int, int]) -> bool:
        return (0 <= field_size[0] and
                0 <= field_size[1])

    def check_state(self, move: tuple[int, int]) -> None:
        """
        Checks if somebody has won (or if it's a draw)
        """

        for vector in ((1, 0), (0, 1), (1, 1), (-1, 1)):
            result = self._check_state_by_vector(move, vector)
            if result["status"]:
                self.over = True
                # save winning points
                self.points = result["points"]
                return
        # draw check
        if min(
                self.w, self.h) != 0 and len(
                self.moves[0]) + len(
                self.moves[1]) == self.w * self.h:
            self.over, self.draw = True, True

    def add(self, move: tuple[int, int]) -> None:
        if self._is_move_done(move):
            raise ValueError("Move had already been done!")
        if not self._is_move_in_field(move):
            raise ValueError("Move is out of field!")
        if self.over:
            raise NotImplementedError("Game is over!")
        self.moves[self.turn].add(move)
        self.check_state(move)
        self.turn ^= 1

    def add_many(self, moves: tuple
                 [set[tuple[int, int]],
                  set[tuple[int, int]]]) -> None:
        if (len(moves[0]) - len(moves[1]) != self.turn or
            len(moves[0] & moves[1]) != 0 or
            any(map(lambda move: (
                self._is_move_done(move) or
                                  not self._is_move_in_field(move)),
                                  moves[0] | moves[1])
                )
            ):
            raise ValueError("Moves are not valid")
        # add one by one
        moves_iter = (iter(moves[0]), iter(moves[1]))
        for i in range(sum(map(len, moves))):
            self.add(next(moves_iter[self.turn]))

    def to_dict(self, json_format=False) -> dict:
        return {
            "amount": self.amount,
            "field_size": self.field_size,
            "moves": self.moves if not json_format else (
                list(self.moves[0]),
                list(self.moves[1])
            )
        }

    def save(self, path: str) -> None:
        with open(path, 'w') as fp:
            json.dump(self.to_dict(json_format=True), fp)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.amount}, \
            {self.field_size}, {self.moves})"

    # ----------------------- private methods
    def _is_move_done(self, move: tuple[int, int]) -> bool:
        return (move in self.moves[0] or
                move in self.moves[1])

    def _is_move_in_field(self, move: tuple[int, int]) -> bool:
        return ((self.w == 0 or 1 <= move[0] <= self.w) and
                (self.h == 0 or 1 <= move[1] <= self.h))

    def _get_move_owner(self, move: tuple[int, int]) -> int:
        if not self._is_move_in_field(move):
            return -2
        if not self._is_move_done(move):
            return -1
        return 0 if move in self.moves[0] else 1

    def _check_state_by_vector(
            self, move: tuple[int, int],
            vector: tuple[int, int]) -> dict:
        owner = self._get_move_owner(move)
        i = (1 - self.amount)
        for j in range(i, self.amount):
            point = (move[0] - vector[0] * j,
                     move[1] - vector[1] * j)
            if (not self._is_move_in_field(point) or
                    not self._get_move_owner(point) == owner):
                i = j + 1
                continue
            if (j - i + 1) == self.amount:
                return {
                    "status": True,
                    "points": {
                        (move[0] - vector[0] * u,
                         move[1] - vector[1] * u) for u in range(i, j + 1)
                    }
                }
        return {
            "status": False,
            "points": set()
        }
