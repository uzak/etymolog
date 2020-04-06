#!/usr/bin/env python3
"""
Tokenizer for .pill files
"""

import ply.lex as lex
from config import log

tokens = (
    'LANG',
    'TOKEN',
    'LPAREN', 'RPAREN',         # just for adjusting priority of eval
    'PLUS',
    'SEP',
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
t_SEP     = ';'
t_TOKEN   = r"\w+"


def t_META(t):
    "//.*"
    t.value = t.value[2:]
    return t


def t_LANG(t):
    r'\w+\s*:'
    t.value = t.value.rstrip(':')
    return t


def t_COMMENT(t):
    r"\[.*?\]"
    t.value = t.value[1:-1]
    return t


def t_error(t):
    log.error(f"Illegal character {t.value[0]!r}")
    t.lexer.skip(1)


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

lexer = lex.lex()


if __name__ == '__main__':
    lex.runmain()
