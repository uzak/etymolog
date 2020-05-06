#!/usr/bin/env python3
# Author   : Martin Užák <martin.uzak@gmail.com>
# Creation : 2020-04-01 17:39

from dataclasses import dataclass

import model
from dump import load_db


def sp(obj):
    text = str(obj)
    return text if not text else ' ' + text


@dataclass
class Translation:
    rel: model.Relationship
    word: model.Word

    def __hash__(self):
        return hash(self.word)


def groupby(key_fct, seq):
    result = {}
    for item in seq:
        key = key_fct(item)
        if key not in result:
            result[key] = set()
        result[key].add(item)
    return result


def groupby_lang_name(seq):
    return groupby(lambda x: x.lang.name, seq)


def split(fct, seq):
    return set(filter(fct, seq)), \
           set(filter(lambda x: not fct(x), seq))


def comments_str(entity):
    if entity.comments:
        return " ".join([f"[{c}]" for c in entity.comments])
    return ""


def translations(word, rel_type=model.Equals):
    if rel_type is model.Equals:
        data = word.equals
    elif rel_type is model.Related:
        data = word.related
    else:
        assert 0
    for rel in data:
        translation = rel.right if rel.left == word else rel.left
        yield translation


def groupbylang_tx(seq):
    return groupby(lambda x: x.word.lang.name, seq)


def translations_str(word, rel_type=model.Equals, ignore=set(), indent="",
                     oneline=False, incl_comments=True):
    # sort data
    translations_comments = []
    translations_no_comments = []
    if rel_type is model.Equals:
        data = word.equals
    elif rel_type is model.Related:
        data = word.related
    for rel in data:
        w = rel.right if rel.left == word else rel.left
        tx = Translation(rel = rel, word=w)
        if tx.word not in ignore:
            if not oneline and tx.rel.comments or tx.word.comments:
                translations_comments.append(tx)
            else:
                translations_no_comments.append(tx)

    # print
    firstline = []
    for lang, txs in groupbylang_tx(translations_no_comments).items():
        tx_str = ", ".join([tx.word.value for tx in txs])
        firstline.append(f"{indent}{rel_type.Symbol} {lang}:{tx_str}")
    result = []
    if firstline:
        result.append("\n".join(firstline))
    for lang, txs in groupbylang_tx(translations_comments).items():
        for tx in txs:
            rel_comments = ""
            word_comments = ""
            if incl_comments:
                rel_comments = comments_str(tx.rel) or ""
                word_comments = comments_str(tx.word)
            result.append(f"{indent}{rel_type.Symbol}{rel_comments}{sp(tx.word)}{sp(word_comments)}")
    return "\n".join(result)


def parents(word, incl_comments=True):
    for p in word.derived_from:
        parents(p.left, incl_comments=incl_comments)
        if p.left.unions:
            print_unions(p.left, "   ", in_header=True)
        else:
            print(f"    {p.left} {translations_str(p.left, oneline=True, incl_comments=incl_comments)}")
        if word.derived_from:
            comments = comments_str(p)
            print(f"      | {comments}")
    else:
        if not word.derived_from:
            print(f"      * ")
            print(f"      |")


def derived_details(word, indent, seen_on_left=set(), incl_comments=True):
    for lang, derivates in groupby(lambda d: d.right.lang.name, word.derives).items():
        for d in derivates:
            indent_incl_word = indent + " "*(4+len(str(d.right)))
            trans = translations_str(d.right, ignore=seen_on_left, incl_comments=incl_comments, indent=indent_incl_word).lstrip()
            seen_on_left.add(d.left)
            if not incl_comments:
                comments = ""
            else:
                comments = comments_str(d)
            print(f"{indent}{model.Derived.Symbol} {d.right}{sp(trans)}{sp(comments)}")
            if d.right.derives:
                derived_details(d.right, indent + '  ', seen_on_left=seen_on_left, incl_comments=incl_comments)


def details(word, incl_comments=True):
    indent = '    '

    for u in word.in_unions:
        print(f"{indent}+ {u.word} {translations_str(u.word, incl_comments=incl_comments, oneline=True)}")

    derived_details(word, indent, set(), incl_comments=incl_comments)

    print(f"{indent}{translations_str(word, rel_type=model.Related)}")


def print_unions(word, indent, in_header=False):
    if word.unions:
        for i, u in enumerate(word.unions):
            if in_header:
                print(f"    {word} {translations_str(word, oneline=True)}")
            else:
                print(f"{indent}{i+1}. union: {u}")
            for component in u.components:
                print(f"{indent}   . {component} {translations_str(component, rel_type=model.Equals, oneline=True)}")


def pretty_print(word, incl_comments=True):
    indent = "    "
    parents(word, incl_comments=incl_comments)
    print(f" => {word.as_str(unions=False, comments=incl_comments)}")
    tx_str = translations_str(word, indent=indent, incl_comments=incl_comments)
    if tx_str:
        print(tx_str)
    print_unions(word, indent, in_header=False)
    details(word, incl_comments=incl_comments)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("lang")
    parser.add_argument("--sc", action="store_true", default=False)
    parser.add_argument("word")
    args = parser.parse_args()

    # XXX arg: translation_only_in?
    # XXX find similarly sounding (difflib.get_close_matches) sounds?

    load_db()

    w = model.World.lang(args.lang).get_word(args.word)
    if w:
        pretty_print(w, incl_comments=not args.sc)
    else:
        print(f"`{args.lang}:{args.word}` not found")
