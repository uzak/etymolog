#!/usr/bin/env python3
"""
Tokenizer for .pill files
"""

import ply.lex as lex
from log import log

tokens = (
    'EQUALS', 'DERIVE',
    'LANG',
    'TOKEN',
    'PLUS',
    'SEP',
    'COMMENT', 'META', 'LUNION', 'RUNION', # TODO Rename?
    'RELATED',
    'TAG',
    'PAREN',
)

# Tokens
t_EQUALS  = r'='
t_DERIVE  = r'->'
t_RELATED = r'~'
t_PLUS    = r'\+'
t_SEP     = ','
t_TOKEN   = r"[\w'/\.]+"        # rules: s/,/\// and s/-/./
t_LUNION  = r'{'
t_RUNION  = r'}'

def t_TAG(t):
    r'[#]\s*\w+'
    t.value = t.value.lstrip("#").strip()
    return t


def t_META(t):
    "//.*"
    t.value = t.value[2:]
    return t


def t_PAREN(t):
    r"\(.*?\)"
    t.value = t.value[1:-1]
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
    raise SyntaxError(f"Illegal character {t.value[0]!r} at line: {t.lexer.lineno}")


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


t_ignore = ' \t'

lexer = lex.lex()


if __name__ == '__main__':
    lex.runmain()
