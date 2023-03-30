from pathlib import Path
from typing import List

import click

from code_ import Code
from parser import Parser, CommandType
from symbol_table import SymbolTable


def assemble(input_lines: List[str]):
    code = Code()
    symbol_table = SymbolTable()

    # First pass
    instruction_count = 0
    parser = Parser(input_lines=input_lines)
    while True:
        match parser.command_type():
            case CommandType.A_COMMAND:
                instruction_count += 1
            case CommandType.C_COMMAND:
                instruction_count += 1
            case CommandType.L_COMMAND:
                label = parser.symbol()
                symbol_table.add_entry(label, instruction_count)
            case _:
                raise Exception(f"unknown command type: {parser.command_type()}")
        if parser.has_more_commands():
            parser.advance()
        else:
            break

    # Second pass
    result = []
    next_variable_address = 16
    parser = Parser(input_lines=input_lines)
    while True:
        match parser.command_type():
            case CommandType.A_COMMAND:
                symbol_ = parser.symbol()

                if symbol_.isdigit():
                    address = int(symbol_)
                elif symbol_table.contains(symbol_):
                    address = symbol_table.get_address(symbol_)
                else:
                    address = next_variable_address
                    next_variable_address += 1
                    symbol_table.add_entry(symbol_, address)
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
            break

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
