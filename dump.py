#!/usr/bin/env python3
# Author   : Martin Užák <martin.uzak@gmail.com>
# Creation : 2020-04-01 17:39

import model
import argparse
import version
import json

from parser import load_db


def dump(verbose=False):
    for lang in sorted(model.World.Languages.values(), key=lambda l: len(l), reverse=True):
        print(f"{lang} {len(lang)}")

    print(f"Union ({len(model.Union.Table)})")
    if verbose:
        for union in model.Union.Table.values():
            print(f"\t{union.word} {{{union}}}")

    for cls in (model.Derived, model.Equals, model.Related):
        print(f"Relationship {cls.cls_str()}")
        if verbose:
            seen = []
            for k, v in cls.Table.items():
                if v not in seen:
                    print(f"\t{v}")
                    seen.append(v)

    tags = model.World.Tags.keys()
    print(f"Tags ({len(tags)}): {', '.join(tags)}")


def export_json():
    result = {}
    result["words"] = []
    for lang in model.World.Languages.values():
        result["words"].extend([w.to_json() for w in lang.words.values()])
    result["relationships"] = {}
    for cls in (model.Derived, model.Related, model.Equals):
        key = cls.__name__.lower()
        result["relationships"][key] = []
        for rel in cls.Table.values():
            result["relationships"][key].append(rel.to_json())
    result["unions"] = []
    for union in model.Union.Table.values():
        result["unions"].append(union.to_json())
    result["version"] = version.rev_no
    # TODO export Tags
    print(json.dumps(result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", default=False)
    parser.add_argument("-j", "--json", action="store_true", default=False)
    args = parser.parse_args()

    load_db()
    if args.json:
        export_json()
    else:
        dump(args.verbose)
