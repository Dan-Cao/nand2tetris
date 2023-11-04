import xml.etree.ElementTree as ET

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
                    f"Expected one of {tokens}",
                )
                e = ET.Element("keyword")
                e.text = f" {self._tokenizer.key_word().value} "
                self._tokenizer.advance()
                return e
            case TokenType.SYMBOL:
                self._assert(
                    self._tokenizer.symbol() in tokens,
                    f"Expected one of {tokens}",
                )
                e = ET.Element("symbol")
                e.text = f" {self._tokenizer.symbol()} "
                self._tokenizer.advance()
                return e
            case _:
                raise JackSyntaxError(f"Expected one of {tokens}")

    def _assert(self, test, message):
        # Does assertion on a token
        if not test:
            raise JackSyntaxError(
                f"{message}\nGot '{self._tokenizer.current_token()}' at:\n{self._tokenizer.current_line()}"
            )

    def compile_class(self):
        e = ET.Element("class")
        self._tokenizer.advance()
        e.append(self._eat(Keyword.CLASS))

        self._assert(
            self._tokenizer.token_type() == TokenType.IDENTIFIER,
            "class must be followed by identifier",
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
                "Type must be int, char or boolean",
            )

            keyword = ET.SubElement(e, "keyword")
            keyword.text = f" {self._tokenizer.key_word().value} "
            self._tokenizer.advance()
        elif self._tokenizer.token_type() == TokenType.IDENTIFIER:
            identifier = ET.SubElement(e, "identifier")
            identifier.text = f" {self._tokenizer.identifier()} "
            self._tokenizer.advance()
        else:
            raise JackSyntaxError("Type expected in class var declaration")

        self._assert(
            self._tokenizer.token_type() == TokenType.IDENTIFIER,
            "Identifier must follow type",
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
                f"Identifier must follow ','",
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
