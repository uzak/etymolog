#!/usr/bin/env python3

"""
Parse .pill files
"""

import model
import config

from lexer import tokens

#
# YACC
#

# Words

def p_expression_word(p):
    'expression : word'
    p[0] = p[1]


def p_word_token_colon_token(p):
    'word : TOKEN COLON TOKEN'
    p[0] = model.World.lang(p[1]).word(p[3])


def p_word_word_word(p):
    '''word : word word'''
    if p[1].lang.name != p[2].lang.name:
        if p[2].lang.name == config.default_lang:
            p[2].lang = model.World.lang(p[1].lang.name)
    assert p[1].lang.name == p[2].lang.name
    p[0] = model.World.lang(p[1].lang.name).word(f"{p[1].value} {p[2].value}")


def p_word_token(p):
    'word : TOKEN'
    p[0] = model.World.lang(config.default_lang).word(p[1])


def p_expression_lparen_expr_rparen(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]


# Groups

def p_expression_group(p):
    'expression : group'
    p[0] = p[1]


def p_group_expression_comma_expression(p):
    'group : expression COMMA expression'
    c = model.Group(p[1], p[3])
    p[0] = c

# Relationships

def p_expr_rel(p):
    'expression : relationship'
    p[0] = p[1]


def p_relationship_word_rel_word(p):
    '''relationship : expression DERIVE expression
                    | expression RELATED expression
                    | expression EQUALS expression
                    | expression PLUS expression
    '''
    # NOTE relationship reduces to last expression
    if p[2] == "->":
        model.World.rel(model.Derive, p[1], p[3])
        p[0] = p[3]
    elif p[2] == "=":
        model.World.rel(model.Equals, p[1], p[3])
        p[0] = p[3]
    elif p[2] == "~":
        model.World.rel(model.Related, p[1], p[3])
        p[0] = p[3]
    elif p[2] == "+":
        p[0] = model.World.rel(model.Union, p[1], p[3])

# Comments

def p_expression_word_comment(p):
    'expression : word COMMENT'
    p[1].comment(p[2][1:-1])
    p[0] = p[1]


def p_expression_expr_rel_comment_expr(p):
    '''expression : expression DERIVE COMMENT expression
                  | expression EQUALS COMMENT expression
                  | expression RELATED COMMENT expression
    '''
    if p[2] == "->":
        p[0] = model.World.rel(model.Derive, p[1], p[4])
    elif p[2] == "=":
        p[0] = model.World.rel(model.Equals, p[1], p[4])
    elif p[2] == "~":
        p[0] = model.World.rel(model.Related, p[1], p[4])
    p[0].comment(p[3][1:-1])
    p[0] = p[4]


# META is either an user defined comment that will be ignored
# or a pragma directive for the parser

def handle_meta(comment):
    comment = comment.strip()
    if comment.startswith("SRC"):
        src = comment[4:]
        config.default_source = src


def p_meta(p):
    '''expression : expression META
                  | META
    '''
    if len(p) == 3:
        p[0] = p[1]
        handle_meta(p[2][1:])
    else:
        handle_meta(p[1][1:])


def p_error(p):
    raise SyntaxError(f"Syntax error at token {p!r}")

def t_eof(t):
    pass

precedence = (
    ('left', 'EQUALS', 'RELATED', 'DERIVE'),
    ('left', 'COMMA'),
    ('left', 'PLUS'),
    ('left', 'LPAREN', 'RPAREN'),
    ('left', 'COLON'),
    ('left', 'META'),
)


import ply.yacc
yacc = ply.yacc.yacc()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    with open(args.file) as f:
        for line in f.readlines():
            line = line.strip()
            if line:
                yacc.parse(line)
