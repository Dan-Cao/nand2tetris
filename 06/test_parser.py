from pathlib import Path

from parser import CommandType, Parser

FIXTURES_PATH = Path(__file__).parent / "fixtures"


def test_parser_removes_whitespace_and_comments():
    input_file = FIXTURES_PATH / "Add.asm"
    input_text = input_file.read_text()
    input_lines = input_text.splitlines()

    parser = Parser(input_lines)
    expected_commands = ["@2", "D=A", "@3", "D=D+A", "@0", "M=D"]

    assert parser.commands == expected_commands


def test_has_more_commands():
    assert Parser(["@1234", "D=A"]).has_more_commands() is True


def test_has_more_commands_false():
    assert Parser(["@1234"]).has_more_commands() is False


def test_advance():
    parser = Parser(["@1234", "D=A"])
    assert parser.has_more_commands() is True
    assert parser.command_type() == CommandType.A_COMMAND

    parser.advance()
    assert parser.has_more_commands() is False
    assert parser.command_type() == CommandType.C_COMMAND


def test_command_type_with_a_command():
    assert Parser(["@1234"]).command_type() == CommandType.A_COMMAND


def test_command_type_with_c_command():
    assert Parser(["D=D+A"]).command_type() == CommandType.C_COMMAND


def test_command_type_with_l_command():
    assert Parser(["(FOO)"]).command_type() == CommandType.L_COMMAND


def test_symbol_with_a_command():
    assert Parser(["@123"]).symbol() == "123"


def test_symbol_with_label():
    assert Parser(["(FOO)"]).symbol() == "FOO"


def test_dest():
    assert Parser(["D=D+1;JMP"]).dest() == "D"


def test_dest_none():
    assert Parser(["D+1;JMP"]).dest() is None


def test_comp():
    assert Parser(["D=D+1;JMP"]).comp() == "D+1"


def test_jump():
    assert Parser(["D=D+1;JMP"]).jump() == "JMP"


def test_jump_none():
    assert Parser(["D=D+1"]).jump() is None
