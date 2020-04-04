#!/usr/bin/env python3
# Author   : Martin Užák <martin.uzak@gmail.com>
# Creation : 2020-04-01 17:39

import model
import argparse

from parser import load_db


def dump(verbose=False):
    for lang in sorted(model.World.Languages.values(), key=lambda l: len(l), reverse=True):
        print(f"{lang} {len(lang)}")

    print(f"Union {len(model.Union.Table)}")
    if verbose:
        for union in model.Union.Table.values():
            print(f"\t{union}")

    for cls in (model.Derived, model.Equals, model.Related):
        print(f"Relationship {cls.cls_str()}")
        if verbose:
            seen = []
            for k, v in cls.Table.items():
                if v not in seen:
                    print(f"\t{v}")
                    seen.append(v)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", default=False)
    args = parser.parse_args()

    load_db()
    dump(args.verbose)
