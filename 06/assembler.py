from pathlib import Path
from typing import List

import click

from code_ import Code
from parser import Parser, CommandType


def assemble(input_lines: List[str]):
    parser = Parser(input_lines=input_lines)
    code = Code()
    result = []

    done = False
    while not done:
        match parser.command_type():
            case CommandType.A_COMMAND:
                symbol_ = parser.symbol()
                # Assuming we are working with decimal number
                address = int(symbol_)
                result.append(f"{address:0>16b}")
            case CommandType.C_COMMAND:
                comp = code.comp(parser.comp())
                dest = code.dest(parser.dest())
                jump = code.jump(parser.jump())
                result.append(f"111{comp}{dest}{jump}")
            case CommandType.L_COMMAND:
                pass
            case _:
                raise Exception(f"unknown command type: {parser.command_type()}")

        if parser.has_more_commands():
            parser.advance()
        else:
            done = True

    return result


@click.command()
@click.argument("asm_file", type=click.Path(exists=True))
def hello(asm_file):
    """Hack assembler"""
    asm_file_path = Path(asm_file)
    asm_lines = asm_file_path.read_text().splitlines()

    binary_lines = assemble(input_lines=asm_lines)
    binary_text = "\n".join(binary_lines)
    click.echo(binary_text)

    output_file = asm_file_path.with_suffix(".hack")
    output_file.write_text(binary_text)


if __name__ == "__main__":
    hello()
