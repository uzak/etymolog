# Author   : Martin Užák <martin.uzak@gmail.com>
# Creation : 2020-03-28 21:11

"""
Object Model for the etymology project
"""

import re
import config


class Entity:
    def __init__(self):
        self.comments = set()
        self.sources = set()
        if config.source:
            self.sources.add(config.source)

    def comment(self, text):
        if not text in self.comments:
            self.comments.add(text)
        return text


class Word(Entity):
    def __init__(self, value, lang):
        super().__init__()
        self.value = value
        self.lang = lang
        self.derived_from = set()
        self.derives = set()
        self.equals = set()
        self.related = set()
        self.unions = set()
        self.tags = set()
        self.in_unions = set()

    def add_tag(self, tag):
        tag = tag.lower()
        if tag not in World.Tags:
            World.Tags[tag] = set()
        World.Tags[tag].add(self)
        self.tags.add(tag)

    def __lt__(self, other):
        assert self.lang == other.lang
        return self.value < other.value

    def key(self):
        return f"{self.lang.name}:{self.value}"

    def label(self):
        value = re.sub(r'\d+$', '', self.value)
        return f"{self.lang.name}:{value}"

    def as_str(self, comments=True, unions=True, tags=False):
        _comments = ""
        _unions = ""
        _tags = ""
        if comments and self.comments:
            _comments = " "
            _comments += " ".join([f"[{c}]" for c in self.comments])
        if unions and self.unions:
            _unions = " "
            _unions += " ".join(map(lambda u: f"{{{u}}}", sorted(self.unions)))
        if tags and self.tags:
            _tags = " "
            _tags += " ".join([f"#{t}" for t in self.tags])
        return f"{self.key()}{_unions}{_comments}{_tags}"

    def to_json(self):
        return {
            "lang": self.lang.name,
            "value": self.value,
            "comments": list(self.comments),
            "sources": list(self.sources),
            "tags": list(self.tags)
        }

    def __str__(self):
        return self.as_str(comments=False)


class Union:
    Table = {}

    def __init__(self, word, *components):
        self.word = word
        self.components = components
        for word in self.components:
            word.in_unions.add(self)
        self.Table[str(self)] = self

    def __lt__(self, other):
        return self.word < other.word

    def __contains__(self, item):
        return item in self.components

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)

    def __str__(self):
        result = []
        for c in self.components:
            if c.lang == self.word.lang:
                result.append(c.value)
            else:
                result.append(c.key())
        return "+".join(result)
    __repr__ = __str__

    def to_json(self):
        return {
            "word": self.word.as_str(comments=False, unions=False),
            "components": [c.as_str(unions=False, comments=False) for c in self.components],
        }


class Group:
    "Group of words"

    def __init__(self, *args):
        self.content = []
        for a in args:
            if isinstance(a, Group):
                self.content.extend(a.content)
            else:
                self.content.append(a)

    def rel(self, rel_type, other):
        for c in self.content:
            rel_type.add(c, other)

    def __iter__(self):
        return iter(self.content)

    def __str__(self):
        return f"Group: {self.content}"
    __repr__ = __str__


class RelationshipMeta(type):
    def __new__(mcls, name, bases, attrs, **kw):
        attrs['Table'] = {}
        attrs['Mirror'] = {}
        return super().__new__(mcls, name, bases, attrs)


class Relationship(Entity, metaclass=RelationshipMeta):
    Bidirectional = True

    def __init__(self, left, right):
        super().__init__()
        self.left = left
        self.right = right

    @classmethod
    def add(cls, left, right, comment=None):
        if isinstance(right, Group):
            for r in right:                     # right is good; take all words
                cls.add(left, r, comment=comment)
        elif isinstance(left, Group):
            cls.add(left.content[-1], right, comment=comment)  # only last word from left
        else:
            return cls._add(left, right, comment=comment)

    @classmethod
    def _add(cls, left, right, comment=None):
        """get Relationship if it exists, otherwise add"""
        msg = f"Two relationships without a word in between? {left} - {right}"
        assert right is not None, msg
        obj = cls.get(left, right)
        key = (left.key(), right.key())
        if obj is None:
            obj = cls(left, right)
            cls.Table[key] = obj
            if cls.Bidirectional:
                cls.Mirror[key] = obj
        if comment:
            obj.comment(comment)
        return obj

    @classmethod
    def get(cls, left, right):
        key = (left.key(), right.key())
        rev_key = (right.key(), left.key())
        if key in cls.Table:
            return cls.Table[key]
        elif cls.Bidirectional and rev_key in cls.Mirror:
            return cls.Mirror[rev_key]

    @classmethod
    def cls_str(cls):
        return f"{cls.__name__} ({len(cls.Table)})"

    def __repr__(self):
        comments = f"[{', '.join(self.comments)}]" if self.comments else ""
        return f"({self.left} {self.Symbol}{comments} {self.right})"

    def __str__(self):
        return f"({self.left} {self.Symbol} {self.right})"

    def __hash__(self):
        return hash((self.Symbol, self.left, self.right))

    def __eq__(self, other):
        if (self.Symbol, self.left, self.right) == (other.Symbol, other.left, other.right):
            return True
        elif self.Bidirectional:
            if (self.Symbol, self.right, self.left) == (other.Symbol, other.left, other.right):
                return True
        return False

    def to_json(self):
        return {
            "left": self.left.as_str(comments=False, unions=False),
            "right": self.right.as_str(comments=False, unions=False),
            "comments": list(self.comments),
            "sources": list(self.sources),
        }

#XXX rename to Derivation, Equality, Relation?
class Derived(Relationship):
    Bidirectional = False
    Symbol = "->"

    def __init__(self, left: Word, right: Word):
        super().__init__(left, right)
        left.derives.add(self)
        right.derived_from.add(self)


class Equals(Relationship):
    Symbol = "="

    def __init__(self, left: Word, right: Word):
        super().__init__(left, right)
        left.equals.add(self)
        right.equals.add(self)


class Related(Relationship):
    Symbol = "~"

    def __init__(self, left: Word, right: Word):
        super().__init__(left, right)
        left.related.add(self)
        right.related.add(self)


class World:
    "Universal Mind"

    Tags = {}           # name: set(words)
    Languages = {}

    @staticmethod
    def lang(name):
        key = name.lower()
        if key not in World.Languages:
            lang = Language(name)
            World.Languages[key] = lang
        return World.Languages[key]


class Language:

    TranslationTable = {
        'gr': {
            'A': 'á',
            'O': 'ó',
            'Y': 'ý',
        },
        'sa': {
        },
        'sk': {
            'T': 'ť',
            'L': 'ľ',
            'S': 'š',
            'C': 'č',
            'Z': 'ž',
            'Y': 'ý',
            'I': 'í',
            'E': 'é',
            'A': 'á',
        }
    }

    def __init__(self, name):
        self.name = name
        self.words = {}

    def __iter__(self):
        return iter(self.words.values())

    def translate(self, word):
        translation_dict = Language.TranslationTable.get(self.name, {})
        return ''.join([translation_dict.get(char, char) for char in word])


    def add_word(self, value):
        value = self.translate(value)
        if value.lower() not in self.words:
            word = Word(value, self)
            self.words[value.lower()] = word
            word.lang = self
        else:
            # XXX hackish? add source if changed since last addition
            word = self.words[value.lower()]
            if config.source and config.source not in word.sources:
                word.sources.add(config.source)
        return self.words[value.lower()]

    def get_word(self, value, case_sensitive=False):
        word = self.words.get(value.lower())
        if word and case_sensitive and value != word.value:
            return
        return word

    def get_words(self, value, case_sensitive=False):
        # only match words that start with value and optionally continue
        # with a number
        matches = []
        for key, word in self.words.items():
            if key.startswith(value):
                postfix = key[len(value):]
                if not postfix or postfix.isdigit():
                    matches.append(word)
        if case_sensitive:
            matches = filter(lambda w: value != w.value, matches)
        return list(matches)

    def __eq__(self, other):
        return self.name == other.name

    def __len__(self):
        return len(self.words)

    def __str__(self):
        return f"Language: {self.name}"
