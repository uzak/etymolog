#!/usr/bin/env python3
# Author   : Martin Užák <martin.uzak@gmail.com>
# Creation : 2020-04-04 15:02

import model
import locale
import details

from dump import load_db

locale.setlocale(locale.LC_ALL, '')


def derived_paths(word, path=()):
    """ancestor chains of word: one list of relationships per branch, sorted"""
    path = path + (word,)
    parents = sorted((r for r in word.derived_from if r.left not in path),  # skip cycles
                     key=lambda r: str(r.left))
    result = []
    for rel in parents:
        for sub in derived_paths(rel.left, path) or [[]]:
            result.append([rel] + sub)
    return result


def derived(word, indent, incl_comments=True):
    for chain in derived_paths(word):
        result = []
        for rel in chain:
            if rel.comments and incl_comments:
                comments_str = " ".join([f"[{c}]" for c in sorted(rel.comments)])
                result.append(f"-> {comments_str} {rel.left}")
            else:
                result.append(f"-> {rel.left}")
        print(f'{indent}{" ".join(result)}')


def dictionary(lang_name, incl_comments=True):
    lang = model.World.lang(lang_name)
    print(f"Dictionary for ``{lang.name}`` ({len(lang)} items):")
    for w in sorted(lang, key=lambda word: locale.strxfrm(word.value.lower())):
        indent = "    "
        print(f"* {w.value}")
        if w.equals:
            print(details.translations_str(w, rel_type=model.Equals, indent=indent, incl_comments=incl_comments))
        if w.related:
            print(details.translations_str(w, rel_type=model.Related, indent=indent, incl_comments=incl_comments))
        if incl_comments:
            for comment in w.comments:
                print(f"{indent}[{comment}]")
        derived(w, indent, incl_comments=incl_comments)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("lang")
    parser.add_argument('--sc', help="suppress comments", default=False, action="store_true")
    args = parser.parse_args()

    #XXX add translate_to_languages=* ?

    load_db()

    if args.lang.lower() not in model.World.Languages:
        parser.error(f"unknown language: {args.lang}")
    dictionary(args.lang, incl_comments=not args.sc)
