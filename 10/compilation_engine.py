import xml.etree.ElementTree as ET
from enum import Enum

from jack_tokenizer import JackTokenizer, TokenType, Keyword


class CompilationEngine:
    def __init__(self, tokenizer: JackTokenizer):
        self._tokenizer = tokenizer

    def _eat(self, token):
        # checks current token matches expected
        match self._tokenizer.token_type():
            case TokenType.KEYWORD:
                assert (
                    self._tokenizer.key_word() == token
                ), f"Expected {token}, got {self._tokenizer.key_word()}"
                self._tokenizer.advance()
                e = ET.Element("keyword")
                e.text = f" {token.value} "
                return e
            case TokenType.SYMBOL:
                assert (
                    self._tokenizer.symbol() == token
                ), f"Expected {token}, got{self._tokenizer.symbol()}"
                self._tokenizer.advance()
                e = ET.Element("symbol")
                e.text = f" {token} "
                return e
            case _:
                raise NotImplementedError(
                    f"Cannot eat token type {self._tokenizer.token_type()}"
                )

    def compile_class(self):
        e = ET.Element("class")
        self._tokenizer.advance()
        e.append(self._eat(Keyword.CLASS))

        assert (
            self._tokenizer.token_type() == TokenType.IDENTIFIER
        ), "class must be followed by identifier"
        identifier = ET.SubElement(e, "identifier")
        identifier.text = f" {self._tokenizer.identifier()} "
        self._tokenizer.advance()

        e.append(self._eat("{"))

        # e.append(self._eat("}"))

        return e

    def compile_class_var_dec(self):
        pass

    def compile_subroutine(self):
        pass

    def compile_parameter_list(self):
        pass

    def compile_var_dec(self):
        pass

    def compile_statements(self):
        pass

    def compile_do(self):
        pass

    def compile_let(self):
        pass

    def compile_while(self):
        pass

    def compile_return(self):
        pass

    def compile_if(self):
        pass

    def compile_expression(self):
        pass

    def compile_term(self):
        pass

    def compile_expression_list(self):
        pass
