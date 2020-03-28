# Author   : Martin Užák <martin.uzak@gmail.com>
# Creation : 2020-03-28 14:59

"""
Parse .pill files
"""

#XXX EXPLANATION => LBRACE, RBRACE (and parse just like anything)

tokens = (
    'TOKEN', 'COLON', 'COMMA',
    'LPAREN', 'RPAREN',
    'EXPLANATION', 'META',
    'EQUALS', 'DERIVE', 'RELATED', 'PLUS',
)

# Tokens
t_EQUALS = r'='
t_DERIVE = r'->'
t_RELATED = r'~'
t_PLUS = r'\+'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COLON = ':'
t_COMMA = ','
#t_LBRACE = r'\['
#t_RBRACE = r'\]'

def t_TOKEN(t):
    r"[\w]+"
    return t

def t_META(t):
    r"[#].*$"
    return t

def t_EXPLANATION(t):
    r"\[.*?\]"
    return t

def t_error(t):
    print(f"Illegal character {t.value[0]!r}")
    t.lexer.skip(1)

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

t_ignore = ' \t'

import ply.lex as lex
lexer = lex.lex()

precedence = (
    ('left', 'EQUALS', 'DERIVE', 'RELATED', 'PLUS'),
    ('left', 'COLON'),
    ('left', 'COMMA'),
    ('left', 'LPAREN', 'RPAREN'),
)

def p_term(p):
    '''expression : TOKEN
                  | TOKEN TOKEN'''
    if len(p) == 3 :
        p[0] = f"{p[1]} {p[2]}"
    else:
        p[0] = p[1]

def p_term_lang(p):
    'expression : TOKEN COLON TOKEN'
    p[0] = f"{p[1]}:{p[3]}"

def p_token_list(p):
    'expression : expression COMMA expression'
    p[0] = f"{p[1]}, {p[3]}"
    print("comma", p[0])

def p_group(p):
    'expression : LPAREN expression RPAREN'
    #print(p.slice)
    #print(dir(p))
    p[0] = p[2]

def p_relationship(p):
    '''expression : expression DERIVE expression
                  | expression RELATED expression
                  | expression EQUALS expression
                  | expression PLUS expression
                  '''
    print("rel", p[1], p[2], p[3])
    p[0] = f"{p[1]}{p[2]}{p[3]}"

def p_single_rel(p):
    '''expression : DERIVE expression
                  | RELATED expression
                  | EQUALS expression
                  | PLUS expression
                  '''
    print("single REL", p[1], p[2])
    p[0] = f"{p[1]}{p[2]}"

def p_just_rel(p):
    '''expression : DERIVE
                  | RELATED
                  | EQUALS
                  | PLUS
                  '''
    print("just REL", p[1])
    p[0] = f"{p[1]}"



def p_relationship_explanation(p):
    '''expression : expression DERIVE EXPLANATION expression
                  | expression RELATED EXPLANATION expression
                  | expression EQUALS EXPLANATION expression
                  | expression PLUS EXPLANATION expression
                  '''
    print("rel + c", p[3])
    p[0] = f"{p[1]}{p[2]}{p[3]} {p[4]}"


def p_explanation(p):
    'expression : expression EXPLANATION'
    print("explanation", p[1], p[2])
    p[0] = f"{p[1]}, {p[2]}"

# meta is either a comment or a pragma directive
def p_meta(p):
    '''expression : expression META
                  | META
    '''
    if len(p) == 3:
        p[0] = p[1]
        print("IGNORE META", p[2])
    else:
        print("IGNORE META", p[1])


def p_error(p):
    print(f"Syntax error at {p.value!r}")


import ply.yacc as yacc
yp = yacc.yacc()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    # with open(args.file) as f:
    #     for line in f.readlines():
    #         yp.parse(line)

    data = """sa:Raghu -> Ragusa
sa:Raghu [dynasty in which Lord Rama took birth]
sa:dvi = both side
-> sa:dvi = both side, sk:dve
~
sa:Pasa -> sk:spasiť, sk:spása
#SRC https://www.facebook.com/groups/1520538148174445/permalink/2701503503411231/
sa:Pasu = [that which is observed, watched, beheld] animal
sa:Raghu ~ sa:Ravana # lala
# just comment
sa:pirya -> (free, friend)
(sa:dvi + sa:ap) -> (sa:Dvipa = island) -> hindu:Doab, ir:Dobar, cornish:Dofer, (celtic:Dubron -> Dubrovnik)
sa:pur [that which stands before its citizens, that which protects them]
sa:purohitam [that which (stands = sa:Hira) (before = sa:Pura)]
sa:Pasa -> (lat:Pacify -> (lat:Pact = covenant, agreement, contract -> (Peace = binding contract, treaty, agreement)))
sa:P = Purity ->[com1] sa:Pa = protect -> (sa:Pasu =[c2,cdf] animal)"""
    [yp.parse(line) for line in  data.splitlines()]

    # while True:
    #     tok = lexer.token()
    #     if not tok:
    #         break
    #     print(tok)
