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
                self._raise_syntax_error(f"Expected one of {tokens}")

    def _assert(self, test, message):
        # Does assertion on a token
        if not test:
            self._raise_syntax_error(message)

    def _raise_syntax_error(self, message):
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

        while self._tokenizer.token_type() == TokenType.KEYWORD and self._tokenizer.key_word() in [
            Keyword.CONSTRUCTOR,
            Keyword.FUNCTION,
            Keyword.METHOD,
        ]:
            e.append(self.compile_subroutine())

        # TODO: remove
        # e.append(self._eat("}"))

        return e

    def _compile_type(self):
        if self._tokenizer.token_type() == TokenType.KEYWORD:
            self._assert(
                self._tokenizer.key_word() in [Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN],
                "Type must be int, char or boolean",
            )
            keyword = ET.Element("keyword")
            keyword.text = f" {self._tokenizer.key_word().value} "
            self._tokenizer.advance()
            return keyword
        elif self._tokenizer.token_type() == TokenType.IDENTIFIER:
            identifier = ET.Element("identifier")
            identifier.text = f" {self._tokenizer.identifier()} "
            self._tokenizer.advance()
            return identifier
        else:
            self._raise_syntax_error("Type expected")

    def compile_class_var_dec(self):
        e = ET.Element("classVarDec")
        e.append(self._eat(Keyword.STATIC, Keyword.FIELD))

        e.append(self._compile_type())

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
        e = ET.Element("subroutineDec")
        e.append(self._eat(Keyword.CONSTRUCTOR, Keyword.FUNCTION, Keyword.METHOD))

        if self._tokenizer.token_type() == TokenType.KEYWORD:
            self._assert(
                self._tokenizer.key_word() in [Keyword.VOID, Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN],
                "Subroutine must have return type",
            )
            keyword = ET.SubElement(e, "keyword")
            keyword.text = f" {self._tokenizer.key_word().value} "
            self._tokenizer.advance()

        elif self._tokenizer.token_type() == TokenType.IDENTIFIER:
            identifier = ET.SubElement(e, "identifier")
            identifier.text = f" {self._tokenizer.identifier()} "
            self._tokenizer.advance()
        else:
            self._raise_syntax_error("Subroutine must have return type")

        self._assert(
            self._tokenizer.token_type() == TokenType.IDENTIFIER,
            "Subroutine name expected",
        )
        identifier = ET.SubElement(e, "identifier")
        identifier.text = f" {self._tokenizer.identifier()} "
        self._tokenizer.advance()

        e.append(self._eat("("))
        e.append(self.compile_parameter_list())
        e.append(self._eat(")"))

        e.append(self.compile_subroutine_body())
        return e

    def compile_parameter_list(self):
        e = ET.Element("parameterList")

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
            return e

        while self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == ",":
            e.append(self._eat(","))
            e.append(self._compile_type())

        return e

    def compile_subroutine_body(self):
        e = ET.Element("subroutineBody")

        e.append(self._eat("{"))
        # TODO

        return e

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
