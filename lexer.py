#!/usr/bin/env python3
"""
Tokenizer for .pill files
"""

import ply.lex as lex

tokens = (
    'TOKEN', 'COLON',
    'LPAREN', 'RPAREN',         # just for adjusting priority of eval
    'PLUS',
    'COMMA',
    'COMMENT', 'META',
    'EQUALS', 'DERIVE',
    'RELATED',
)

# Tokens
t_EQUALS  = r'='
t_DERIVE  = r'->'
t_RELATED = r'~'
t_PLUS    = r'\+'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_COLON   = ':'
t_COMMA   = ','
t_TOKEN   = r"[\w]+"
t_META    = r"[#].*"
t_COMMENT = r"\[.*?\]"


def t_error(t):
    print(f"Illegal character {t.value[0]!r}")
    t.lexer.skip(1)


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

t_ignore = ' \t'

lexer = lex.lex()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    with open(args.file) as f:
        lexer.input(f.read())

    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)
