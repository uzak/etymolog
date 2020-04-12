#!/usr/bin/env python3
# Author   : Martin Užák <martin.uzak@gmail.com>
# Creation : 2020-04-01 17:39

import model
from dump import load_db

indent_size = 2


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


def comments_str(word):
    if word.comments:
        comments = ", ".join(word.comments)
        return f"[{comments}]"
    return " "


def translations(word, rel_type=model.Equals):
    if rel_type is model.Equals:
        data = word.equals
    elif rel_type is model.Related:
        data = word.related
    else:
        assert 0
    for w in data:
        translation = w.right if w.left == word else w.left
        yield translation


def _translations_str(trs, rel_type=model.Equals):
    result = []
    for lang, words in groupby_lang_name(trs).items():
        trs = [str(tr.value) for tr in words]
        equals = ", ".join(trs)
        if trs:
            equals = f"{lang}:{equals}"
            result.append(equals)
    return f" {rel_type.Symbol} {', '.join(result)}" if result else " "


def translations_str(word, rel_type=model.Equals, ignore=set()):
    trs = translations(word, rel_type=rel_type)
    trs = set(trs).difference(ignore)
    return _translations_str(trs, rel_type=rel_type)


def parents(word):
    for p in word.derived_from:
        parents(p.left)
        if p.left.unions:
            for i, u in enumerate(p.left.unions):
                print(f"    {p.left}{translations_str(p.left)}")
                print(f"      .{u.left}{translations_str(u.left)}")
                print(f"      .{u.right}{translations_str(u.right)}")
        else:
            print(f"    {p.left}{translations_str(p.left)}")
        if word.derived_from:
            comments = comments_str(p)
            print(f"      | {comments}")
    else:
        if not word.derived_from:
            print(f"      * ")          # AUM
            print(f"      |")


def derived_details(word, indent, seen_on_left=set()):
    for lang, derivates in groupby(lambda d: d.right.lang.name, word.derives).items():
        for d in derivates:
            trans = translations_str(d.right, ignore=seen_on_left)
            seen_on_left.add(d.left)
            comments = comments_str(d)
            if comments:
                comments = ' ' + comments
            print(f"{indent}{model.Derived.Symbol} {d.right}{trans}{comments}")
            if d.right.derives:
                derived_details(d.right, indent + ' '*indent_size, seen_on_left=seen_on_left)


def details(word):
    indent = ' ' * (indent_size + 1)

    for u in word.in_unions:
        print(f"{indent} + {u.word}{translations_str(u.word)} {comments_str(u.word)}")

    derived_details(word, indent, set())

    trs = translations(word, rel_type=model.Related)
    for lang, lang_trs in groupby_lang_name(trs).items():
        trs_comm, trs_no_comm = split(lambda x: x.comments, lang_trs)
        for t in trs_comm:
            print(f"{indent} {model.Related.Symbol} {t}")
        if trs_no_comm:
            print(f"{indent}{_translations_str(trs_no_comm, rel_type=model.Related)}")


def pretty_print(word):
    parents(word)
    print(f" => {word.as_str(unions=False)}{translations_str(word)}")
    if word.unions:
        for i, u in enumerate(word.unions):
            print(f"    {i+1}. union: {u}")
    details(word)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("lang")
    parser.add_argument("word")
    args = parser.parse_args()

    # TODO arg: translation_only_in?
    # TODO find similarly sounding (difflib.get_close_matches) sounds

    load_db()

    w = model.World.lang(args.lang).get_word(args.word)
    if w:
        pretty_print(w)
    else:
        print(f"`{args.lang}:{args.word}` not found")
