from typing import Iterable, Union, Optional

from lexit import Lexer, LexerError, Token


class JsonLexer(Lexer):
    NUMBER = r'-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?'
    STRING = r'"(\\\"|\\\\|[^"\n])*?"i?'
    L_BRACE = r'{'
    R_BRACE = r'}'
    L_BRACKET = r'\['
    R_BRACKET = r'\]'
    TRUE = r'true'
    FALSE = r'false'
    NULL = r'null'
    COMMA = r','
    COLON = r':'

    ignore = r'\s+'


class ParserError(Exception):
    pass


class ExpectedError(Exception):
    def __init__(self, expected_types, token):
        self.expected_types = expected_types
        self.token = token


def maybe(fn) -> Optional:
    try:
        return fn()
    except ExpectedError:
        return


class JsonParser:
    VALUE_TYPE = Union[int, float, str, list, dict, type(None)]

    def __init__(self, tokens: Iterable[Token]):
        self._tokens = list(tokens)
        self._idx = 0  # current token index

    def consume(self, *token_types):
        self.expect(*token_types)
        return self.advance()

    def advance(self) -> Token:
        """
        Returns current_token and increments the current token index
        """
        token = self.token
        self._idx += 1

        if self._idx > len(self._tokens):
            raise ParserError

        return token

    @property
    def token(self) -> Optional[Token]:
        """
        Returns current token or None if no such token
        """
        try:
            return self._tokens[self._idx]
        except IndexError:
            return None

    def check_token_type(self, *token_types: str) -> bool:
        return self.token and self.token.type in token_types

    @property
    def lookup(self) -> Optional[Token]:
        """
        Returns next token or None if no such token
        """
        try:
            return self._tokens[self._idx + 1]
        except IndexError:
            return None

    def parse(self) -> VALUE_TYPE:
        return self.read_value()

    def read_value(self) -> VALUE_TYPE:
        expected = []

        readers = [
            self.read_number,
            self.read_string,
            self.read_list,
            self.read_dict,
            self.read_null,
            self.read_true,
            self.read_false
        ]

        for reader in readers:
            try:
                return reader()
            except ExpectedError as e:
                expected += e.expected_types

        if expected:
            token_type = getattr(self.token, 'type', 'no token')
            raise ParserError(
                f'Expected on of {", ".join(expected)}, got {token_type} instead'
            )

    def expect(self, *token_types):
        if not self.check_token_type(*token_types):
            raise ExpectedError(token_types, self.token)

    def read_number(self) -> Union[int, float]:
        token = self.consume('NUMBER')

        if token.value.isdigit():
            return int(token.value)

        return float(token.value)

    def read_string(self) -> str:
        return self.consume('STRING').value[1:-1]

    def read_list(self) -> list:
        self.consume('L_BRACKET')

        rv = []

        while not self.check_token_type('R_BRACKET'):
            value = self.read_value()
            rv.append(value)

            if not maybe(self.read_comma):
                break

        if not self.check_token_type('R_BRACKET'):
            raise ParserError(
                f'Expected "," or "]", got {self.token.type} instead'
            )

        self.advance()

        return rv

    def read_comma(self):
        return self.consume('COMMA')

    def read_null(self) -> None:
        self.consume('NULL')
        return None

    def read_true(self) -> True:
        self.consume('TRUE')
        return True

    def read_false(self) -> True:
        self.consume('FALSE')
        return False

    def read_dict(self) -> dict:
        self.consume('L_BRACE')

        rv = {}

        while not self.check_token_type('R_BRACE'):
            key, value = self.read_pair()
            rv[key] = value
            maybe(self.read_comma)

        if not self.check_token_type('R_BRACE'):
            raise ParserError(
                f'Expected "," or "}}", got {self.token.type} instead'
            )

        self.advance()
        return rv

    def read_pair(self) -> tuple:
        key = self.read_string()
        self.read_colon()
        value = self.read_value()

        return key, value

    def read_colon(self):
        return self.consume('COLON')


json_text = r"""
[
    1, 
    "two", 
    true,
    false, 
    null,
    {"hello": "world", "hi": "there"},
]
"""


def main():
    try:
        tokens = list(JsonLexer.lex(json_text))
        print(tokens)
    except LexerError as e:
        print(e.pretty())
        return exit(1)

    parser = JsonParser(tokens)
    print(repr(parser.parse()))


if __name__ == '__main__':
    main()
