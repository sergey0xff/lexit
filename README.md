# Lexit
Lexit is an open source lexer generator written in Python3.6 using new features like `NamedTuple`, type hinting and `__init_subclass__` hook.

### Simple example
```python
from typing import Iterable

from lexit import Lexer, Token


class MyLexer(Lexer):
    NUMBER = '\d+'
    ADD = '\+'
    SUB = '-'
    MUL = '\*'
    DIV = '/'

    ignore = r'\s+'


tokens_iter: Iterable[Token] = MyLexer.lex('2 + 2')
print(*tokens_iter, sep='\n')
```
Produces the following output
```python
Token(type='NUMBER', value='2', line=1, column=1)
Token(type='ADD', value='+', line=1, column=3)
Token(type='NUMBER', value='2', line=1, column=5)
```

### JSON lexer example 
```python
from lexit import Lexer


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


tokens = list(JsonLexer.lex('{"hello": "world"}'))
``` 

### Requirements
* The only requirement is Python3.6+
* For testing the `pytest` library is used

### Installation
```bash
pip install lexit
```

### Error handling
```
try:
    tokens = list(JsonLexer.lex('${"hello": "world"}'))
except LexerError as e:
    print(e.pretty())
    exit(1)

# The error message is self-describing
# It shows what happened and where 
No match for character '$' in line 1 column 1
${"hello": "world"}
^
```

### Design decisions
* Should be easy to use
* Longest match priority (`++` always wins over `+` despite of the order in which the tokens are defined in the lexer class)
* Self-describing errors for humans (it's should be obvious what happened and where)
