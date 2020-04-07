#!/usr/bin/env python3
# Author   : Martin Užák <martin.uzak@gmail.com>
# Creation : 2020-04-01 17:39

import model
from dump import load_db

indent_size = 2


#XXX unittest/doctest?
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

#XXX unittest/doctest?
def translations_str(word, rel_type=model.Equals, ignore=set()):
    trs = translations(word, rel_type=rel_type)
    trs = set(trs).difference(ignore)
    trs = [str(tr) for tr in trs]
    equals = ", ".join(trs)
    return f" {rel_type.Symbol} {equals}" if equals else ""


def parents(word):
    for p in word.derived_from:
        parents(p.left)
        if p.left.union:
            print(f"    {p.left}{translations_str(p.left)}")
            print(f"      .{p.left.union.left}{translations_str(p.left.union.left)}")
            print(f"      .{p.left.union.right}{translations_str(p.left.union.right)}")
        else:
            print(f"    {p.left}{translations_str(p.left)}")
        if word.derived_from:
            comments = comments_str(p)
            print(f"      | {comments}")
    else:
        if not word.derived_from:
            print(f"      * ")          # AUM
            print(f"      |")


def comments_str(word):
    if word.comments:
        comments = ", ".join(word.comments)
        return f"[{comments}]"
    return ""


def derived_details(word, indent, seen_on_left=set()):
    for c in word.derives:
        comments = comments_str(c.right)
        #XXX also group by languages here
        trans = translations_str(c.right, ignore=seen_on_left)
        seen_on_left.add(c.left)
        print(f"{indent}{model.Derived.Symbol} {c.right}{trans} {comments}")
        if c.right.derives:
            derived_details(c.right, indent + ' '*indent_size, seen_on_left=seen_on_left)


#XXX unittest/doctest?
def _group_by_lang(translations):
    result = {}
    for t in translations:
        if t.lang.name not in result:
            # 1. set = translations with comments
            # 2. set = without
            result[t.lang.name] = set(), set()
        if t.comments:
            result[t.lang.name][0].add(t)
        else:
            result[t.lang.name][1].add(t)
    return result


def details(word):
    indent = ' ' * (indent_size + 1)
    trs = translations(word)
    # XXX DRY, make it more simple, comment
    for lang, (trs_comm, trs_no_comm) in _group_by_lang(trs).items():
        for t in trs_comm:
            comments = comments_str(t)
            print(f"{indent}{model.Equals.Symbol} {t} {comments}")
        print(f"{indent}{model.Equals.Symbol} {', '.join(map(str, trs_no_comm))}")
    trs = translations(word, rel_type=model.Related)
    for lang, (trs_comm, trs_no_comm) in _group_by_lang(trs).items():
        for t in trs_comm:
            comments = comments_str(t)
            print(f"{indent}{model.Related.Symbol} {t} {comments}")
        print(f"{indent}{model.Related.Symbol} {', '.join(map(str, trs_no_comm))}")
    derived_details(word, indent, set())


def word_details(word):
    parents(word)
    print(f" => {word}")
    if word.union:
        print(f"    UNION: {word.union.left}{translations_str(word.union.left)}")
        print(f"    UNION: {word.union.right}{translations_str(word.union.right)}")
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
        word_details(w)
