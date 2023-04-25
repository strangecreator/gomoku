from types import SimpleNamespace
from dataclasses import dataclass


def to_dict(obj: SimpleNamespace) -> dict:
    result = {}
    for name, value in vars(obj).items():
        result[name] = value if not isinstance(value, SimpleNamespace) \
            else to_dict(value)
    return result


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

    def __sub__(self, vector):
        return Vector2D(self.x - vector.x, self.y - vector.y)

    def __mul__(self, vector):
        return Vector2D(self.x * vector.x, self.y * vector.y)

    def __floordiv__(self, obj):
        if isinstance(obj, int):
            return Vector2D(self.x // obj, self.y // obj)
        elif isinstance(obj, Vector2D):
            return Vector2D(self.x // obj.x, self.y // obj.y)
        else:
            raise NotImplementedError


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
