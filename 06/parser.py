from enum import Enum
from typing import List


class CommandType(Enum):
    A_COMMAND = 1
    C_COMMAND = 2
    L_COMMAND = 3


class Parser:
    def __init__(self, input_lines):
        self.commands = self.remove_whitespace_and_comments(input_lines)
        self.position = 0

    def remove_whitespace_and_comments(self, input_lines: List[str]):
        def sanitise_line(line):
            line_without_comments = line.split("//")[0]
            line_without_whitespace = line_without_comments.replace(" ", "")
            return line_without_whitespace

        def is_line_non_blank(line):
            return bool(line)

        return list(filter(is_line_non_blank, map(sanitise_line, input_lines)))

    def has_more_commands(self):
        return self.position + 1 < len(self.commands)

    def advance(self):
        self.position += 1

    @property
    def current_command(self) -> str:
        return self.commands[self.position]

    def command_type(self):
        match self.current_command[0]:
            case "@":
                return CommandType.A_COMMAND
            case "(":
                return CommandType.L_COMMAND
            case _:
                return CommandType.C_COMMAND

    def symbol(self):
        if self.current_command.startswith("@"):
            return self.current_command[1:]
        else:
            return self.current_command.removeprefix("(").removesuffix(")")

    def dest(self):
        if "=" in self.current_command:
            return self.current_command.split("=")[0]
        else:
            return None

    def comp(self):
        command_without_dest = self.current_command.split("=")[-1]
        command_without_dest_or_jump = command_without_dest.split(";")[0]
        return command_without_dest_or_jump

    def jump(self):
        if ";" in self.current_command:
            return self.current_command.split(";")[-1]
        else:
            return None
