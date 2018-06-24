import re
import sre_constants
from typing import NamedTuple, List, Pattern, Iterable, Union, Optional

ERROR_SYMBOL = '^'


def format_error_line(text, line, column, error_symbol=ERROR_SYMBOL):
    text_line = text.split('\n')[line - 1]

    if not text_line:
        return ''

    tabs_count = text_line[:column].count('\t')
    error_line = error_symbol.rjust(min(column - tabs_count, len(text_line) - tabs_count))
    error_line = '\t' * tabs_count + error_line
    return text_line + '\n' + error_line


class RuleError(Exception):
    pass


class LexerError(Exception):
    def __init__(self, message: str, text: str, line: int, column: int):
        super().__init__(message)
        self.message = message
        self.text = text
        self.line = line
        self.column = column

    def pretty(self) -> str:
        return self.message + '\n' + format_error_line(self.text, self.line, self.column)


class Token(NamedTuple):
    type: str
    value: str
    line: int
    column: int

    def __cmp__(self, other: Union['Token', str]):
        if isinstance(other, str):
            return self.type == other

        return self.type == other.type and self.value == other.value


class Rule(NamedTuple):
    token_type: str
    regex: Pattern

    def validate(self):
        if self.regex.match(''):
            raise RuleError(f'Regex {repr(self.regex.pattern)} matches empty string')


class TokenIter:
    def __init__(self, text: str, rules: List[Rule], ignore_type: str):
        self._text = text
        self._rules = rules
        self._ignore_type = ignore_type

    def __iter__(self) -> Iterable[Token]:
        text = self._text
        rules = self._rules

        idx = 0  # text index
        line = 1
        column = 1

        while idx < len(self._text):
            longest_match = None
            longest_rule = None

            for rule in rules:
                match = rule.regex.match(text, idx)

                if match and rule.token_type:
                    longest_match = longest_match or match
                    longest_rule = longest_rule or rule

                    if match.end() > longest_match.end():
                        longest_match = match
                        longest_rule = rule

            if longest_match is None:
                try:
                    char = text.split('\n')[line - 1][column - 1]
                    message = f'No match for character {repr(char)} in line {line} column {column}'
                except IndexError:
                    message = f'No match in line {line} column {column}'

                raise LexerError(
                    message,
                    text,
                    line,
                    column
                )

            match_text = longest_match.group()
            idx = longest_match.end()
            new_lines = match_text.count('\n')

            if longest_rule.token_type != self._ignore_type:
                yield Token(
                    type=longest_rule.token_type,
                    value=match_text,
                    line=line,
                    column=column,
                )

            if new_lines:
                line += new_lines
                column = len(match_text.split('\n')[-1]) + 1
            else:
                column += len(match_text)


class Lexer:
    ignore: Optional[str] = None
    rules: List[Rule] = None
    IGNORE_TYPE = '__IGNORE__'

    @classmethod
    def lex(cls, text: str) -> Iterable[Token]:
        return TokenIter(text, cls.rules, cls.IGNORE_TYPE)

    def __str__(self):
        rules = ', '.join(str(x) for x in self.rules)
        return f'{self.__class__.__name__}<{rules}>'

    def __init_subclass__(cls, **kwargs):
        rules = []

        if cls.ignore:
            rule = Rule(
                token_type=cls.IGNORE_TYPE,
                regex=re.compile(cls.ignore, re.UNICODE),
            )
            rule.validate()
            rules.append(rule)

        for token_type, regex in cls.__dict__.items():
            if token_type.startswith('_') or not token_type.isupper():
                continue

            try:
                compiled_re = re.compile(regex, re.UNICODE)
            except sre_constants.error:
                raise RuleError(
                    f'Could not compile regex {repr(regex)}'
                    '\nEscape a character with \\ (backslash) if needed'
                )

            rule = Rule(
                token_type=token_type,
                regex=compiled_re,
            )
            rule.validate()
            rules.append(rule)

        cls.rules = rules
