#!/usr/bin/env python3
# Author   : Martin Užák <martin.uzak@gmail.com>
# Creation : 2020-04-04 15:02

import model
import details

from dump import load_db

def _derived(word, result):
    for w in word.derived_from:
        result.append(w.left)
        _derived(w.left, result=result)
    return result

def derived(word, indent):
    parents = _derived(word, [])
    parents_str = " -> ".join(map(lambda word: word.key(), parents))
    if parents:
        print(f"{indent}-> {parents_str}")

def dictionary(lang_name):
    lang = model.World.lang(lang_name)
    print(f"Dictionary for ``{lang.name}`` ({len(lang)} items):")
    for w in sorted(lang, key=lambda word: word.value.lower()):
        # TODO group translations by language
        print(f"* {w.value}{details.translations_str(w)}")
        indent = "    "
        if w.related:
            print(f"{indent}{details.translations_str(w, rel_type=model.Related)}")
        derived(w, indent)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("lang")
    args = parser.parse_args()

    #XXX add translate_to_languages=*
    #XXX special language handlers, e.g. english should remove "to" infront of verbs

    load_db()

    dictionary(args.lang)
