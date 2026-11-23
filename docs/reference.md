# etymolog — detailed reference

> Level 2 of 2. Start with [overview.md](overview.md) if you only need the gist.
>
> Written from a full source read plus experiments against the real DB, at commit `8e38b8b` plus uncommitted edits to `details.py`, `log.py`, `parser.py`, `tests/util.py` (2026-11-23). Facts in §9 are a snapshot; re-verify before relying on them.

## Contents

1. [Purpose and scope](#1-purpose-and-scope)
2. [Repository layout](#2-repository-layout)
3. [Setup, running, testing](#3-setup-running-testing)
4. [The `.pill` language](#4-the-pill-language)
5. [Data model (`model.py`)](#5-data-model-modelpy)
6. [Parsing pipeline](#6-parsing-pipeline)
7. [CLI tools and output formats](#7-cli-tools-and-output-formats)
8. [The dataset (`db/`)](#8-the-dataset-db)
9. [Known issues (snapshot from an audit)](#9-known-issues-snapshot-from-an-audit)
10. [Working on the code: practical notes](#10-working-on-the-code-practical-notes)

---

## 1. Purpose and scope

`etymolog` stores etymological knowledge as a graph of words and typed relationships, written by hand in a terse text format, and provides read-only tools to query it. It is a personal research tool, not a library or service:

- No packaging (`pyproject.toml`/`setup.py` absent), no install step, no versioned API.
- No network, no database. Everything is loaded from text files into memory on every run (~0.5 s for the full DB).
- No authentication, no untrusted input handling concerns beyond "the `.pill` files are trusted".
- Output is for humans (terminal text) or for the sibling UI project (JSON).

Out of scope: editing tools (data is edited by hand in `.pill` files), search/fuzzy lookup (listed in `TODO.txt`), persistence, caching.

## 2. Repository layout

| Path | Role |
|---|---|
| `lexer.py` | PLY lexer; defines the token set. Run directly for a token dump (`lex.runmain()`). |
| `parser.py` | PLY yacc grammar + semantic actions that build the model; `parse_file`, `get_pills`, `load_db`. Run directly with a file path to parse one file. |
| `model.py` | Object model: `Entity`, `Word`, `Union`, `Group`, `Relationship` (+ `Derived`, `Equals`, `Related`), `World`, `Language`. |
| `config.py` | Two mutable globals: `default_lang = "en"`, `source = None`. Mutated by the parser (directives) during a load. |
| `details.py` | CLI: show one word's parents, translations, unions, descendants. Also exports helpers (`translations_str`, …) reused by `dict.py`. |
| `dict.py` | CLI: dictionary listing for one language. |
| `dump.py` | CLI: statistics, or JSON export (`-j`). |
| `log.py` | Logging setup. Level from env `ETYMOLOG_LOG_LEVEL` (default `WARNING`; the env-var support is an uncommitted change — previously hard-coded `DEBUG`). |
| `version.py` | `rev_no` = number of git commits (`git rev-list --count HEAD`, run in the module's directory), embedded in the JSON export. `None` if git is unavailable. |
| `Makefile` | Targets `test`, `coverage`, `db.json`, `count_slovak_words`, `clean`. |
| `README.md` | Author's description of the grammar and tools (accurate on grammar; see §9 for places where behaviour differs). |
| `TODO.txt` | Author's backlog and resolved design decisions. |
| `requirements.txt` | `ply`, `pytest` (unpinned). `coverage` is used by `make coverage` but not listed. |
| `basic.pill` | A small sample at the repo root. **Not loaded** by `load_db()` (which only walks `db/`); parse it explicitly with `./parser.py basic.pill`. |
| `db/**.pill` | The dataset (§8). |
| `tests/` | pytest suite: `test_parser.py` (482 lines), `test_model.py`, `util.py` (`TestCase` base class that resets global model state around every test). |
| `parser.out`, `parsetab.py` | PLY-generated artefacts, written next to `parser.py`; gitignored. |

Import graph (bare-name imports, so cwd/rootdir must be the repo root):

```
lexer  -> log
parser -> model, config, lexer(tokens), log, ply.yacc
model  -> config
details-> config, model, parser(load_db)
dict   -> model, details, dump(load_db re-export)   # dump -> version -> git
dump   -> model, version, parser(load_db)
```

## 3. Setup, running, testing

```sh
python3 -m venv .venv && .venv/bin/pip install ply pytest coverage
.venv/bin/python -m pytest -q          # expected: 68 passed
.venv/bin/python details.py sa:tr
```

- The scripts have `#!/usr/bin/env python3` shebangs; `./details.py …` works only if that `python3` has `ply`.
- Tested with Python 3.14.4, PLY 3.11, pytest 9.2.
- `make test` = `pytest -v`; `make coverage` = coverage with branch tracking; `make db.json` = `./dump.py -j > db.json` then copies to `${UI_DIR}/public/` (default `~/repos/etymolog-ui`; fails if that directory does not exist).
- Coverage at audit time: 49% overall. `details.py`, `dict.py`, `dump.py`, `version.py` are at 0% (no CLI tests). `parser.py` 76%, `model.py` 81%.
- Environment variable: `ETYMOLOG_LOG_LEVEL=DEBUG` (or INFO, …) to see parser debug messages.

## 4. The `.pill` language

Files are UTF-8 text (read with the locale default encoding — see §9). **One statement per line**; each line is parsed independently by `yacc.parse(line)`. Blank lines are legal (empty expression). Spaces and tabs between tokens are ignored; multiple words are joined with a single space.

### 4.1 Tokens (`lexer.py`)

| Token | Pattern | Meaning |
|---|---|---|
| `TOKEN` | `[\w'/\.]+` | A word fragment: letters, digits, `_`, `'`, `/`, `.`. **Hyphen is illegal** (conflicts with `->`; the author decided "no"). |
| `LANG` | `\w+\s*:` | Language prefix, e.g. `sa:` (colon stripped). Takes priority over `TOKEN`. |
| `DERIVE` | `->` | Directional derivation. |
| `EQUALS` | `=` | Translation / equivalence (symmetric). |
| `RELATED` | `~` | Generic relation, "somehow related" (symmetric). |
| `SEP` | `,` | Group separator. |
| `PLUS` | `+` | Separator inside a union. |
| `LUNION` / `RUNION` | `{` / `}` | Union delimiters. |
| `COMMENT` | `\[.*?\]` | Meaningful comment (stored). Brackets stripped. |
| `PAREN` | `\(.*?\)` | Embedded comment, **discarded**. Parentheses stripped. |
| `TAG` | `#\s*\w+` | Tag; stored lowercase. |
| `META` | `//.*` | End-of-line comment or parser directive. |

Any other character (e.g. `!`, `-`, `:` outside a language prefix) raises `SyntaxError("Illegal character …")`.

### 4.2 Words and languages

```
ship                 # word in default language (config.default_lang, "en" unless changed)
en:ship              # explicit language
big ship (of wood)   # one composite word "big ship"; the parenthesised part is dropped
sa:sveta asva        # composite Sanskrit word "sveta asva"
```

- Only the **first** word of a composite may carry a language; `en:big de:Schiff` is a syntax error.
- Language names are free-form identifiers (`sa`, `lat`, `gr`, `slavic`, `old_church_slavonic`…). **Any new name silently creates a new language** — there is no registry, so typos create phantom languages.
- Lookup is case sensitive, except in `Language.CaseInsensitive` (`en`, `gr`), where the spelling **first seen** during the load is the stored `value`. Keys are produced by `Language.fold`.
- **Homonym numbering:** a trailing number distinguishes homonyms (`ie:az1`, `ie:az2`). `Word.label()` strips trailing digits for display; `Language.get_words("az")` returns `az`, `az1`, `az2`… (prefix + optional digits only).
- **Character translation** (`Language.TranslationTable`, applied when a word is added and when the CLI looks one up): for `sk`, capital `T L S C Z Y I E A` become `ť ľ š č ž ý í é á`; for `gr`, `A O Y` become `á ó ý`; `sa` has an (empty) table. This is how accented letters are typed in ASCII. The lookup key is the language name **exactly as first created** (`sk`, not `SK`).
- Sanskrit data uses a Harvard-Kyoto-like ASCII transliteration where case is meaningful (`A`=ā, `T`=ṭ, `R`=ṛ …), and `sa` is case sensitive.

### 4.3 Groups

`boat, ship, steam trawler` — comma-separated words (or sub-expressions) form a `Group`. Groups matter inside relationships:

- Group on the **right** of a relationship: the relationship is created with **every** member.
- Group on the **left**: only the **last** member is used.

`SEP` binds tighter than the relationship operators, so `a -> b, c` means `a -> (b, c)`.

### 4.4 Relationships

| Syntax | Class | Direction | Notes |
|---|---|---|---|
| `a -> b` | `Derived` | directed (a gave rise to b) | |
| `a = b` | `Equals` | symmetric | translation/same meaning |
| `a ~ b` | `Related` | symmetric | vague connection |

- Chains are **left-associative** and each relationship "returns" its **right-most** word, so `sa:Pas -> sa:Pasa -> lat:pax -> pacify` creates three `Derived` edges (`Pas→Pasa`, `Pasa→pax`, `pax→pacify`), and `sa:Pas -> sa:Pasa = rope, cord` creates `Pas→Pasa` plus `Pasa=rope`, `Pasa=cord`.
- Operators can be mixed on one line.
- Equal relationships are de-duplicated (keyed by `(left.key(), right.key())`; for symmetric types the reverse key also matches).
- Parser rejects `a -> a` (same word object, case-insensitive) and a right side that evaluates to nothing (`a ->`) with `ValueError`/`SyntaxError`. (A self-loop via a group, `a -> a, b`, is *not* caught.)

### 4.5 Comments on words and relationships

```
boat [means of transport on water]            # comment on the word `boat`
en:pyre ~[person turning red] sk:pýriť sa     # comment on the relationship (bracket right after the operator)
a [b] [c]                                     # several comments allowed
```

A `[...]` directly after a word attaches to that word; directly after an operator it attaches to that relationship. Comments are stored as sets of strings (unordered).

### 4.6 Unions (compounds)

```
sa:vi+sa {vi+sa}                  # (README example)  
sa:svetAsvatara {sveta+asva+tara}
slavic:Dažbog {sa:dadati+bog}     # components may carry explicit languages
azru {az+ru} [noise (ru) that reaches (az)] = to tear
```

`word {c1+c2+…}` records that `word` is composed of the components. Components default to the **language of the union word** (the parser temporarily switches `config.default_lang`); each component becomes a normal word in the DB. A `Union` is attached to `word.unions` and to each component's `in_unions`. Comments/tags/relationships may follow the union on the same line.

### 4.7 Tags

`Thames #river #UK`, `sa:danu -> danube #river` — a tag attaches to the **word immediately before it**. Stored lowercase in `Word.tags` and the global index `World.Tags` (tag → set of words). Tags in the shipped DB: planet, city, island, god, river, water, geo, mountain, mount, town.

### 4.8 Directives (`// DIRECTIVE`)

A `META` token is either a plain comment (ignored) or a directive recognised by prefix (case-sensitive) on the stripped text:

| Directive | Effect |
|---|---|
| `// SRC <text>` | Sets `config.source` (usually a URL or book title). Every `Entity` created afterwards records it; an empty `SRC` clears it. |
| `// NOSRC` | Clears `config.source`. |
| `// LANG <code>` | Sets the default language for words without a prefix. |
| `// IGNORE` | Stops processing the rest of the file. |

All directive state is reset at the end of each file (`finish_file()`: `source=None`, `default_lang=en`). README says directives must occupy a whole line, but the grammar also accepts them after a statement (`expression META`), so a trailing comment beginning with `SRC`/`LANG`/`IGNORE` would act as a directive.

### 4.9 Complete small example

```
// SRC Comparative etymological Dictionary of classical Indo-European languages
// LANG en
ie:az1 [start (an) of an approach (z)] = to reach, to obtain
ie:az1 -> sa:az/aznoti = to reach, to get, to obtain
sa:az -> sa:azman [instrument made of stone] = stone, rock
sa:az -> sa:azani = thunderbolt
sa:az -> azru {az+ru} [noise (ru) that reaches (az)] = to tear
lat:donare -> donate, donor, donation
```

Note that in the last line `donate` etc. are English words (default language) and each gets a `lat:donare → en:…` edge (group on the right).

## 5. Data model (`model.py`)

All of these are **process-wide singletons held in class attributes**.

```
World
  Languages: dict[lowercase name -> Language]
  Tags:      dict[tag -> set[Word]]
  World.lang(name) -> Language (creates on first use; keeps first-seen name casing)

Language(name)
  words: dict[value.lower() -> Word]
  add_word(value)      # applies TranslationTable; returns existing Word if lower() key exists (adds config.source to it if new)
  get_word(value, case_sensitive=False)
  get_words(value)     # prefix + optional digits (homonyms)
  translate(value)

Entity                 # base: comments:set[str], sources:set[str]; sources seeded from config.source at construction
  Word(value, lang)
    derived_from: set[Derived]      derives: set[Derived]
    equals: set[Equals]             related: set[Related]
    unions: set[Union]              in_unions: set[Union]
    tags: set[str]
    key() -> "lang:value"           label() -> key without trailing digits
    as_str(comments, unions, tags)  to_json()
  Relationship(left, right)         # metaclass gives each subclass its own Table and Mirror dicts
    Derived  (Symbol "->", directed)
    Equals   (Symbol "=",  symmetric)
    Related  (Symbol "~",  symmetric)
    add(left, right, comment=None)  # classmethod; expands Groups; get-or-create; returns the Relationship (or None for Group inputs)
    Table: {(left.key(), right.key()): rel}

Union(word, *components)   # not an Entity; Union.Table[str(self)] = self; str = "c1+c2" (component shown as lang:value if language differs from the word's)
Group(*items)              # flat list of words, used only during parsing
```

Notes:

- Word identity is Python object identity; the same `Word` object is shared by all statements mentioning it.
- `Relationship.Mirror` holds the same keys as `Table` for symmetric types (used by `get` to find `(b,a)` when `(a,b)` exists); for `Derived` it is unused.
- JSON/`as_str` refer to words by the string `lang:value`.

## 6. Parsing pipeline

```
load_db(db_dir=<repo>/db)
  for fn in get_pills(db_dir)            # os.walk, *.pill, unsorted order
    parse_file(fn)
      with _parse_context():             # always calls finish_file() at the end
        for lineno, line in enumerate(file.readlines(), 1):
            yacc.parse(line)             # lexer + grammar actions mutate model/config directly
            # IgnoreFile -> stop file; SyntaxError/ValueError -> re-raised as SyntaxError("<file>:<line>: <msg>")
```

- Parsing is **fail-fast and all-or-nothing**: the first bad line raises and aborts the whole `load_db()`; partially loaded state remains in memory.
- Grammar actions build the model immediately (no AST). Order of lines and files therefore affects results (first-seen spelling, language name casing, which source is recorded first).
- `yacc = ply.yacc.yacc()` runs at import time of `parser.py` and (re)generates `parser.out`/`parsetab.py` beside it. The grammar currently reports no PLY conflicts/warnings.
- The precedence table at the bottom of `parser.py` is unconventional (it lists nearly all tokens); `SEP` binds tighter than relationship operators, which is what makes group semantics in §4.3 work.
- Other exceptions (e.g. `AssertionError`, `AttributeError`) are **not** wrapped and carry no file/line information.

## 7. CLI tools and output formats

All tools call `load_db()` first, so each invocation re-parses the entire DB.

### `details.py [--sc] [lang:]word`

- Splits on `:` (exactly one colon allowed; `a:b:c` crashes). Without a language uses `config.default_lang` (`en`).
- Applies `Language.translate`, then `get_words` (exact match for case-sensitive languages) (prefix + optional digits). Prints a block per match; prints `` `lang:word` not found `` (exit code 0) if none.
- `--sc` suppresses comments.
- Block layout (indentation is 4 spaces; cosmetic details are slightly inconsistent):

```
      * / ancestors chain printed first (recursively), each with its translations and union
      | [relationship comments]
 => sa:tr                         # the word itself (with comments, tags)
    = en:stars, to cross over     # translations (Equals), words with comments listed separately
    + sa:rAtrI {ra+tr} = en:night # unions this word is a component of
    -> sa:str = en:star, …        # descendants (Derived), recursively indented
      -> sa:tara = en:crossing
    ~ …                           # Related
```

### `dict.py [--sc] lang`

Prints `Dictionary for ``lang`` (N items):` then, for every word of that language sorted with `locale.strxfrm` (so the process locale affects order; `locale.setlocale(LC_ALL, '')` runs at import): `* word`, its translations/related (`=`/`~` lines), its comments in brackets, and its ancestors, one line per derivation path (`-> sa:bheda -> …`; a word with several parents gets several lines, sorted). An unknown language prints an empty dictionary (and creates the language).

### `dump.py [-v] [-j]`

- default: language list with word counts (largest first), `Union (n)`, `Relationship Derived|Equals|Related (n)`, tag list. `-v` also lists every union/relationship (quadratic de-dup; ~20 s on the full DB).
- `-j`: JSON to stdout:

```json
{
  "words": [{"lang": "sa", "value": "tr", "comments": [], "sources": [], "tags": []}, …],
  "relationships": {
    "derived": [{"left": "sa:str", "right": "sa:tara", "comments": [], "sources": []}, …],
    "related": […],
    "equals":  […]
  },
  "unions": [{"word": "sa:rAtrI", "components": ["sa:ra", "sa:tr"]}, …],
  "version": 97
}
```

`version` is the git commit count (`version.rev_no`). List-valued fields come from Python sets, so their order is not stable between runs.

### `parser.py <file>` / `lexer.py`

`./parser.py some.pill` parses one file (errors surface as exceptions, no output on success). `./lexer.py` uses PLY's `runmain` (tokenises stdin/file for debugging).

## 8. The dataset (`db/`)

- ~94 `.pill` files in subfolders named after the **source**: `james_cooper/` (many small topic files), `rendlich_franco/` (alphabetical, largely Slovak ↔ Sanskrit), `vediccafe/` (articles), `swami_paramarthananda/`, plus loose files (`english`, `slovak`, `portuguese`, `vedanta`, `rene_guenon`, `noologie.de`, `the_three_ages_of_atlantis`, …).
- Typical file starts with `// SRC <book or URL>` and optionally `// LANG xx`.
- At audit time: 14,253 words; ~93 languages (largest: en 6457, sa 2591, lat 1530, gr 1346, sk 845, ie 640, he 267, ar 99); 5,869 derived, 11,425 equals, 587 related relationships; 573 unions in the table; 10 tags.
- Content spans mainstream etymology and speculative/fringe comparative claims from the sources listed; **the model has no field distinguishing the two** other than `sources`. Treat output as "what source X claims", not as established fact.
- No LICENSE file exists in the repo; the data appears to transcribe third-party works.
- 37 languages contain exactly one word (several look like typos or aliases: `ske`, `nahualt`, `summerian`, `jp`/`ja`, `kurdisch`/`kurdish`, `german`/`de`, `greek`/`gr`).

## 9. Known issues (snapshot from an audit)

Verified by experiment unless marked *(code reading)*. Ordered by impact.

**Data integrity**
1. ~~Case-folding merges distinct words.~~ Fixed (#3): only `en` and `gr` fold case.
2. ~~Unions lost.~~ Fixed (#4): unions are identified by word and components.
3. ~~Relationship provenance dropped.~~ Fixed (#5): re-asserting a relationship under a new `SRC` adds the source.
4. **Cycles are accepted.** The DB contains `he:adam -> he:adamah -> he:adam`; `a -> a, b` creates a self-loop (the self-reference check compares against a `Group`).
5. **Phantom languages.** Language names are never validated.

**Crashes / robustness**
6. `details.py he:adam` and `dict.py he` → `RecursionError` (no visited set in `details.parents`, `details.derived_details`, `dict.derived_chain`). Ancestors are also printed once per path (exponential in dense DAGs) *(code reading)*.
7. ~~`version.py` needs a git cwd.~~ Fixed (#6): runs git in its own directory; `rev_no` is `None` on failure.
8. ~~`a -> [c]` raised a bare `AssertionError`.~~ Fixed (#6): `_add` raises `ValueError` (reported with file:line).
9. `details.py a:b:c` → `ValueError` (unpack).
10. Directive parsing is prefix-based: `// LANG   sa` sets language `"  sa"`; `// LANG` sets `""`; `// SRCfoo` sets source `"oo"`.
11. `open(fn)` without `encoding=` *(code reading)*; the DB is valid UTF-8 without BOMs/CRLF today.

**Reproducibility**
12. `get_pills` is unsorted `os.walk`; reversing file order changed 412 word keys and a language name (`Toltec` vs `toltec`).
13. `dump -j` output differs across runs (`PYTHONHASHSEED`) because sets are serialised with `list(set)`.
14. Lexer line numbers in errors are cumulative across files (`at line: 9` for line 1); the `file:line` prefix added by `parse_file` is the reliable one.

**Smaller defects**
15. `Language.get_words(case_sensitive=True)` filter is inverted (`model.py:333-335`); currently unused.
16. `Relationship.__hash__` ignores symmetry (`Equals(a,b) == Equals(b,a)` but hashes differ) and `__eq__` raises `AttributeError` for foreign types.
17. `details.py:81`: `not oneline and tx.rel.comments or tx.word.comments` — probably missing parentheses.
18. `dump -v` is ~40× slower than non-verbose (list membership test in `dump.py:26-29`).
19. Unknown language on the CLI exits 0 and creates the language as a side effect.
20. `Makefile`'s `db.json` rule has no `.DELETE_ON_ERROR`; a failed dump may leave an empty `db.json` that `make` considers up to date *(code reading)*.

## 10. Working on the code: practical notes

- **Tests** subclass `tests.util.TestCase`, whose autouse fixture calls `reset_model()` (reassigns each class-level `Table`/`Mirror`, `World.Languages`, `World.Tags`). If you add new global state to `model.py`, add it to `reset_model()` too. Tests drive the parser with `parser.yacc.parse("line")` and assert on `model.World`.
- There are **no CLI tests**; if you change `details.py`/`dict.py`/`dump.py`, verify manually against the real DB (`./details.py sa:tr`, `./dict.py sk`, `./dump.py -j | python -m json.tool >/dev/null`).
- Adding a language-specific character mapping = edit `Language.TranslationTable` in `model.py` (keyed by the exact language name).
- Adding syntax = edit `lexer.py` (tokens) and `parser.py` (rules + `precedence`); delete stale `parser.out`/`parsetab.py` if PLY seems to use an old table.
- Design decisions already taken (from `TODO.txt`): relationships are **not** transitive; no `a = b, c = d` expression groups; no implicit language propagation inside groups; `-` is not allowed in words.
- Open backlog (from `TODO.txt`): verb forms, language-specific case rules, language groups, showing union derivations, lookup/fuzzy search, Redis caching, removing `Relationship.Table`, multiline relationships.
- Suggested fix priority from the audit: (1) visited-set + cycle/self-loop rejection, (2) sorted file order and sorted JSON lists, (3) `Union.Table` keyed by `(word.key(), str(union))`, (4) make `version.py` robust (git `-C <script dir>`, fallback), (5) per-language case sensitivity, (6) stricter directive parsing, (7) CLI tests.
