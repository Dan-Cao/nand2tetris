from enum import Enum


class Kind(Enum):
    STATIC = "static"
    FIELD = "field"
    ARG = "arg"
    VAR = "var"


class SymbolTable:
    def __init__(self):
        self._class_symbols = {"static": {}, "field": {}}
        self._subroutine_symbols = {"arg": {}, "var": {}}

    def start_subroutine(self):
        self._subroutine_symbols = {"arg": {}, "var": {}}

    def define(self, name: str, type_: str, kind: str):
        if self.kind_of(name):
            raise Exception(f"Symbol {name} is already defined")

        kind = Kind(kind)
        index = self.var_count(kind)

        match kind:
            case Kind.STATIC:
                self._class_symbols["static"][name] = {"type": type_, "index": index}
            case Kind.FIELD:
                self._class_symbols["field"][name] = {"type": type_, "index": index}
            case Kind.ARG:
                self._subroutine_symbols["arg"][name] = {"type": type_, "index": index}
            case Kind.VAR:
                self._subroutine_symbols["var"][name] = {"type": type_, "index": index}
            case _:
                raise NotImplementedError(f"Unknown symbol type: {kind}")

    def var_count(self, kind: Kind):
        kind = Kind(kind)

        match kind:
            case Kind.STATIC:
                return len(self._class_symbols["static"])
            case Kind.FIELD:
                return len(self._class_symbols["field"])
            case Kind.ARG:
                return len(self._subroutine_symbols["arg"])
            case Kind.VAR:
                return len(self._subroutine_symbols["var"])
            case _:
                raise NotImplementedError(f"Unknown symbol type: {kind}")

    def kind_of(self, name: str):
        if self._subroutine_symbols["var"].get(name):
            return "var"
        elif self._subroutine_symbols["arg"].get(name):
            return "arg"
        elif self._class_symbols["field"].get(name):
            return "field"
        elif self._class_symbols["static"].get(name):
            return "static"

    def type_of(self, name: str):
        if s := self._subroutine_symbols["var"].get(name):
            return s["type"]
        elif s := self._subroutine_symbols["arg"].get(name):
            return s["type"]
        elif s := self._class_symbols["field"].get(name):
            return s["type"]
        elif s := self._class_symbols["static"].get(name):
            return s["type"]

    def index_of(self, name):
        if s := self._subroutine_symbols["var"].get(name):
            return s["index"]
        elif s := self._subroutine_symbols["arg"].get(name):
            return s["index"]
        elif s := self._class_symbols["field"].get(name):
            return s["index"]
        elif s := self._class_symbols["static"].get(name):
            return s["index"]
