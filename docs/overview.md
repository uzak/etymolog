# etymolog — overview (brief)

> Level 1 of 2. For the full picture (grammar, data model, CLI behaviour, JSON schema, known defects) read [reference.md](reference.md).

## What it is

`etymolog` is a small Python 3 project (author: Martin Užák, started 2020) for storing and querying **etymological facts**: which word derives from which, which words are translations of each other, which are loosely related, and which words are compounds of others.

It has three parts:

1. **A plain-text data format**, `.pill` files, one statement per line, e.g. `sa:Pas -> sa:Pasa -> lat:pax -> pacify`.
2. **A parser** (PLY lexer + yacc grammar) that loads all `.pill` files in `db/` into an in-memory object graph (`Word`, `Language`, `Derived`/`Equals`/`Related` relationships, `Union`).
3. **Three CLI tools** that read that graph: `details.py` (look up one word), `dict.py` (dictionary for one language), `dump.py` (stats or JSON export).

The shipped dataset (`db/`, ~94 pill files, ~14k words, ~93 languages, ~18k relationships) is heavily Sanskrit / Indo-European oriented, transcribed from several third-party sources.

There is no database server, no web service, no network access. The JSON export (`db.json`) is consumed by a separate UI repo (`~/repos/etymolog-ui`).

## How it is used

```sh
pip install ply pytest          # the only dependencies
./details.py sa:tr              # derivations/translations of Sanskrit "tr" (lang defaults to en)
./dict.py sk                    # dictionary of Slovak words with their derivation chains
./dump.py [-v]                  # stats (-v: list every relationship; very slow, ~20 s)
./dump.py -j > db.json          # JSON export for the UI (also: make db.json)
python -m pytest                # 68 tests, run from repo root
```

Run everything **from the repo root**; modules are imported by bare name (`import parser`, `import model`).

## Things to know before touching it

- All state is **global and mutable** (`config`, class-level `Table` dicts on the model classes, `World.Languages`). Loading the DB twice in one process duplicates/merges state; tests reset it via `tests/util.py::reset_model`.
- Words are matched **case-insensitively** (first-seen spelling wins). This wrongly merges distinct Sanskrit words (`varNa`/`varna`).
- Known defects exist (cycle in the data crashes `details.py`/`dict.py`; unions silently lost; non-deterministic export; `version.py` needs git). See *Known issues* in [reference.md](reference.md#9-known-issues-snapshot-from-an-audit).
- Source modules are named `parser.py`, `dict.py`, `log.py`, `version.py`, `config.py` — they shadow/resemble stdlib names; don't "fix" imports without checking.
