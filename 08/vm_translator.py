from pathlib import Path

import click

from code_writer import CodeWriter
from command_type import CommandType
from parser import Parser


@click.command()
@click.argument("filename", type=click.Path(exists=True, path_type=Path))
def translate(filename: Path):
    """
    Translate VM commands to Hack assembly

    Creates a new file with the extension .asm
    """
    code_writer = CodeWriter()
    code_writer.write_init()

    if filename.is_file():
        _process_file_path(code_writer=code_writer, filename=filename)

        asm_commands = code_writer.get_output()
        click.echo(asm_commands)

        output_file = filename.with_suffix(".asm")
        output_file.write_text("\n".join(asm_commands))

    elif filename.is_dir():
        for f in filename.iterdir():
            if f.suffix == ".vm":
                print(f"Translating {f}")
                _process_file_path(code_writer=code_writer, filename=f)
            else:
                print(f"Skipping {f}")

        asm_commands = code_writer.get_output()
        click.echo(asm_commands)

        output_file = filename / f"{filename.stem}.asm"
        output_file.write_text("\n".join(asm_commands))
    else:
        raise NotImplementedError(f"Unsupported path type {filename}")


def _process_file_path(code_writer, filename):
    code_writer.set_file_name(filename.stem)

    vm_commands = filename.read_text().splitlines()
    click.echo(vm_commands)
    parser_ = Parser(commands=vm_commands)

    while parser_.has_more_commands():
        parser_.advance()
        command_type = parser_.command_type()
        match command_type:
            case CommandType.C_ARITHMETIC:
                code_writer.write_arithmetic(parser_.arg1())
            case CommandType.C_PUSH:
                code_writer.write_push_pop(
                    command=CommandType.C_PUSH,
                    segment=parser_.arg1(),
                    index=parser_.arg2(),
                )
            case CommandType.C_POP:
                code_writer.write_push_pop(
                    command=CommandType.C_POP,
                    segment=parser_.arg1(),
                    index=parser_.arg2(),
                )
            case CommandType.C_LABEL:
                code_writer.write_label(parser_.arg1())
            case CommandType.C_IF:
                code_writer.write_if(parser_.arg1())
            case CommandType.C_GOTO:
                code_writer.write_goto(parser_.arg1())
            case CommandType.C_FUNCTION:
                code_writer.write_function(parser_.arg1(), parser_.arg2())
            case CommandType.C_RETURN:
                code_writer.write_return()
            case CommandType.C_CALL:
                code_writer.write_call(parser_.arg1(), parser_.arg2())
            case _:
                raise NotImplementedError(f"Unsupported command type {command_type}")


if __name__ == "__main__":
    translate()
