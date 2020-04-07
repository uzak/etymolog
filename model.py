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
        self.lang = lang
        self.derived_from = set()
        self.derives = set()
        self.equals = set()
        self.related = set()
        self.unions = set()
        self.tags = set()

    def add_tag(self, tag):
        tag = tag.lower()         # XXX ok?
        if tag not in World.Tags:
            World.Tags[tag] = set()
        World.Tags[tag].add(self)
        self.tags.add(tag)

    def __lt__(self, other):
        assert self.lang == other.lang
        return self.value < other.value

    def key(self):
        if self.comments:
            comments = " ".join([f"[{c}]" for c in self.comments])
            return f"{self.lang.name}:{self.value} {comments}"
        return f"{self.lang.name}:{self.value}"

    def __repr__(self):
        return self.key()

    def __str__(self):
        def union_to_str(union): #XXX hackish hack
            if self.lang == union.left.lang:
                left = union.left.value
            else:
                left = str(union.left)
            if self.lang == union.right.lang:
                right = union.right.value
            else:
                right = str(union.right)
            return f"{left}{Union.Symbol}{right}"
        self_str = f"{self.lang.name}:{self.value}"
        if self.unions:
            unions = ", ".join(map(union_to_str, sorted(self.unions)))
            return f"{self_str} [{unions}]"
        return self_str


class Union(Word):
    Symbol = "+"
    Table = {}

    def __init__(self, left: Word, right: Word):
        self.left = left
        self.right = right
        key = str(self)
        super().__init__(key, left.lang)
        self.Table[(left, right)] = self

    def register_composite_word(self):
        key = f"{self.left.value}{self.right.value}"
        lang = self.left.lang
        word = lang.get_word(key)
        if not word:
            word = lang.add_word(key)
        word.unions.add(self)

    def __str__(self):
        key = f"{self.left}{Union.Symbol}{self.right}"
        return key

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
            for r in right:         # right is good; take all
                cls.add(left, r, comment=comment)
        elif isinstance(left, Group):
            cls.add(left.content[-1], right, comment=comment)  # only last from left
        else:
            return cls._add(left, right, comment=comment)

    @classmethod
    def _add(cls, left, right, comment=None):
        """get Relationship if it exists, otherwise add"""
        obj = cls.get(left, right)
        key = (left.key(), right.key())
        rev_key = (right.key(), left.key())
        if obj is None:
            obj = cls(left, right)
            cls.Table[key] = obj
            if cls.Bidirectional:
                cls.Table[rev_key] = obj
        if comment:
            obj.comment(comment)
        return obj

    @classmethod
    def get(cls, left, right):
        key = (left.key(), right.key())
        rev_key = (right.key(), left.key())
        if key in cls.Table:
            return cls.Table[key]
        elif cls.Bidirectional and rev_key in cls.Table:
            return cls.Table[rev_key]

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


class Derived(Relationship):
    Bidirectional = False
    Symbol = "->"

    def __init__(self, left: Word, right: Word):
        super().__init__(left, right)
        #print(f"Setting derives for {left} to {id(self)}")
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
        if name not in World.Languages:
            lang = Language(name)
            World.Languages[name] = lang
        return World.Languages[name]


class Language:

    def __init__(self, name):
        self.name = name
        self._words = {}

    def __iter__(self):
        return iter(self._words.values())

    def add_word(self, value, word=None):
        if value.lower() not in self._words:
            word = word or Word(value, self)
            self._words[value.lower()] = word
            word.lang = self
        return self._words[value.lower()]

    def get_word(self, value, case_sensitive=False):
        word = self._words.get(value.lower())
        if word and case_sensitive and value != word.value:
            return
        return word

    def del_word(self, word):
        if word.value.lower() in self._words:
            del self._words[word.value.lower()]

    def concat(self, w1, w2):
        if w1.lang != w2.lang:
            if w2.lang.name == config.default_lang:
                w2.lang.del_word(w2)
                w2.lang = w1.lang
            else:
                raise ValueError(f"Can't concat {w1} and {w2}")
        w1.lang.del_word(w1)
        w2.lang.del_word(w2)
        return self.add_word(f"{w1.value} {w2.value}")

    def __eq__(self, other):
        return self.name == other.name

    def __len__(self):
        return len(self._words)

    def __str__(self):
        return f"Language: {self.name}"
