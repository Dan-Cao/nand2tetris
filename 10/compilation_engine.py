import xml.etree.ElementTree as ET
from enum import Enum

from jack_tokenizer import JackTokenizer, TokenType, Keyword


class CompilationEngine:
    def __init__(self, tokenizer: JackTokenizer):
        self._tokenizer = tokenizer

    def _eat(self, *tokens):
        # checks current token matches expected
        match self._tokenizer.token_type():
            case TokenType.KEYWORD:
                self._assert(
                    self._tokenizer.key_word() in tokens,
                    f"Expected one of {tokens}, got {self._tokenizer.current_token()}",
                )
                e = ET.Element("keyword")
                e.text = f" {self._tokenizer.key_word().value} "
                self._tokenizer.advance()
                return e
            case TokenType.SYMBOL:
                self._assert(
                    self._tokenizer.symbol() in tokens,
                    f"Expected one of {tokens}, got {self._tokenizer.current_token()}",
                )
                e = ET.Element("symbol")
                e.text = f" {self._tokenizer.symbol()} "
                self._tokenizer.advance()
                return e
            case _:
                raise JackSyntaxError(f"Expected one of {tokens}. Got {self._tokenizer.current_token()}")

    def _assert(self, test, message):
        if not test:
            raise JackSyntaxError(message)

    def compile_class(self):
        e = ET.Element("class")
        self._tokenizer.advance()
        e.append(self._eat(Keyword.CLASS))

        self._assert(
            self._tokenizer.token_type() == TokenType.IDENTIFIER,
            f"class must be followed by identifier. Got {self._tokenizer.current_token()}",
        )
        identifier = ET.SubElement(e, "identifier")
        identifier.text = f" {self._tokenizer.identifier()} "
        self._tokenizer.advance()

        e.append(self._eat("{"))
        while self._tokenizer.token_type() == TokenType.KEYWORD and self._tokenizer.key_word() in [
            Keyword.STATIC,
            Keyword.FIELD,
        ]:
            e.append(self.compile_class_var_dec())

        # TODO: implement subroutine dec
        # e.append(self._eat("}"))

        return e

    def compile_class_var_dec(self):
        e = ET.Element("classVarDec")
        e.append(self._eat(Keyword.STATIC, Keyword.FIELD))

        if self._tokenizer.token_type() == TokenType.KEYWORD:
            self._assert(
                self._tokenizer.key_word() in [Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN],
                f"Type must be int, char or boolean. Got {self._tokenizer.current_token()}",
            )

            keyword = ET.SubElement(e, "keyword")
            keyword.text = f" {self._tokenizer.key_word().value} "
            self._tokenizer.advance()
        elif self._tokenizer.token_type() == TokenType.IDENTIFIER:
            identifier = ET.SubElement(e, "identifier")
            identifier.text = f" {self._tokenizer.identifier()} "
            self._tokenizer.advance()
        else:
            raise JackSyntaxError(f"Type expected in class var declaration. Got {self._tokenizer.current_token()}")

        self._assert(
            self._tokenizer.token_type() == TokenType.IDENTIFIER,
            f"Identifier must follow type. Got {self._tokenizer.current_token()}",
        )
        identifier = ET.SubElement(e, "identifier")
        identifier.text = f" {self._tokenizer.identifier()} "
        self._tokenizer.advance()

        while self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == ",":
            symbol = ET.SubElement(e, "symbol")
            symbol.text = f" {self._tokenizer.symbol()} "
            self._tokenizer.advance()

            self._assert(
                self._tokenizer.token_type() == TokenType.IDENTIFIER,
                f"Identifier must follow ',', got {self._tokenizer.token_type()}",
            )
            identifier = ET.SubElement(e, "identifier")
            identifier.text = f" {self._tokenizer.identifier()} "
            self._tokenizer.advance()

        e.append(self._eat(";"))
        return e

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


class JackSyntaxError(Exception):
    pass
