import xml.etree.ElementTree as ET

from jack_tokenizer import JackTokenizer, TokenType, Keyword
from symbol_table import SymbolTable


class CompilationEngine:
    def __init__(self, tokenizer: JackTokenizer):
        self._tokenizer = tokenizer
        self._symbol_table = SymbolTable()

    def _eat(self, *tokens):
        # checks current token matches expected
        match self._tokenizer.token_type():
            case TokenType.KEYWORD:
                self._assert(
                    self._tokenizer.key_word() in tokens,
                    f"Expected one of {tokens}",
                )
                e = ET.Element("keyword")
                e.text = self._tokenizer.key_word().value
                self._tokenizer.advance()
                return e
            case TokenType.SYMBOL:
                self._assert(
                    self._tokenizer.symbol() in tokens,
                    f"Expected one of {' '.join(tokens)}",
                )
                e = ET.Element("symbol")
                e.text = self._tokenizer.symbol()
                self._tokenizer.advance()
                return e
            case _:
                self._raise_syntax_error(f"Expected one of {' '.join(tokens)}")

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

        e.append(self._eat("}"))
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

        kind = self._eat(Keyword.STATIC, Keyword.FIELD)
        e.append(kind)

        type_ = self._compile_type()
        e.append(type_)

        self._assert(
            self._tokenizer.token_type() == TokenType.IDENTIFIER,
            "Identifier must follow type",
        )
        identifier = ET.SubElement(e, "identifier")
        identifier.text = self._tokenizer.identifier()

        self._symbol_table.define(name=identifier.text, type_=type_.text, kind=kind.text)
        identifier.attrib.update(
            {"category": kind.text, "index": str(self._symbol_table.index_of(identifier.text)), "usage": "declared"}
        )
        self._tokenizer.advance()

        while self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == ",":
            symbol = ET.SubElement(e, "symbol")
            symbol.text = ","
            self._tokenizer.advance()

            self._assert(
                self._tokenizer.token_type() == TokenType.IDENTIFIER,
                f"Identifier must follow ','",
            )
            identifier = ET.SubElement(e, "identifier")
            identifier.text = self._tokenizer.identifier()
            self._symbol_table.define(name=identifier.text, type_=type_.text, kind=kind.text)
            identifier.attrib.update(
                {"category": kind.text, "index": str(self._symbol_table.index_of(identifier.text)), "usage": "declared"}
            )
            self._tokenizer.advance()

        e.append(self._eat(";"))
        return e

    def compile_subroutine(self):
        self._symbol_table.start_subroutine()

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
            e.text = "\n"  # hacky workaround for output to pass TextCompare check
            return e

        e.append(self._compile_identifier("variable identifier expected"))

        while self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == ",":
            e.append(self._eat(","))
            e.append(self._compile_type())
            e.append(self._compile_identifier("parameter name expected"))

        return e

    def compile_subroutine_body(self):
        e = ET.Element("subroutineBody")

        e.append(self._eat("{"))

        while self._tokenizer.token_type() == TokenType.KEYWORD and self._tokenizer.key_word() == Keyword.VAR:
            e.append(self.compile_var_dec())

        e.append(self.compile_statements())
        e.append(self._eat("}"))
        return e

    def compile_var_dec(self):
        e = ET.Element("varDec")

        e.append(self._eat(Keyword.VAR))
        e.append(self._compile_type())

        e.append(self._compile_identifier("variable identifier expected"))

        while self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == ",":
            e.append(self._eat(","))
            e.append(self._compile_identifier("variable identifier expected"))

        e.append(self._eat(";"))

        return e

    def _compile_identifier(self, help_text):
        self._assert(self._tokenizer.token_type() == TokenType.IDENTIFIER, help_text)
        identifier = ET.Element("identifier")
        identifier.text = f" {self._tokenizer.identifier()} "
        self._tokenizer.advance()
        return identifier

    def compile_statements(self):
        e = ET.Element("statements")

        if self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == "}":
            e.text = "\n"  # hacky workaround for output to pass TextCompare check
            return e

        while not (self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == "}"):
            self._assert(self._tokenizer.token_type() == TokenType.KEYWORD, "Start of statement expected")

            match self._tokenizer.key_word():
                case Keyword.LET:
                    e.append(self.compile_let())
                case Keyword.IF:
                    e.append(self.compile_if())
                case Keyword.WHILE:
                    e.append(self.compile_while())
                case Keyword.DO:
                    e.append(self.compile_do())
                case Keyword.RETURN:
                    e.append(self.compile_return())
                case _:
                    self._raise_syntax_error(f"Unexpected {self._tokenizer.key_word()} at start of statement")
        return e

    def compile_do(self):
        e = ET.Element("doStatement")
        e.append(self._eat(Keyword.DO))
        e.append(self._compile_identifier("class or subroutine identifier expected"))

        if self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == ".":
            e.append(self._eat("."))
            e.append(self._compile_identifier("class method identifier expected"))

        e.append(self._eat("("))
        e.append(self.compile_expression_list())
        e.append(self._eat(")"))

        e.append(self._eat(";"))
        return e

    def compile_let(self):
        e = ET.Element("letStatement")
        e.append(self._eat(Keyword.LET))
        e.append(self._compile_identifier("variable name expected"))

        if self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == "[":
            e.append(self._eat("["))
            e.append(self.compile_expression())
            e.append(self._eat("]"))

        e.append(self._eat("="))
        e.append(self.compile_expression())
        e.append(self._eat(";"))
        return e

    def compile_while(self):
        e = ET.Element("whileStatement")
        e.append(self._eat(Keyword.WHILE))
        e.append(self._eat("("))
        e.append(self.compile_expression())
        e.append(self._eat(")"))
        e.append(self._eat("{"))
        e.append(self.compile_statements())
        e.append(self._eat("}"))
        return e

    def compile_return(self):
        e = ET.Element("returnStatement")
        e.append(self._eat(Keyword.RETURN))

        if not (self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == ";"):
            e.append(self.compile_expression())
        e.append(self._eat(";"))

        return e

    def compile_if(self):
        e = ET.Element("ifStatement")
        e.append(self._eat(Keyword.IF))
        e.append(self._eat("("))
        e.append(self.compile_expression())
        e.append(self._eat(")"))
        e.append(self._eat("{"))
        e.append(self.compile_statements())
        e.append(self._eat("}"))

        if self._tokenizer.token_type() == TokenType.KEYWORD and self._tokenizer.key_word() == Keyword.ELSE:
            e.append(self._eat(Keyword.ELSE))
            e.append(self._eat("{"))
            e.append(self.compile_statements())
            e.append(self._eat("}"))
        return e

    def compile_expression(self):
        e = ET.Element("expression")
        e.append(self.compile_term())

        if self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() in "+-*/&|<>=":
            op = ET.SubElement(e, "symbol")
            op.text = f" {self._tokenizer.symbol()} "
            self._tokenizer.advance()

            e.append(self.compile_term())

        return e

    def compile_term(self):
        e = ET.Element("term")

        match self._tokenizer.token_type():
            case TokenType.INT_CONST:
                int_const = ET.SubElement(e, "integerConstant")
                int_const.text = f" {self._tokenizer.int_val()} "
                self._tokenizer.advance()
            case TokenType.STRING_CONST:
                str_const = ET.SubElement(e, "stringConstant")
                str_const.text = f" {self._tokenizer.string_val()} "
                self._tokenizer.advance()
            case TokenType.KEYWORD if self._tokenizer.key_word() in [
                Keyword.TRUE,
                Keyword.FALSE,
                Keyword.NULL,
                Keyword.THIS,
            ]:
                e.append(self._eat(Keyword.TRUE, Keyword.FALSE, Keyword.NULL, Keyword.THIS))
            case TokenType.SYMBOL if self._tokenizer.symbol() in "-~":
                e.append(self._eat("-", "~"))
                e.append(self.compile_term())
            case TokenType.SYMBOL if self._tokenizer.symbol() == "(":
                e.append(self._eat("("))
                e.append(self.compile_expression())
                e.append(self._eat(")"))
            case TokenType.IDENTIFIER:
                e.append(self._compile_identifier("identifier expected"))

                # array
                if self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == "[":
                    e.append(self._eat("["))
                    e.append(self.compile_expression())
                    e.append(self._eat("]"))
                # function call
                elif self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == "(":
                    e.append(self._eat("("))
                    e.append(self.compile_expression_list())
                    e.append(self._eat(")"))
                # method call
                elif self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == ".":
                    e.append(self._eat("."))
                    e.append(self._compile_identifier("function name expected"))
                    e.append(self._eat("("))
                    e.append(self.compile_expression_list())
                    e.append(self._eat(")"))

            case _:
                raise self._raise_syntax_error("Do not know how to handle this term yet")

        return e

    def compile_expression_list(self):
        e = ET.Element("expressionList")
        if self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == ")":
            e.text = "\n"  # hacky workaround for output to pass TextCompare check
            return e

        e.append(self.compile_expression())
        while self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == ",":
            e.append(self._eat(","))
            e.append(self.compile_expression())
        return e


class JackSyntaxError(Exception):
    pass
