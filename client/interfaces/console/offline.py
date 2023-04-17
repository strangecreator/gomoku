import os, sys, platform
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from game_logic.main import State


class ConsoleOfflineInterface:
    """
    Class that implements offline game console interface
    """

    string_point = {
        "classic": '•',
        "winning": '⦿'
    }

    # ----------------------- public methods
    def __init__(self) -> None:
        self.state = State(5, (0, 0)) # classic gomoku
        self.borders = None
        self.offset = 0

    def initialize(self) -> None:
        # configuration
        self.state = State(
            int(input("Amount chips in a row to win: ")),
            tuple(map(int, input("Field size, 0 represents unlimited field by this axis: ").split()))
        )

    def play(self) -> None:
        if self.state.over:
            raise NotImplementedError("Game is over!")
        self.print_field()
        while not self.state.over:
            move = tuple(map(int, input(f"Player {self.state.turn + 1} to move: ").split()))
            self.offset += 1
            try:
                self.state.add(move)
                self.print_field()
            except Exception as e:
                print(e)
                self.offset += 1
        if self.state.draw:
            print("The game is a draw! Congratulations!")
        else:
            print(f"Player {(self.state.turn ^ 1) + 1} has won! Congratulations!")

    def print_field(self) -> None:
        self._clear_screen()
        self.borders = self._get_borders()
        for j in range(self.borders[1][1], self.borders[1][0] - 1, -1):
            row_string = ""
            for i in range(self.borders[0][0], self.borders[0][1] + 1):
                owner = self.state._get_move_owner((i, j))
                string_point = self.string_point["classic"]
                if self.state.over and (i, j) in self.state.points:
                    string_point = self.string_point["winning"]
                if owner == 0:
                    string_point = f"\033[32m{string_point}\033[0m"
                elif owner == 1:
                    string_point = f"\033[31m{string_point}\033[0m"
                row_string += string_point
            print(row_string)

    # ----------------------- private methods
    def _get_borders(self) -> tuple[tuple[int, int], tuple[int, int]]:
        horizontal = [1, self.state.w]
        if self.state.w == 0:
            horizontal = [
                min(self.state.moves[0] | self.state.moves[1] | {(0, 0)})[0],
                max(self.state.moves[0] | self.state.moves[1] | {(0, 0)})[0]
            ]
        vertical = [1, self.state.h]
        if self.state.h == 0:
            vertical = [
                min(self.state.moves[0] | self.state.moves[1] | {(0, 0)}, key=lambda move: move[1])[1],
                max(self.state.moves[0] | self.state.moves[1] | {(0, 0)}, key=lambda move: move[1])[1]
            ]
        return (tuple(horizontal), tuple(vertical))
    
    def _clear_screen(self):
        if self.borders is None:
            return
        print(f"\033[{self.borders[1][1] - self.borders[1][0] + 1 + self.offset}F\033[0J", end='')
        self.offset = 0
        


if __name__ == "__main__":
    interface = ConsoleOfflineInterface()
    interface.initialize()
    interface.play()

    if platform.system() == "Windows":
        os.system("pause")
    else:
        input("Press ENTER to continue...")
