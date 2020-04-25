#!/usr/bin/env python3

"""
Parse .pill files
"""

import os
import model
import config
import ply.yacc

from log import log

from lexer import tokens

#
# YACC
#

class IgnoreFile(Exception):
    "Indicator that processing of a file will be skipped"
    pass

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

def p_inline_comment_word(p):
    'word : word PAREN'
    p[0] = p[1]

def p_inline_tokens_comment(p):
    'tokens : tokens PAREN'
    p[0] = p[1]

def p_inline_comment_tokens(p):
    'tokens : PAREN tokens'
    p[0] = p[2]

# Groups


def p_expression_group(p):
    'expression : group'
    p[0] = p[1]


def p_group_expression_comma_expression(p):
    'group : expression SEP expression'
    if p[3] is None:
        raise ValueError("trailing group item is empty")
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
    # XXX todo check for circularity here
    if p[3] is None:
        raise ValueError("right side of relationship yields ``None``")
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


def p_expression_word_comment(p):
    'word : word COMMENT'
    word = p[1]
    word.comment(p[2])
    p[0] = word


def p_expression_expr_rel_comment_expr(p):
    '''expression : expression DERIVE COMMENT expression
                  | expression EQUALS COMMENT expression
                  | expression RELATED COMMENT expression
    '''
    # XXX todo check for circularity here
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


# Unions


_pre_union_default_lang = None
def p_start_union(p):
    'start_union : '
    global _pre_union_default_lang
    _pre_union_default_lang = config.default_lang
    config.default_lang = p[-1].lang.name    # access grammar symbol to the left


def p_end_union(p):
    'end_union : '
    config.default_lang = _pre_union_default_lang


def p_word_union(p):
    'word : word start_union union end_union'
    union = model.Union(p[1], *p[3])
    p[1].unions.add(union)
    p[0] = p[1]


def p_union(p):
    'union : LUNION word plus_words RUNION'
    p[3].insert(0, p[2])
    p[0] = p[3]


def p_plus_words2(p):
    'plus_words : plus_words PLUS word'
    p[1].append(p[3])
    p[0] = p[1]


def p_plus_words1(p):
    'plus_words : PLUS word'
    p[0] = [p[2]]


# META is either an user defined comment that will be ignored
# or a pragma directive for the parser

orig_default_lang = None

def handle_meta(meta, p):
    meta = meta.strip()
    if meta.startswith("SRC"):
        src = meta[4:].strip() or None
        config.default_source = src
    elif meta.startswith("NOSRC"):
        config.default_source = None
    elif meta.startswith("LANG"):
        global orig_default_lang        # XXX global ...
        if not orig_default_lang:
            orig_default_lang = config.default_lang
        lang = meta[5:]
        config.default_lang = lang
    elif meta.startswith("IGNORE"):
        raise IgnoreFile



def p_meta(p):
    '''expression : expression META
                  | META
    '''
    if len(p) == 3:
        p[0] = p[1]
        meta = p[2]
    else:
        meta = p[1]
    handle_meta(meta, p)


def p_tag(p):
    'word : word TAG'
    p[1].add_tag(p[2])
    p[0] = p[1]


def p_error(p):
    raise SyntaxError(f"Syntax error at token {p!r}")


def t_eof(t):
    pass


precedence = (
    ('left', 'EQUALS', 'RELATED', 'DERIVE'),
    ('left', 'LUNION', 'RUNION'),
    ('left', 'COMMENT'),
    ('left', 'SEP'),
    ('left', 'PLUS'),
    ('left', 'TAG'),
    ('left', 'LANG'),
    ('left', 'META'),
    ('left', 'PAREN'),
)

yacc = ply.yacc.yacc()


def parse_file(fn):
    log.debug(f"Parsing: {fn}")
    with open(fn) as f:
        for line in f.readlines():
            try:
                yacc.parse(line)
            except IgnoreFile:
                break
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
