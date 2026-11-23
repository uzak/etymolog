# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`etymolog` stores and queries etymological facts (derivation, translation, loose relation, compounds). Data lives in plain-text `.pill` files under `db/`; a PLY lexer/parser loads them into an in-memory object graph; CLI scripts query that graph. Python 3, only dependencies are `ply` and `pytest` (venv in `.venv`).

Docs: `README.md` has the `.pill` grammar. `docs/overview.md` is a short intro and `docs/reference.md` is the detailed reference (data model, parsing pipeline, CLI output formats, known issues). Read `docs/reference.md` before non-trivial changes.

## Commands

Run everything **from the repo root**. Modules are imported by bare name (`import parser`, `import model`).

```sh
pytest -v                                   # all tests (make test)
pytest tests/test_parser.py::TestX::test_y  # single test
make coverage                               # coverage run + report
./details.py [--sc] [lang:]word             # look up a word (lang defaults to en)
./dict.py [--sc] lang                       # dictionary of a language with derivations
./dump.py [-v]                              # DB stats (-v is slow, ~20 s)
./dump.py -j > db.json                      # JSON export (make db.json; also copies to $UI_DIR/public, default ~/repos/etymolog-ui)
./parser.py file.pill                       # parse a single file (debugging grammar)
ETYMOLOG_LOG_LEVEL=DEBUG ./details.py ...   # logging verbosity (default WARNING)
```

## Architecture

- `lexer.py` / `parser.py`: PLY lexer and yacc grammar. `parser.load_db()` parses every `.pill` under `db/` and builds objects directly during parsing (no separate AST). Parser directives (`// SRC`, `// LANG`, `// NOSRC`, `// IGNORE`) mutate state in `config.py` (`default_lang`, `source`).
- `model.py`: `Word`, `Language`, `World` (registry of languages/tags), relationships `Derived` / `Equals` / `Related` (each with class-level `Table`/`Mirror` dicts) and `Union`.
- `details.py`, `dict.py`, `dump.py`: read-only consumers of the model. `dict.py` imports `load_db` via `dump`, and uses helpers from `details`.
- `parsetab.py` and `parser.out` are PLY-generated and gitignored. Delete them if the grammar changes oddly.

## Gotchas

- All state is global and mutable (`config`, class-level tables on model classes, `World.Languages`). Loading the DB twice in one process merges or duplicates state. Tests extend `tests/util.py::TestCase`, whose autouse fixture calls `reset_model()`. **If you add a new class-level table to the model, reset it in `reset_model()` too.**
- Words are case sensitive except in languages listed in `Language.CaseInsensitive` (`en`, `gr`), where the first-seen spelling wins.
- Module names `parser.py`, `dict.py`, `log.py`, `version.py`, `config.py` shadow or resemble stdlib names. Don't "fix" imports without checking.
- `version.py` shells out to `git rev-list` in its own directory; `rev_no` is `None` outside a git checkout.
- Known defects (cycles in data crash `details.py`/`dict.py`, non-deterministic export) are listed in `docs/reference.md` §9. `TODO.txt` has design decisions (e.g. no transitive equality, no `-` in word chars because it conflicts with `->`).
- `db.json` (~7 MB) is generated and gitignored. Don't edit it by hand.
- When fixing an issue, always remove it from `TODO.txt`.
