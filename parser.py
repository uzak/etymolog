#!/usr/bin/env python3

"""
Parse .pill files
"""

import os
import re
import model
import config
import ply.yacc

from log import log

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


def p_word_lang_tokens(p):
    'word : LANG tokens'
    lang = model.World.lang(p[1])
    p[0] = lang.add_word(p[2])


def p_word_tokens(p):
    'word : tokens'
    lang = model.World.lang(config.default_lang)
    p[0] = lang.add_word(p[1])


def p_tokens_tokens_token(p):
    'tokens : tokens TOKEN'
    p[0] = f"{p[1]} {p[2]}"


def p_tokens_token(p):
    'tokens : TOKEN'
    p[0] = p[1]

# inline comments

def p_word_word_ic(p):
    'tokens : tokens LPAREN tokens RPAREN'
    p[0] = p[1]


def p_word_ic_word(p):
    'tokens : LPAREN tokens RPAREN tokens'
    p[0] = p[4]


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
    '''
    # NOTE relationship reduces to last expression
    if p[1] == p[3]:
        raise ValueError("self-referencing relationship is not allowed")
    if p[2] == "->":
        model.Derived.add(p[1], p[3])
        p[0] = p[3]
    elif p[2] == "=":
        model.Equals.add(p[1], p[3])
        p[0] = p[3]
    elif p[2] == "~":
        model.Related.add(p[1], p[3])
        p[0] = p[3]


# Comments
union_pat = re.compile(r"(\w+\s*:\s*)?(\w+)\s*\+\s*(\w+\s*:\s*)?(\w+)")


def p_expression_word_comment(p):
    'expression : word COMMENT'
    comment = p[2]
    word = p[1]

    # let's see if it is an union
    match = union_pat.match(comment)
    if match:
        lang_left, left, lang_right, right = match.groups()
        ll = lr = word.lang
        if lang_left:
            ll = model.World.lang(lang_left.rstrip(":"))
        if lang_right:
            lr = model.World.lang(lang_right.rstrip(":"))
        w1 = ll.add_word(left)
        w2 = lr.add_word(right)
        p[0] = union = model.Union(w1, w2)
        word.unions.add(union)
    else:
        word.comment(comment)
        p[0] = word


def p_expression_expr_rel_comment_expr(p):
    '''expression : expression DERIVE COMMENT expression
                  | expression EQUALS COMMENT expression
                  | expression RELATED COMMENT expression
    '''
    if p[1] == p[4]:
        raise ValueError("self-referencing relationship is not allowed")
    comment = p[3]
    if p[2] == "->":
        p[0] = model.Derived.add(p[1], p[4], comment=comment)
    elif p[2] == "=":
        p[0] = model.Equals.add(p[1], p[4], comment=comment)
    elif p[2] == "~":
        p[0] = model.Related.add(p[1], p[4], comment=comment)
    p[0] = p[4]


def p_word_union(p):
    'word : union'
    p[0] = p[1]

def p_union_token_token(p):
    'union : TOKEN PLUS TOKEN'
    lang = model.World.lang(config.default_lang)
    w1 = lang.add_word(p[1])
    w2 = lang.add_word(p[3])
    p[0] = union = model.Union(w1, w2)
    union.register_composite_word()


def p_union_lang_token_token(p):
    'union : LANG TOKEN PLUS TOKEN'
    lang = model.World.lang(p[1])
    w1 = lang.add_word(p[2])
    w2 = lang.add_word(p[4])
    p[0] = union = model.Union(w1, w2)
    union.register_composite_word()

# META is either an user defined comment that will be ignored
# or a pragma directive for the parser

orig_default_lang = None

def handle_meta(comment):
    comment = comment.strip()
    if comment.startswith("SRC"):
        src = comment[4:]
        config.default_source = src
    if comment.startswith("LANG"):
        global orig_default_lang        # XXX global ...
        if not orig_default_lang:
            orig_default_lang = config.default_lang
        lang = comment[5:]
        config.default_lang = lang


def p_meta(p):
    '''expression : expression META
                  | META
    '''
    if len(p) == 3:
        p[0] = p[1]
        meta = p[2]
    else:
        meta = p[1]
    handle_meta(meta)


def p_error(p):
    raise SyntaxError(f"Syntax error at token {p!r}")


def t_eof(t):
    pass


precedence = (
    ('left', 'EQUALS', 'RELATED', 'DERIVE'),
    ('left', 'COMMENT'),
    ('left', 'SEP'),
    ('left', 'PLUS'),
    ('left', 'LPAREN', 'RPAREN'),
    ('left', 'LANG'),
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
    if orig_default_lang:
        log.debug(f"Setting config.default_lang={orig_default_lang}")
        config.default_lang = orig_default_lang


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
