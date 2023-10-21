from command_type import CommandType


class Parser:
    def __init__(self, commands):
        self.commands = commands
        self.position = -1
        self.current_command = []

    def has_more_commands(self):
        for c in self.commands[self.position + 1 :]:
            if c and not c.startswith("//"):
                return True
        return False

    def advance(self):
        while self.position + 1 < len(self.commands):
            self.position += 1

            command = self.commands[self.position]

            if command and not command.startswith("//"):
                self.current_command = command.split(" ")
                return

    def command_type(self):
        match self.current_command[0]:
            case "add" | "sub" | "neg" | "eq" | "gt" | "lt" | "and" | "or" | "not":
                return CommandType.C_ARITHMETIC
            case "push":
                return CommandType.C_PUSH
            case "pop":
                return CommandType.C_POP
            case "label":
                return CommandType.C_LABEL
            case "goto":
                return CommandType.C_GOTO
            case "if-goto":
                return CommandType.C_IF
            case "function":
                return CommandType.C_FUNCTION
            case "call":
                return CommandType.C_CALL
            case "return":
                return CommandType.C_RETURN
            case _:
                raise NotImplementedError(
                    f"Unsupported command type {self.current_command[0]}"
                )

    def arg1(self):
        if self.command_type() == CommandType.C_ARITHMETIC:
            return self.current_command[0]
        else:
            return self.current_command[1]

    def arg2(self):
        return self.current_command[2]
