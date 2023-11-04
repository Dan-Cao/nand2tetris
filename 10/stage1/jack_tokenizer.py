import re
from enum import Enum

KEYWORD_RE_RAW = (
    "(class)|(constructor)|(function)|(method)|(field)|(static)|(var)|(int)|(char)|(boolean)|(void)|"
    "(true)|(false)|(null)|(this)|(let)|(do)|(if)|(else)|(while)|(return)"
)
KEYWORD_RE = re.compile(KEYWORD_RE_RAW)

SYMBOL_RE_RAW = r"([{}\(\)\[\]\.,;\+\-\*\/&\|<>=~])"
SYMBOL_RE = re.compile(SYMBOL_RE_RAW)

INTEGER_CONSTANT_RE_RAW = r"(\d{1,5})"
INTEGER_CONSTANT_RE = re.compile(INTEGER_CONSTANT_RE_RAW)

STRING_CONSTANT_RE_RAW = r'(".*")'
STRING_CONSTANT = re.compile(STRING_CONSTANT_RE_RAW)

IDENTIFIER_RE_RAW = r"([A-Za-z_]\w*)"
IDENTIFIER_RE = re.compile(IDENTIFIER_RE_RAW)

WHITESPACE_RE_RAW = r"(\s+)"
COMMENT_RE_RAW = r"(\/\/.*)|(\/\*(?:.|\n)*?\*\/)"
WHITESPACE_OR_COMMENT_RE_RAW = f"{WHITESPACE_RE_RAW}|{COMMENT_RE_RAW}"
WHITESPACE_OR_COMMENT_RE = re.compile(WHITESPACE_OR_COMMENT_RE_RAW)


class TokenType(Enum):
    KEYWORD = "keyword"
    SYMBOL = "symbol"
    IDENTIFIER = "identifier"
    INT_CONST = "integerConstant"
    STRING_CONST = "stringConstant"


class Keyword(Enum):
    CLASS = "class"
    METHOD = "method"
    FUNCTION = "function"
    CONSTRUCTOR = "constructor"
    INT = "int"
    BOOLEAN = "boolean"
    CHAR = "char"
    VOID = "void"
    VAR = "var"
    STATIC = "static"
    FIELD = "field"
    LET = "let"
    DO = "do"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    RETURN = "return"
    TRUE = "true"
    FALSE = "false"
    NULL = "null"
    THIS = "this"


class JackTokenizer:
    def __init__(self, input_text: str):
        self.input_text = input_text
        self._current_token = None
        self._current_type = None
        self._remaining_text = input_text

    def has_more_tokens(self):
        self._skip_whitespace_and_comments()
        return len(self._remaining_text) > 0

    def advance(self):
        self._skip_whitespace_and_comments()

        if match := KEYWORD_RE.match(self._remaining_text):
            self._current_token = match.group()
            self._current_type = TokenType.KEYWORD
            self._remaining_text = self._remaining_text.replace(self._current_token, "", 1)
        elif match := SYMBOL_RE.match(self._remaining_text):
            self._current_token = match.group()
            self._current_type = TokenType.SYMBOL
            self._remaining_text = self._remaining_text.replace(self._current_token, "", 1)
        elif match := INTEGER_CONSTANT_RE.match(self._remaining_text):
            self._current_token = match.group()
            self._current_type = TokenType.INT_CONST
            self._remaining_text = self._remaining_text.replace(self._current_token, "", 1)
        elif match := STRING_CONSTANT.match(self._remaining_text):
            self._current_token = match.group()
            self._current_type = TokenType.STRING_CONST
            self._remaining_text = self._remaining_text.replace(self._current_token, "", 1)
        elif match := IDENTIFIER_RE.match(self._remaining_text):
            self._current_token = match.group()
            self._current_type = TokenType.IDENTIFIER
            self._remaining_text = self._remaining_text.replace(self._current_token, "", 1)
        else:
            raise NotImplementedError(f"Unknown token: {self._remaining_text}")

    def _skip_whitespace_and_comments(self):
        while match := WHITESPACE_OR_COMMENT_RE.match(self._remaining_text):
            self._remaining_text = self._remaining_text.replace(match.group(), "", 1)

    def token_type(self):
        return self._current_type

    def key_word(self):
        return Keyword(self._current_token)

    def symbol(self):
        return self._current_token

    def identifier(self):
        return self._current_token

    def int_val(self):
        return int(self._current_token)

    def string_val(self):
        return self._current_token[1:-1]
