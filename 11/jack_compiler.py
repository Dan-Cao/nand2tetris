from pathlib import Path
import xml.etree.ElementTree as ET

import click

from compilation_engine import CompilationEngine
from jack_tokenizer import JackTokenizer


@click.command()
@click.argument("filename", type=click.Path(exists=True, path_type=Path))
def compile_(filename: Path):
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
    output_xml_file = filename.with_name(f"{name}_").with_suffix(".xml")

    tokenizer = JackTokenizer(filename.read_text())
    compilation_engine = CompilationEngine(tokenizer=tokenizer)

    tree = compilation_engine.compile_class()
    ET.indent(tree)
    tree_str = ET.tostring(tree, encoding="unicode", short_empty_elements=True)
    output_xml_file.write_text(tree_str)

    output_asm_file = filename.with_suffix(".asm")
    output_asm_file.write_text("\n".join(compilation_engine.get_vm_commands()))


if __name__ == "__main__":
    compile_()
