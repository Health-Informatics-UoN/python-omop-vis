from enum import Enum


class RType(Enum):
    CHARACTER = ("character", str)
    INT = ("int", int)

    py_type: type

    def __new__(cls, value: str, py_type: type):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.py_type = py_type

        return obj
