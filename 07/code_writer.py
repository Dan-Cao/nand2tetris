from command_type import CommandType


class CodeWriter:
    def __init__(self):
        self.output = []
        self.file_name = ""

    def get_output(self):
        return self.output

    def set_file_name(self, file_name):
        self.file_name = file_name

    def write_arithmetic(self, command):
        self.output.append(f"// {command}")
        match command:
            case "add":
                self.output.extend(
                    [
                        # Get value from top of stack, load into D
                        "@SP",
                        "A=M-1",
                        "D=M",
                        # Add D to value below in stack
                        "A=A-1",
                        "M=M+D",
                        # Decrement stack pointer,
                        "@SP",
                        "M=M-1",
                    ]
                )
            case "sub":
                pass
            case "neg":
                pass
            case "eq":
                pass
            case "gt":
                pass
            case "lt":
                pass
            case "and":
                pass
            case "or":
                pass
            case "not":
                pass
            case _:
                raise NotImplementedError(f"Unsupported arithmetic command {command}")

    def write_push_pop(self, command, segment, index):
        match command:
            case CommandType.C_PUSH:
                self.output.append(f"// push {segment} {index}")

                if segment == "constant":
                    self.output.extend(
                        [
                            # Load constant into D register
                            f"@{index}",
                            "D=A",
                            # Dereference stack pointer and store value into stack
                            "@SP",
                            "A=M",
                            "M=D",
                            # Increment stack pointer
                            "@SP",
                            "M=M+1",
                        ]
                    )
                else:
                    raise NotImplementedError(f"Unsupported segment {segment}")

            case CommandType.C_POP:
                self.output.append(f"// pop {segment} {index}")
            case _:
                raise NotImplementedError(f"Unknown push/pop command {command}")
