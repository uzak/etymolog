#!/usr/bin/env python3
# Author   : Martin Užák <martin.uzak@gmail.com>
# Creation : 2020-04-01 17:39

from dataclasses import dataclass

import config
import lookup
import model
from parser import load_db


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


def comment_lines(indent, *entities):
    """one line per comment, in the order of the entities"""
    return [f"{indent}{c}" for e in entities for c in e.comment_strs()]


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


def translations_str(word, rel_type=model.Equals, ignore=None, indent="",
                     oneline=False, incl_comments=True):
    # sort data
    ignore = ignore or set()
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
            if (not oneline and tx.rel.comments) or tx.word.comments:
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
            result.append(f"{indent}{rel_type.Symbol} {tx.word}")
            if incl_comments:
                result.extend(comment_lines(indent + "    ", tx.rel, tx.word))
    return "\n".join(result)


def parents(word, incl_comments=True, path=()):
    path = path + (word,)
    for p in word.derived_from:
        if p.left in path:  # cycle in data
            continue
        parents(p.left, incl_comments=incl_comments, path=path)
        if p.left.unions:
            print_unions(p.left, "   ", in_header=True, incl_comments=incl_comments)
        else:
            print(f"    {p.left} {translations_str(p.left, oneline=True, incl_comments=incl_comments)}")
        if word.derived_from:
            lines = [f"      | {c}" for c in p.comment_strs()] if incl_comments else []
            print("\n".join(lines) or "      | ")
    else:
        if not word.derived_from:
            print(f"      * ")
            print(f"      |")


def derived_details(word, indent, seen_on_left=set(), incl_comments=True, path=()):
    path = path + (word,)
    for lang, derivates in groupby(lambda d: d.right.lang.name, word.derives_to).items():
        for d in derivates:
            if d.right in path:  # cycle in data
                continue
            indent_incl_word = indent + " "*(4+len(str(d.right)))
            trans = translations_str(d.right, ignore=seen_on_left, incl_comments=incl_comments, indent=indent_incl_word).lstrip()
            seen_on_left.add(d.left)
            print(f"{indent}{model.Derived.Symbol} {d.right}{sp(trans)}")
            if incl_comments:
                for line in comment_lines(indent + "    ", d):
                    print(line)
            if d.right.derives_to:
                derived_details(d.right, indent + '  ', seen_on_left=seen_on_left, incl_comments=incl_comments, path=path)


def details(word, incl_comments=True):
    indent = '    '

    for u in word.in_unions:
        print(f"{indent}+ {u.word} {translations_str(u.word, incl_comments=incl_comments, oneline=True)}")
        derived_details(u.word, indent + "  ", set(), incl_comments=incl_comments)

    derived_details(word, indent, set(), incl_comments=incl_comments)

    print(translations_str(word, rel_type=model.Related, indent=indent, incl_comments=incl_comments))


def print_unions(word, indent, in_header=False, incl_comments=True):
    if word.unions:
        for i, u in enumerate(word.unions):
            if in_header:
                print(f"    {word} {translations_str(word, oneline=True, incl_comments=incl_comments)}")
            else:
                print(f"{indent}{i+1}. union: {u}")
            for component in u.components:
                print(f"{indent}   . {component} {translations_str(component, rel_type=model.Equals, oneline=True, incl_comments=incl_comments)}")


def hint(word):
    """first translation of a word, English preferred, as ' = lang:word'"""
    txs = sorted(translations(word), key=lambda w: (w.lang.name != "en", w.lang.name, w.value))
    return f" = {txs[0].key()}" if txs else ""


def print_similar(query, lang, exact, suggest=False):
    """list words that look (or, with suggest, sound) like query; exact matches are skipped"""
    if suggest:      # other languages too, but not English glosses
        langs = [l for l in model.World.Languages.values() if l is lang or l.name != "en"]
        hits = lookup.similar(query, langs, phonetic=True, cutoff=0.6, exclude=exact)
    else:
        hits = lookup.similar(query, [lang], exclude=exact)
    if hits:
        print("similar:")
    for score, w in hits:
        print(f"  {score:.2f} {w.key()}{hint(w)}")


def pretty_print(word, incl_comments=True):
    indent = "    "
    parents(word, incl_comments=incl_comments)
    print(f" => {word.as_str(unions=False, comments=False, tags=True)}")
    if incl_comments:
        for line in comment_lines(indent, word):
            print(line)
    tx_str = translations_str(word, indent=indent, incl_comments=incl_comments)
    if tx_str:
        print(tx_str)
    print_unions(word, indent, in_header=False, incl_comments=incl_comments)
    details(word, incl_comments=incl_comments)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--sc", action="store_true", default=False)
    parser.add_argument("-s", "--similar", action="store_true",
                        help="also list similar-looking words in the language")
    parser.add_argument("-S", "--suggest", action="store_true",
                        help="like --similar, but compare sound across other languages too")
    parser.add_argument("word",
                        help="word prefixed by language, e.g.: en:waters")
    args = parser.parse_args()

    # XXX arg: translation_only_in?

    load_db()

    if ":" in args.word:
        lang, _, word = args.word.partition(":")
        if not lang or not word or ":" in word:
            parser.error("expected [lang:]word, e.g. en:waters")
    else:
        lang = config.default_lang
        word = args.word

    if lang.lower() not in model.World.Languages:
        parser.error(f"unknown language: {lang}")
    lang = model.World.lang(lang)
    word = lang.translate(word)

    words = lang.get_words(word)
    if not words:
        print(f"`{lang.name}:{word}` not found")
    for w in words:
        pretty_print(w, incl_comments=not args.sc)
    if args.similar or args.suggest:
        print_similar(word, lang, words, suggest=args.suggest)
