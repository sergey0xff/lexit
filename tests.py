import pytest

from lexit import Lexer, RuleError, LexerError


@pytest.fixture(scope='module', name='lexer')
def create_lexer():
    class TestLexer(Lexer):
        NUMBER = r'\d+'
        NAME = r'\w+'

        ADD = r'\+'
        SUB = r'-'
        MUL = r'\*'
        DIV = r'/'
        POW = r'\*\*'
        INCR = r'\+\+'

        ignore = '\s+'

    return TestLexer


@pytest.mark.parametrize('text,expected_token_types', [
    (' \t\n\r123 \t\n\r', ['NUMBER']),
    (' ', []),
    ('\n', []),
    ('\n\r', []),
    ('\r', []),
    ('\t', []),
])
def test_ignores_whitespaces(lexer: Lexer, text, expected_token_types):
    token_types = [x.type for x in lexer.lex(text)]
    assert token_types == expected_token_types


@pytest.mark.parametrize('text,expected_token_types', [
    ('123', ['NUMBER']),
])
def test_valid_cases(
    lexer: Lexer, text, expected_token_types
):
    token_types = [x.type for x in lexer.lex(text)]
    assert token_types == expected_token_types


@pytest.mark.parametrize('text', [
    '$', '   ^', '\n\n\r\t321??'
])
def test_invalid_cases_raise_exception(lexer: Lexer, text):
    with pytest.raises(LexerError):
        list(lexer.lex(text))


@pytest.mark.parametrize('text,expected_token_types', [
    ('+ ++', ['ADD', 'INCR']),
    ('* ** ++ +', ['MUL', 'POW', 'INCR', 'ADD']),
])
def test_longest_rule_wins(
    lexer: Lexer, text, expected_token_types
):
    token_types = [x.type for x in lexer.lex(text)]
    assert token_types == expected_token_types


@pytest.mark.parametrize('text,line,column', [
    ('123', 1, 1),
    (' 123', 1, 2),
    ('\n123', 2, 1),
    ('\n123\n\n\n\n', 2, 1),
    ('   \n  123   ', 2, 3),
])
def test_token_lines_and_columns(lexer: Lexer, text, line, column):
    first_token = list(lexer.lex(text))[0]
    assert first_token.line == line
    assert first_token.column == column


def test_rules_that_match_empty_strings():
    with pytest.raises(RuleError):
        class BadLexer(Lexer):
            BAD_RULE = r''

        BadLexer.lex('')

    with pytest.raises(RuleError):
        class BadLexer2(Lexer):
            BAD_RULE = r'(\d+|)'

        BadLexer2.lex('')
