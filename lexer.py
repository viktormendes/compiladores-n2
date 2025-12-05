import re
from typing import List, Tuple, cast
from ast_nodes import Token, LexError

_token_specification = [
    ("COMMENT_ML",    r"/\*[\s\S]*?\*/"),
    ("COMMENT_SL",    r"//[^\n]*"),
    ("NEWLINE",       r"\n"),
    ("WHITESPACE",    r"[ \t\r]+"),
    ("EQ",            r"=="),
    ("NE",            r"!="),
    ("LE",            r"<="),
    ("GE",            r">="),
    ("AND",           r"&&"),
    ("OR",            r"\|\|"),
    ("LT",            r"<"),
    ("GT",            r">"),
    ("EQUAL",         r"="),
    ("PLUS",          r"\+"),
    ("MINUS",         r"-"),
    ("STAR",          r"\*"),
    ("SLASH",         r"/"),
    ("LPAREN",        r"\("),
    ("RPAREN",        r"\)"),
    ("LBRACE",        r"\{"),
    ("RBRACE",        r"\}"),
    ("LBRACK",        r"\["),
    ("RBRACK",        r"\]"),
    ("SEMI",          r";"),
    ("COMMA",         r","),
    ("NUM",           r"\d+(\.\d+)?"),
    ("CHAR",          r"'.'"),
    ("STRING",        r"\"([^\"\\]|\\.)*\""),
    ("ID",            r"[A-Za-z_][A-Za-z0-9_]*"),
]

_master_regex = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in _token_specification),
    re.MULTILINE
)

_keywords_map = {
    "int": "INT",
    "float": "FLOAT",
    "char": "CHAR_TYPE",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "for": "FOR",
    "return": "RETURN",
    "void": "VOID",
    "true": "TRUE",
    "false": "FALSE",
}


def lex(code: str) -> Tuple[List[Token], List[LexError]]:
    tokens: List[Token] = []
    errors: List[LexError] = []
    line = 1
    col = 1
    pos = 0
    length = len(code)

    while pos < length:
        m = _master_regex.match(code, pos)
        if not m:
            ch = code[pos]
            errors.append(LexError(f"Simbolo inesperado '{ch}'", line, col))
            pos += 1
            if ch == '\n':
                line += 1
                col = 1
            else:
                col += 1
            continue

        kind = cast(str, m.lastgroup)    
        lexeme = cast(str, m.group(kind))  

        start = pos
        pos = m.end()

        if kind == "NEWLINE":
            tokens.append(Token("EOL", "", line, col))
            line += 1
            col = 1
            continue

        if kind in ("WHITESPACE", "COMMENT_ML", "COMMENT_SL"):
            newlines = lexeme.count('\n')
            if newlines:
                line += newlines
                last = lexeme.rfind('\n')
                col = len(lexeme) - last
            else:
                col += len(lexeme)
            continue

        ttype = kind
        if kind == "ID":
            ttype = _keywords_map.get(lexeme, "ID")

        tokens.append(Token(ttype, lexeme, line, col))
        col += (pos - start)

    if not tokens or tokens[-1].type != "EOL":
        tokens.append(Token("EOL", "", line, col))
    tokens.append(Token("EOF", "", line, col))
    return tokens, errors
