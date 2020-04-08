#!/usr/bin/env python3
"""
Tokenizer for .pill files
"""

import ply.lex as lex
from log import log

tokens = (
    'LANG',
    'TOKEN',
    'LPAREN', 'RPAREN',
    'PLUS',
    'SEP',
    'COMMENT', 'META',
    'EQUALS', 'DERIVE',
    'RELATED',
    'TAG',
)

# Tokens
t_EQUALS  = r'='
t_DERIVE  = r'->'
t_RELATED = r'~'
t_PLUS    = r'\+'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_SEP     = ','
t_TOKEN   = r"[\w]+"

def t_TAG(t):
    r'[#]\s*\w+'
    t.value = t.value.lstrip("#").strip()
    return t


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
    raise SyntaxError(f"Illegal character {t.value[0]!r}")


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


t_ignore = ' \t'

lexer = lex.lex()


if __name__ == '__main__':
    lex.runmain()
