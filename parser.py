#!/usr/bin/env python3

"""
Parse .pill files
"""

import os
import model
import config
import ply.yacc

from config import log

from lexer import tokens

#
# YACC
#

def p_empty_line(p):
    'expression : '
    # do nothing

# Words

def p_expression_word(p):
    'expression : word'
    p[0] = p[1]


def p_word_token_colon_token(p):
    'word : TOKEN COLON TOKEN'
    p[0] = model.World.lang(p[1]).add_word(p[3])


def p_word_word_word(p):
    'word : word word'
    p[0] = p[1].lang.concat(p[1], p[2])


def p_word_token(p):
    'word : TOKEN'
    p[0] = model.World.lang(config.default_lang).add_word(p[1])

# inline comments

def p_word_word_ic(p):
    'word : word LPAREN word RPAREN'
    p[0] = p[1]
    p[3].lang.del_word(p[3])

def p_word_ic_word(p):
    'word : LPAREN word RPAREN word'
    p[0] = p[4]
    p[2].lang.del_word(p[2])


# Groups

def p_expression_group(p):
    'expression : group'
    p[0] = p[1]


def p_group_expression_comma_expression(p):
    'group : expression SEP expression'
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
        model.Derived.add(p[1], p[3])
        p[0] = p[3]
    elif p[2] == "=":
        model.Equals.add(p[1], p[3])
        p[0] = p[3]
    elif p[2] == "~":
        model.Related.add(p[1], p[3])
        p[0] = p[3]
    elif p[2] == "+":
        p[0] = union = model.Union(p[1], p[3])
        union.register(p[1].lang)

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
    comment = p[3][1:-1]
    if p[2] == "->":
        p[0] = model.Derived.add(p[1], p[4], comment=comment)
    elif p[2] == "=":
        p[0] = model.Equals.add(p[1], p[4], comment=comment)
    elif p[2] == "~":
        p[0] = model.Related.add(p[1], p[4], comment=comment)
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
    ('left', 'SEP'),
    ('left', 'PLUS'),
    ('left', 'LPAREN', 'RPAREN'),
    ('left', 'COLON'),
    ('left', 'META'),
)

yacc = ply.yacc.yacc()


def parse_file(fn):
    log.debug(f"Parsing: {fn}")
    with open(fn) as f:
        for line in f.readlines():
            yacc.parse(line)
        finish_file()


def finish_file():
    log.debug("Setting config.default_source=None")
    config.default_source = None


def get_pills(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith(".pill"):
                yield os.path.join(root, f)


def load_db(db_dir=None):
    db_dir = db_dir or os.path.join(os.path.dirname(__file__), "db")
    for fn in get_pills(db_dir):
        parse_file(fn)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    parse_file(args.file)
