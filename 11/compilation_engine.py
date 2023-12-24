import xml.etree.ElementTree as ET

from jack_tokenizer import JackTokenizer, TokenType, Keyword
from symbol_table import SymbolTable, Kind
from vm_writer import VMWriter, Segment, ArithmeticCommand


class CompilationEngine:
    def __init__(self, tokenizer: JackTokenizer):
        self._tokenizer = tokenizer
        self._symbol_table = SymbolTable()
        self._vm_writer = VMWriter()
        self._if_counter = 0
        self._while_counter = 0
        self._class_var_count = 0

    def get_vm_commands(self):
        return self._vm_writer.get_vm_commands()

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
        identifier.text = self._tokenizer.identifier()
        identifier.attrib.update({"category": "class", "usage": "declared"})
        class_name = identifier.text
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
            e.append(self.compile_subroutine(class_name=class_name))

        e.append(self._eat("}"))
        return e

    def _compile_type(self):
        if self._tokenizer.token_type() == TokenType.KEYWORD:
            self._assert(
                self._tokenizer.key_word() in [Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN],
                "Type must be int, char or boolean",
            )
            keyword = ET.Element("keyword")
            keyword.text = self._tokenizer.key_word().value
            self._tokenizer.advance()
            return keyword
        elif self._tokenizer.token_type() == TokenType.IDENTIFIER:
            identifier = ET.Element("identifier")
            identifier.text = self._tokenizer.identifier()
            identifier.attrib.update({"category": "class", "usage": "used"})
            self._tokenizer.advance()
            return identifier
        else:
            self._raise_syntax_error("Type expected")

    def compile_class_var_dec(self):
        e = ET.Element("classVarDec")

        kind = self._eat(Keyword.STATIC, Keyword.FIELD)
        is_field = kind.text == Keyword.FIELD.value
        e.append(kind)

        type_ = self._compile_type()
        e.append(type_)

        self._assert(
            self._tokenizer.token_type() == TokenType.IDENTIFIER,
            "Identifier must follow type",
        )
        identifier = ET.SubElement(e, "identifier")
        identifier.text = self._tokenizer.identifier()

        self._symbol_table.define(name=identifier.text, type_=type_.text, kind=Kind(kind.text))
        identifier.attrib.update(
            {"category": kind.text, "index": str(self._symbol_table.index_of(identifier.text)), "usage": "declared"}
        )
        if is_field:
            self._class_var_count += 1
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
            self._symbol_table.define(name=identifier.text, type_=type_.text, kind=Kind(kind.text))
            identifier.attrib.update(
                {"category": kind.text, "index": str(self._symbol_table.index_of(identifier.text)), "usage": "declared"}
            )
            if is_field:
                self._class_var_count += 1
            self._tokenizer.advance()

        e.append(self._eat(";"))
        return e

    def compile_subroutine(self, class_name):
        self._symbol_table.start_subroutine()
        self._if_counter = 0
        self._while_counter = 0

        e = ET.Element("subroutineDec")
        subroutine_type = self._eat(Keyword.CONSTRUCTOR, Keyword.FUNCTION, Keyword.METHOD)
        e.append(subroutine_type)

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
            identifier.attrib.update({"category": "class", "usage": "used"})
            self._tokenizer.advance()
        else:
            self._raise_syntax_error("Subroutine must have return type")

        self._assert(
            self._tokenizer.token_type() == TokenType.IDENTIFIER,
            "Subroutine name expected",
        )
        identifier = ET.SubElement(e, "identifier")
        identifier.text = self._tokenizer.identifier()
        identifier.attrib.update({"category": "subroutine", "usage": "declared"})
        subroutine_name = identifier.text
        self._tokenizer.advance()

        e.append(self._eat("("))
        e.append(self.compile_parameter_list())
        e.append(self._eat(")"))

        e.append(
            self.compile_subroutine_body(
                class_name=class_name, subroutine_name=subroutine_name, subroutine_type=subroutine_type
            )
        )
        return e

    def compile_parameter_list(self):
        e = ET.Element("parameterList")

        if self._tokenizer.token_type() == TokenType.KEYWORD:
            self._assert(
                self._tokenizer.key_word() in [Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN],
                "Type must be int, char or boolean",
            )
            keyword = ET.SubElement(e, "keyword")
            keyword.text = self._tokenizer.key_word().value
            self._tokenizer.advance()

            parameter_type = keyword.text

        elif self._tokenizer.token_type() == TokenType.IDENTIFIER:
            identifier = ET.SubElement(e, "identifier")
            identifier.text = self._tokenizer.identifier()
            identifier.attrib.update({"category": "class", "usage": "used"})
            self._tokenizer.advance()

            parameter_type = identifier.text

        else:
            return e

        identifier = self._compile_identifier("variable identifier expected")
        e.append(identifier)
        self._symbol_table.define(name=identifier.text, type_=parameter_type, kind=Kind.ARG)
        identifier.attrib.update(
            {"category": "arg", "usage": "declared", "index": str(self._symbol_table.index_of(identifier.text))}
        )

        while self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == ",":
            e.append(self._eat(","))

            parameter_type = self._compile_type()
            e.append(parameter_type)

            identifier = self._compile_identifier("parameter name expected")
            e.append(identifier)

            self._symbol_table.define(name=identifier.text, type_=parameter_type.text, kind=Kind.ARG)
            identifier.attrib.update(
                {"category": "arg", "usage": "declared", "index": str(self._symbol_table.index_of(identifier.text))}
            )

        return e

    def compile_subroutine_body(self, class_name, subroutine_name, subroutine_type):
        e = ET.Element("subroutineBody")

        e.append(self._eat("{"))

        while self._tokenizer.token_type() == TokenType.KEYWORD and self._tokenizer.key_word() == Keyword.VAR:
            e.append(self.compile_var_dec())

        self._vm_writer.write_function(
            name=f"{class_name}.{subroutine_name}", n_locals=self._symbol_table.var_count(Kind.VAR)
        )

        if subroutine_type.text == Keyword.CONSTRUCTOR.value:
            self._vm_writer.write_push(segment=Segment.CONST, index=self._class_var_count)
            self._vm_writer.write_call(name="Memory.alloc", n_args=1)
            self._vm_writer.write_pop(segment=Segment.POINTER, index=0)
        elif subroutine_type.text == Keyword.METHOD.value:
            self._vm_writer.write_push(segment=Segment.ARG, index=0)
            self._vm_writer.write_pop(segment=Segment.POINTER, index=0)

        e.append(self.compile_statements(class_name=class_name))
        e.append(self._eat("}"))
        return e

    def compile_var_dec(self):
        e = ET.Element("varDec")

        e.append(self._eat(Keyword.VAR))
        var_type = self._compile_type()
        e.append(var_type)

        identifier = self._compile_identifier("variable identifier expected")
        e.append(identifier)

        self._symbol_table.define(name=identifier.text, type_=var_type.text, kind=Kind.VAR)
        identifier.attrib.update(
            {"category": "local", "usage": "declared", "index": str(self._symbol_table.index_of(identifier.text))}
        )

        while self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == ",":
            e.append(self._eat(","))
            identifier = self._compile_identifier("variable identifier expected")
            e.append(identifier)
            self._symbol_table.define(name=identifier.text, type_=var_type.text, kind=Kind.VAR)
            identifier.attrib.update(
                {"category": "local", "usage": "declared", "index": str(self._symbol_table.index_of(identifier.text))}
            )

        e.append(self._eat(";"))

        return e

    def _compile_identifier(self, help_text):
        self._assert(self._tokenizer.token_type() == TokenType.IDENTIFIER, help_text)
        identifier = ET.Element("identifier")
        identifier.text = self._tokenizer.identifier()
        self._tokenizer.advance()
        return identifier

    def compile_statements(self, class_name):
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
                    e.append(self.compile_if(class_name=class_name))
                case Keyword.WHILE:
                    e.append(self.compile_while(class_name=class_name))
                case Keyword.DO:
                    e.append(self.compile_do(class_name=class_name))
                case Keyword.RETURN:
                    e.append(self.compile_return())
                case _:
                    self._raise_syntax_error(f"Unexpected {self._tokenizer.key_word()} at start of statement")
        return e

    def compile_do(self, class_name):
        e = ET.Element("doStatement")
        e.append(self._eat(Keyword.DO))
        identifier1 = self._compile_identifier("class or subroutine identifier expected")
        e.append(identifier1)

        # Method
        n_args = 0
        if self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == ".":
            e.append(self._eat("."))
            identifier2 = self._compile_identifier("class method identifier expected")
            e.append(identifier2)

            identifier1.attrib.update({"category": "class", "usage": "used"})
            identifier2.attrib.update({"category": "subroutine", "usage": "used"})

            id1_is_object = self._symbol_table.type_of(identifier1.text)
            if id1_is_object:
                identifier1_type = self._symbol_table.type_of(identifier1.text)

                full_name = f"{identifier1_type}.{identifier2.text}"
                n_args += 1
                self._vm_writer.write_push(
                    segment=self._identifier_category_to_segment(
                        category=self._symbol_table.kind_of(name=identifier1.text)
                    ),
                    index=self._symbol_table.index_of(name=identifier1.text),
                )
            else:
                full_name = f"{identifier1.text}.{identifier2.text}"
        # Function call with this class
        else:
            identifier1.attrib.update({"category": "subroutine", "usage": "used"})
            full_name = f"{class_name}.{identifier1.text}"

        e.append(self._eat("("))
        expression_list = self.compile_expression_list()
        n_args += int(expression_list.attrib["count"])
        e.append(expression_list)
        e.append(self._eat(")"))

        e.append(self._eat(";"))

        self._vm_writer.write_call(name=full_name, n_args=n_args)
        self._vm_writer.write_pop(segment=Segment.TEMP, index=0)
        return e

    def compile_let(self):
        e = ET.Element("letStatement")
        e.append(self._eat(Keyword.LET))
        identifier = self._compile_identifier("variable name expected")
        e.append(identifier)
        identifier.attrib.update(
            {
                "category": self._symbol_table.kind_of(identifier.text),
                "index": str(self._symbol_table.index_of(identifier.text)),
                "usage": "used",
            }
        )

        if self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == "[":
            e.append(self._eat("["))
            e.append(self.compile_expression())
            e.append(self._eat("]"))

        e.append(self._eat("="))
        e.append(self.compile_expression())
        e.append(self._eat(";"))

        self._vm_writer.write_pop(
            segment=self._identifier_category_to_segment(identifier.attrib["category"]),
            index=int(identifier.attrib["index"]),
        )
        return e

    def _identifier_category_to_segment(self, category):
        match category:
            case "var":
                return Segment.LOCAL
            case "arg":
                return Segment.ARG
            case "field":
                return Segment.THIS
            case "static":
                return Segment.STATIC
            case _:
                raise NotImplementedError(f"Don't know how to handle identifier of category {category}")

    def compile_while(self, class_name):
        while_counter = 0
        self._while_counter += 1
        e = ET.Element("whileStatement")
        e.append(self._eat(Keyword.WHILE))
        e.append(self._eat("("))
        self._vm_writer.write_label(f"WHILE_EXP{while_counter}")
        e.append(self.compile_expression())
        self._vm_writer.write_arithmetic(command=ArithmeticCommand.NOT)
        self._vm_writer.write_if(label=f"WHILE_END{while_counter}")
        e.append(self._eat(")"))
        e.append(self._eat("{"))
        e.append(self.compile_statements(class_name=class_name))
        e.append(self._eat("}"))
        self._vm_writer.write_goto(label=f"WHILE_EXP{while_counter}")
        self._vm_writer.write_label(label=f"WHILE_END{while_counter}")
        return e

    def compile_return(self):
        e = ET.Element("returnStatement")
        e.append(self._eat(Keyword.RETURN))

        if not (self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == ";"):
            e.append(self.compile_expression())
        else:
            self._vm_writer.write_push(segment=Segment.CONST, index=0)
        e.append(self._eat(";"))

        self._vm_writer.write_return()
        return e

    def compile_if(self, class_name):
        if_counter = self._if_counter
        self._if_counter += 1

        e = ET.Element("ifStatement")
        e.append(self._eat(Keyword.IF))
        e.append(self._eat("("))
        e.append(self.compile_expression())
        e.append(self._eat(")"))
        e.append(self._eat("{"))
        self._vm_writer.write_if(label=f"IF_TRUE{if_counter}")
        self._vm_writer.write_goto(label=f"IF_FALSE{if_counter}")
        self._vm_writer.write_label(label=f"IF_TRUE{if_counter}")
        e.append(self.compile_statements(class_name=class_name))
        e.append(self._eat("}"))
        self._vm_writer.write_goto(label=f"IF_END{if_counter}")

        if self._tokenizer.token_type() == TokenType.KEYWORD and self._tokenizer.key_word() == Keyword.ELSE:
            e.append(self._eat(Keyword.ELSE))
            e.append(self._eat("{"))
            self._vm_writer.write_label(label=f"IF_FALSE{if_counter}")
            e.append(self.compile_statements(class_name=class_name))
            e.append(self._eat("}"))

        self._vm_writer.write_label(label=f"IF_END{if_counter}")
        return e

    def compile_expression(self):
        e = ET.Element("expression")
        e.append(self.compile_term())

        if self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() in "+-*/&|<>=":
            op = ET.SubElement(e, "symbol")
            op.text = self._tokenizer.symbol()
            self._tokenizer.advance()
            symbol = op.text

            e.append(self.compile_term())

            match symbol:
                case "+":
                    self._vm_writer.write_arithmetic(command=ArithmeticCommand.ADD)
                case "-":
                    self._vm_writer.write_arithmetic(command=ArithmeticCommand.SUB)
                case "*":
                    self._vm_writer.write_call(name="Math.multiply", n_args=2)
                case "/":
                    self._vm_writer.write_call(name="Math.divide", n_args=2)
                case "&":
                    self._vm_writer.write_arithmetic(command=ArithmeticCommand.AND)
                case "|":
                    self._vm_writer.write_arithmetic(command=ArithmeticCommand.OR)
                case "<":
                    self._vm_writer.write_arithmetic(command=ArithmeticCommand.LT)
                case ">":
                    self._vm_writer.write_arithmetic(command=ArithmeticCommand.GT)
                case "=":
                    self._vm_writer.write_arithmetic(command=ArithmeticCommand.EQ)
                case _ as operator:
                    raise NotImplementedError(f"Unknown operator {operator}")

        return e

    def compile_term(self):
        e = ET.Element("term")

        match self._tokenizer.token_type():
            case TokenType.INT_CONST:
                int_const = ET.SubElement(e, "integerConstant")
                int_val = self._tokenizer.int_val()
                int_const.text = str(int_val)
                self._vm_writer.write_push(segment=Segment.CONST, index=int_val)
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
                match keyword := self._tokenizer.key_word():
                    case Keyword.TRUE:
                        self._vm_writer.write_push(segment=Segment.CONST, index=0)
                        self._vm_writer.write_arithmetic(command=ArithmeticCommand.NOT)
                    case Keyword.FALSE:
                        self._vm_writer.write_push(segment=Segment.CONST, index=0)
                    case Keyword.THIS:
                        self._vm_writer.write_push(segment=Segment.POINTER, index=0)
                    case _:
                        raise NotImplementedError(f"Don't know how to handle keyword {keyword}")

                e.append(self._eat(Keyword.TRUE, Keyword.FALSE, Keyword.NULL, Keyword.THIS))
            case TokenType.SYMBOL if self._tokenizer.symbol() in "-~":
                op = self._tokenizer.symbol()
                e.append(self._eat("-", "~"))
                e.append(self.compile_term())
                if op == "-":
                    self._vm_writer.write_arithmetic(command=ArithmeticCommand.NEG)
                elif op == "~":
                    self._vm_writer.write_arithmetic(command=ArithmeticCommand.NOT)
                else:
                    raise NotImplementedError(f"Unknown operator {op}")
            case TokenType.SYMBOL if self._tokenizer.symbol() == "(":
                e.append(self._eat("("))
                e.append(self.compile_expression())
                e.append(self._eat(")"))
            case TokenType.IDENTIFIER:
                identifier1 = self._compile_identifier("identifier expected")
                e.append(identifier1)

                # array
                if self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == "[":
                    e.append(self._eat("["))
                    e.append(self.compile_expression())
                    e.append(self._eat("]"))
                    identifier1.attrib.update(
                        {
                            "category": self._symbol_table.kind_of(identifier1.text),
                            "index": str(self._symbol_table.index_of(identifier1.text)),
                            "usage": "used",
                        }
                    )
                # function call
                elif self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == "(":
                    e.append(self._eat("("))
                    expression_list = self.compile_expression_list()
                    e.append(expression_list)
                    e.append(self._eat(")"))
                    identifier1.attrib.update({"category": "subroutine", "usage": "used"})

                    subroutine_name = identifier1.text
                    expression_count = int(expression_list.attrib["count"])
                    self._vm_writer.write_call(name=subroutine_name, n_args=expression_count)

                # method call
                elif self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == ".":
                    e.append(self._eat("."))
                    identifier2 = self._compile_identifier("function name expected")
                    e.append(identifier2)
                    e.append(self._eat("("))

                    n_args = 0
                    id1_is_object = self._symbol_table.type_of(name=identifier1.text)
                    if id1_is_object:
                        id1_class = self._symbol_table.type_of(name=identifier1.text)
                        self._vm_writer.write_push(
                            segment=self._identifier_category_to_segment(
                                category=self._symbol_table.kind_of(name=identifier1.text)
                            ),
                            index=self._symbol_table.index_of(name=identifier1.text),
                        )
                        n_args += 1
                        full_name = f"{id1_class}.{identifier2.text}"
                    else:
                        full_name = f"{identifier1.text}.{identifier2.text}"

                    expression_list = self.compile_expression_list()
                    e.append(expression_list)
                    e.append(self._eat(")"))

                    identifier1.attrib.update({"category": "class", "usage": "used"})
                    identifier2.attrib.update({"category": "subroutine", "usage": "used"})

                    n_args += int(expression_list.attrib["count"])
                    self._vm_writer.write_call(name=full_name, n_args=n_args)

                else:
                    identifier1.attrib.update(
                        {
                            "category": self._symbol_table.kind_of(identifier1.text),
                            "index": str(self._symbol_table.index_of(identifier1.text)),
                            "usage": "used",
                        }
                    )

                    self._vm_writer.write_push(
                        segment=self._identifier_category_to_segment(identifier1.attrib["category"]),
                        index=int(identifier1.attrib["index"]),
                    )

            case _:
                raise self._raise_syntax_error("Do not know how to handle this term yet")

        return e

    def compile_expression_list(self):
        e = ET.Element("expressionList")
        e.attrib.update({"count": "0"})
        if self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == ")":
            return e

        e.append(self.compile_expression())
        expression_count = 1
        while self._tokenizer.token_type() == TokenType.SYMBOL and self._tokenizer.symbol() == ",":
            e.append(self._eat(","))
            e.append(self.compile_expression())
            expression_count += 1
        e.attrib.update({"count": str(expression_count)})
        return e


class JackSyntaxError(Exception):
    pass
