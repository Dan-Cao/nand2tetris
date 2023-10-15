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

    def get_static_symbol(self, index):
        return f"@{self.file_name}.{index}"

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
                elif segment == "local":
                    self.output.extend(
                        [
                            # Get address of local segment, store in d register
                            "@LCL",
                            "D=M",
                            # Index into d
                            f"@{index}",
                            "A=D+A",
                            # Read value at index
                            "D=M",
                            # Dereference stack pointer and store value into stack
                            "@SP",
                            "A=M",
                            "M=D",
                            # Increment stack pointer
                            "@SP",
                            "M=M+1",
                        ]
                    )
                elif segment == "argument":
                    self.output.extend(
                        [
                            # Get address of argument segment, store in d register
                            "@ARG",
                            "D=M",
                            # Index into d
                            f"@{index}",
                            "A=D+A",
                            # Read value at index
                            "D=M",
                            # Dereference stack pointer and store value into stack
                            "@SP",
                            "A=M",
                            "M=D",
                            # Increment stack pointer
                            "@SP",
                            "M=M+1",
                        ]
                    )
                elif segment == "this":
                    self.output.extend(
                        [
                            # Get address of this segment, store in d register
                            "@THIS",
                            "D=M",
                            # Index into d
                            f"@{index}",
                            "A=D+A",
                            # Read value at index
                            "D=M",
                            # Dereference stack pointer and store value into stack
                            "@SP",
                            "A=M",
                            "M=D",
                            # Increment stack pointer
                            "@SP",
                            "M=M+1",
                        ]
                    )
                elif segment == "that":
                    self.output.extend(
                        [
                            # Get address of this segment, store in d register
                            "@THAT",
                            "D=M",
                            # Index into d
                            f"@{index}",
                            "A=D+A",
                            # Read value at index
                            "D=M",
                            # Dereference stack pointer and store value into stack
                            "@SP",
                            "A=M",
                            "M=D",
                            # Increment stack pointer
                            "@SP",
                            "M=M+1",
                        ]
                    )
                elif segment == "temp":
                    self.output.extend(
                        [
                            # Set d register to base of temp segment
                            "@5",
                            "D=A",
                            # Index into d
                            f"@{index}",
                            "A=D+A",
                            # Read value at index
                            "D=M",
                            # Dereference stack pointer and store value into stack
                            "@SP",
                            "A=M",
                            "M=D",
                            # Increment stack pointer
                            "@SP",
                            "M=M+1",
                        ]
                    )
                elif segment == "pointer":
                    self.output.extend(
                        [
                            # Set d register to base of pointer segment
                            "@3",
                            "D=A",
                            # Index into d
                            f"@{index}",
                            "A=D+A",
                            # Read value at index
                            "D=M",
                            # Dereference stack pointer and store value into stack
                            "@SP",
                            "A=M",
                            "M=D",
                            # Increment stack pointer
                            "@SP",
                            "M=M+1",
                        ]
                    )
                elif segment == "static":
                    self.output.extend(
                        [
                            self.get_static_symbol(index=index),
                            # Read value at index
                            "D=M",
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
                    raise NotImplementedError(f"Unsupported push segment {segment}")

            case CommandType.C_POP:
                self.output.append(f"// pop {segment} {index}")
                if segment == "constant":
                    raise Exception("Cannot pop into constant segment")
                elif segment == "local":
                    self.output.extend(
                        [
                            # Get address of local segment, store in d register
                            "@LCL",
                            "D=M",
                            # Index into d
                            f"@{index}",
                            "D=D+A",
                            # Store address of index in segment in R13
                            "@R13",
                            "M=D",
                            # Decrement stack pointer
                            "@SP",
                            "M=M-1",
                            # Get value from top of stack and store in d,
                            "A=M",
                            "D=M",
                            # Reference address of index in segment
                            "@R13",
                            "A=M",
                            # Store result
                            "M=D",
                        ]
                    )
                elif segment == "argument":
                    self.output.extend(
                        [
                            # Get address of argument segment, store in d register
                            "@ARG",
                            "D=M",
                            # Index into d
                            f"@{index}",
                            "D=D+A",
                            # Store address of index in segment in R13
                            "@R13",
                            "M=D",
                            # Decrement stack pointer
                            "@SP",
                            "M=M-1",
                            # Get value from top of stack and store in d,
                            "A=M",
                            "D=M",
                            # Reference address of index in segment
                            "@R13",
                            "A=M",
                            # Store result
                            "M=D",
                        ]
                    )
                elif segment == "this":
                    self.output.extend(
                        [
                            # Get address of this segment, store in d register
                            "@THIS",
                            "D=M",
                            # Index into d
                            f"@{index}",
                            "D=D+A",
                            # Store address of index in segment in R13
                            "@R13",
                            "M=D",
                            # Decrement stack pointer
                            "@SP",
                            "M=M-1",
                            # Get value from top of stack and store in d,
                            "A=M",
                            "D=M",
                            # Reference address of index in segment
                            "@R13",
                            "A=M",
                            # Store result
                            "M=D",
                        ]
                    )
                elif segment == "that":
                    self.output.extend(
                        [
                            # Get address of that segment, store in d register
                            "@THAT",
                            "D=M",
                            # Index into d
                            f"@{index}",
                            "D=D+A",
                            # Store address of index in segment in R13
                            "@R13",
                            "M=D",
                            # Decrement stack pointer
                            "@SP",
                            "M=M-1",
                            # Get value from top of stack and store in d,
                            "A=M",
                            "D=M",
                            # Reference address of index in segment
                            "@R13",
                            "A=M",
                            # Store result
                            "M=D",
                        ]
                    )
                elif segment == "temp":
                    self.output.extend(
                        [
                            # Get address of temp segment, store in d register
                            "@R5",
                            "D=A",
                            # Index into d
                            f"@{index}",
                            "D=D+A",
                            # Store address of index in segment in R13
                            "@R13",
                            "M=D",
                            # Decrement stack pointer
                            "@SP",
                            "M=M-1",
                            # Get value from top of stack and store in d,
                            "A=M",
                            "D=M",
                            # Reference address of index in segment
                            "@R13",
                            "A=M",
                            # Store result
                            "M=D",
                        ]
                    )
                elif segment == "pointer":
                    self.output.extend(
                        [
                            # Get address of pointer segment, store in d register
                            "@R3",
                            "D=A",
                            # Index into d
                            f"@{index}",
                            "D=D+A",
                            # Store address of index in segment in R13
                            "@R13",
                            "M=D",
                            # Decrement stack pointer
                            "@SP",
                            "M=M-1",
                            # Get value from top of stack and store in d,
                            "A=M",
                            "D=M",
                            # Reference address of index in segment
                            "@R13",
                            "A=M",
                            # Store result
                            "M=D",
                        ]
                    )
                elif segment == "static":
                    self.output.extend(
                        [
                            # Decrement stack pointer
                            "@SP",
                            "M=M-1",
                            # Get value from top of stack and store in d,
                            "A=M",
                            "D=M",
                            # Reference address of index in segment
                            self.get_static_symbol(index=index),
                            # Store result
                            "M=D",
                        ]
                    )
                else:
                    raise NotImplementedError(f"Unsupported segment {segment}")
            case _:
                raise NotImplementedError(f"Unknown push/pop command {command}")
