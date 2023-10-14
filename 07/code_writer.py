from command_type import CommandType


class CodeWriter:
    def __init__(self):
        self.output = []
        self.file_name = ""
        self.label_counter = 0

    def get_output(self):
        return self.output

    def set_file_name(self, file_name):
        self.file_name = file_name
        self.label_counter = 0

    def new_label(self):
        label = f"DAN{self.label_counter}DAN"
        self.label_counter += 1
        return label

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
                        "M=D+M",
                        # Decrement stack pointer,
                        "@SP",
                        "M=M-1",
                    ]
                )
            case "sub":
                self.output.extend(
                    [
                        # Get value from top of stack, load into D
                        "@SP",
                        "A=M-1",
                        "D=M",
                        # Sub D from value below in stack
                        "A=A-1",
                        "M=M-D",
                        # Decrement stack pointer,
                        "@SP",
                        "M=M-1",
                    ]
                )
            case "neg":
                self.output.extend(
                    [
                        # Get value from top of stack
                        "@SP",
                        "A=M-1",
                        # Apply arithmetic negation
                        "M=-M",
                    ]
                )
            case "eq":
                done_label = self.new_label()
                self.output.extend(
                    [
                        # Get value from top of stack, load into D
                        "@SP",
                        "A=M-1",
                        "D=M",
                        # Do x - y, store result in D
                        "A=A-1",
                        "D=M-D",
                        # Set initial result to true (-1)
                        "M=-1",
                        # Decrement stack pointer,
                        "@SP",
                        "M=M-1",
                        # We are done if x - y == 0
                        f"@{done_label}",
                        "D;JEQ",
                        # Otherwise result is false (0)
                        "@SP",
                        "A=M-1",
                        "M=0",
                        f"({done_label})",
                    ]
                )
            case "gt":
                done_label = self.new_label()
                self.output.extend(
                    [
                        # Get value from top of stack, load into D
                        "@SP",
                        "A=M-1",
                        "D=M",
                        # Do x - y, store result in D
                        "A=A-1",
                        "D=M-D",
                        # Set initial result to true (-1)
                        "M=-1",
                        # Decrement stack pointer,
                        "@SP",
                        "M=M-1",
                        # We are done if x - y > 0
                        f"@{done_label}",
                        "D;JGT",
                        # Otherwise result is false (0)
                        "@SP",
                        "A=M-1",
                        "M=0",
                        f"({done_label})",
                    ]
                )
            case "lt":
                done_label = self.new_label()
                self.output.extend(
                    [
                        # Get value from top of stack, load into D
                        "@SP",
                        "A=M-1",
                        "D=M",
                        # Do x - y, store result in D
                        "A=A-1",
                        "D=M-D",
                        # Set initial result to true (-1)
                        "M=-1",
                        # Decrement stack pointer,
                        "@SP",
                        "M=M-1",
                        # We are done if x - y < 0
                        f"@{done_label}",
                        "D;JLT",
                        # Otherwise result is false (0)
                        "@SP",
                        "A=M-1",
                        "M=0",
                        f"({done_label})",
                    ]
                )
            case "and":
                self.output.extend(
                    [
                        # Get value from top of stack, load into D
                        "@SP",
                        "A=M-1",
                        "D=M",
                        # Bitwise AND with D and value below in stack
                        "A=A-1",
                        "M=D&M",
                        # Decrement stack pointer,
                        "@SP",
                        "M=M-1",
                    ]
                )
            case "or":
                self.output.extend(
                    [
                        # Get value from top of stack, load into D
                        "@SP",
                        "A=M-1",
                        "D=M",
                        # Bitwise OR with D and value below in stack
                        "A=A-1",
                        "M=D|M",
                        # Decrement stack pointer,
                        "@SP",
                        "M=M-1",
                    ]
                )
            case "not":
                self.output.extend(
                    [
                        # Get value from top of stack
                        "@SP",
                        "A=M-1",
                        # Apply bitwise not
                        "M=!M",
                    ]
                )
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
