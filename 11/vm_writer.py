from enum import Enum


class Segment(Enum):
    CONST = "constant"
    ARG = "argument"
    LOCAL = "local"
    STATIC = "static"
    THIS = "this"
    THAT = "that"
    POINTER = "pointer"
    TEMP = "temp"


class ArithmeticCommand(Enum):
    ADD = "add"
    SUB = "sub"
    NEG = "neg"
    EQ = "eq"
    GT = "gt"
    LT = "lt"
    AND = "and"
    OR = "or"
    NOT = "not"


class VMWriter:
    def __init__(self):
        self._vm_commands = []

    def write_push(self, segment: Segment, index: int):
        self._vm_commands.append(f"push {segment.value} {index}")

    def write_pop(self, segment: Segment, index: int):
        self._vm_commands.append(f"pop {segment.value} {index}")

    def write_arithmetic(self, command: ArithmeticCommand):
        self._vm_commands.append(command.value)

    def write_label(self, label: str):
        self._vm_commands.append(f"label {label}")

    def write_goto(self, label: str):
        self._vm_commands.append(f"goto {label}")

    def write_if(self, label: str):
        self._vm_commands.append(f"if-goto {label}")

    def write_call(self, name: str, n_args: int):
        self._vm_commands.append(f"call {name} {n_args}")

    def write_function(self, name: str, n_locals: int):
        self._vm_commands.append(f"function {name} {n_locals}")

    def write_return(self):
        self._vm_commands.append("return")

    def get_vm_commands(self):
        return self._vm_commands
