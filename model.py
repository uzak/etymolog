# Author   : Martin Užák <martin.uzak@gmail.com>
# Creation : 2020-03-28 21:11

"""
Object Model for the etymology project
"""

import config

class Entity:

    def __init__(self):
        self.comments = set()
        self.source = config.default_source

    def comment(self, text):
        if not text in self.comments:
            self.comments.add(text)
        return text


class Word(Entity):
    def __init__(self, value, lang):
        super().__init__()
        self.value = value
        self.rels = set()
        self.lang = lang

    def rel(self, rel_type, other):
        "get or create a relationship"
        rel = rel_type(self, other)
        self.rels.add(rel)
        other.rels.add(rel)
        return rel

    def __str__(self):
        return f"{self.lang.name}:{self.value}"
    __repr__ = __str__


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
            c.rel(rel_type, other)

    def __iter__(self):
        return iter(self.content)

    def __str__(self):
        return f"Group: {self.content}"
    __repr__ = __str__


class Relationship(Entity):
    Bidirectional = True

    def __init__(self, left, right):
        super().__init__()
        self.left = left
        self.right = right
        # XXX skip this?
        if isinstance(left, Word):
            left.rels.add(self)
        if isinstance(right, Word):
            right.rels.add(self)

    def __str__(self):
        return f"{self.Symbol}({self.left}, {self.right})"

    __repr__ = __str__

    def __hash__(self):
        return hash((self.Symbol, self.left, self.right))

    def __eq__(self, other):
        if (self.Symbol, self.left, self.right) == (other.Symbol, other.left, other.right):
            return True
        elif self.Bidirectional:
            if (self.Symbol, self.right, self.left) == (other.Symbol, other.left, other.right):
                return True
        return False


class Derive(Relationship):
    Bidirectional = False
    Symbol = "->"


class Equals(Relationship):
    Symbol = "="


class Related(Relationship):
    Symbol = "~"


class Union(Relationship):
    Symbol = "+"
    Bidirectional = False


class World:
    "Universal Mind"

    Languages = {}
    Relationships = {}

    @staticmethod
    def rel(rel_type, left: Word, right):
        if isinstance(rel_type, str):
            if rel_type == "=":
                rel_type = Equals
            elif rel_type == "->":
                rel_type = Derive
            elif rel_type == "~":
                rel_type = Related

        if isinstance(right, Group):
            for r in right:         # right is good; take all
                World.rel(rel_type, left, r)
        elif isinstance(left, Group):
            World.rel(rel_type, left.content[-1], right)  # only last from left
        else:
            key = f"{left}{rel_type.Symbol}{right}"
            rev_key = f"{right}{rel_type.Symbol}{left}"
            if key in World.Relationships:
                obj = World.Relationships[key]
            elif rel_type.Bidirectional and rev_key in World.Relationships:
                obj = World.Relationships[rev_key]
            else:
                obj = rel_type(left, right)
                World.Relationships[key] = obj
            return obj

    @staticmethod
    def rels(*rel_classes):
        result = set()
        for c in rel_classes:
            r = World.Relationships.get(c.Symbol, {})
            result.update(r.values())
        return result

    @staticmethod
    def lang(name):
        if name not in World.Languages:
            lang = Language(name)
            World.Languages[name] = lang
        return World.Languages[name]


class Language:

    def __init__(self, name):
        self.name = name
        self.words = {}

    def __iter__(self):
        return iter(self.words)

    def word(self, value):
        if value not in self.words:
            self.words[value] = word = Word(value, self)
            word.lang = self
        return self.words[value]

