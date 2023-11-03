from pathlib import Path

import click

from compilation_engine import CompilationEngine
from jack_tokenizer import JackTokenizer, TokenType


@click.command()
@click.argument("filename", type=click.Path(exists=True, path_type=Path))
def analyze(filename: Path):
    """
    Translate Jack source into VM commands
    """

    if filename.is_file():
        _process_file(filename)

    elif filename.is_dir():
        for f in filename.iterdir():
            if f.suffix == ".jack":
                print(f"Processing {f}")
                _process_file(f)
            else:
                print(f"Skipping {f}")

    else:
        raise NotImplementedError(f"Unsupported path type {filename}")


def _process_file(filename):
    name = filename.stem
    output_file = filename.with_name(f"{name}_").with_suffix(".xml")

    tokenizer = JackTokenizer(filename.read_text())

    output = ""
    output += "<tokens>\n"

    while tokenizer.has_more_tokens():
        tokenizer.advance()

        # TODO: escape special XML characters and retest

        match tokenizer.token_type():
            case TokenType.KEYWORD:
                output += f"<keyword> {tokenizer.key_word().value} </keyword>\n"
            case TokenType.SYMBOL:
                output += f"<symbol> {tokenizer.symbol()} </symbol>\n"
            case TokenType.IDENTIFIER:
                output += f"<identifier> {tokenizer.identifier()} </identifier>\n"
            case TokenType.INT_CONST:
                output += (
                    f"<integerConstant> {tokenizer.int_val()} </integerConstant>\n"
                )
            case TokenType.STRING_CONST:
                output += (
                    f"<stringConstant> {tokenizer.string_val()} </stringConstant>\n"
                )
            case _:
                raise NotImplementedError("Unknown token type")

    output += "</tokens>\n"

    print(output)
    output_file.write_text(output)


if __name__ == "__main__":
    analyze()
