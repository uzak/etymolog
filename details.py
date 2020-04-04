#!/usr/bin/env python3
# Author   : Martin Užák <martin.uzak@gmail.com>
# Creation : 2020-04-01 17:39

import model
from dump import load_db

indent_size = 4


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


def translations_str(word, rel_type=model.Equals):
    trs = [str(tr) for tr in translations(word, rel_type=rel_type)]
    equals = ", ".join(trs)
    return f" {rel_type.Symbol} {equals}" if equals else ""


def parents(word):
    for p in word.derived_from:
        parents(p.left)
        if isinstance(p.left , model.Union):
            print(f"    {p.left.left}{translations_str(p.left)}")
            print(f"      +")
            print(f"    {p.left.right}{translations_str(p.left)}")
        else:
            print(f"    {p.left}{translations_str(p.left)}")
        if word.derived_from:
            comments = comments_str(p)
            print(f"      | {comments}")


def comments_str(word):
    if word.comments:
        comments = ", ".join(word.comments)
        return f"[{comments}]"
    return ""


def derived_details(word, indent):
    for c in word.derives:
        comments = comments_str(c.right)
        print(f"{indent}{model.Derived.Symbol} {c.right}{translations_str(c.right)} {comments}")
        if c.right.derives:
            derived_details(c.right, indent + ' '*indent_size)


def details(word):
    indent = ' ' * (indent_size + 1)
    trs = translations(word)
    for t in trs:
        comments = comments_str(t)
        print(f"{indent}{model.Equals.Symbol} {t} {comments}")
    trs = translations(word, rel_type=model.Related)
    for t in trs:
        comments = comments_str(t)
        print(f"{indent}{model.Equals.Symbol} {t} {comments}")
    derived_details(word, indent)


#XXX move to word?
def word_details(word):
    parents(word)
    print(f" => {word}")
    if word.union:
        for i, union in enumerate(word.union):
            print(f"    UNION: {i+1}. {union.left}{translations_str(union.left)}")
            print(f"    UNION: {i+1}. {union.right}{translations_str(union.right)}")
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
