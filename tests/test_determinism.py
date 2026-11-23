"""
Loading and export must not depend on os.walk / hash ordering
"""

from . util import *

import model
import parser


class TestDeterminism(TestCase):

    def test_get_pills_sorted(self, tmp_path):
        for name in ["b/z.pill", "b/a.pill", "a/m.pill", "c.pill", "x.txt"]:
            f = tmp_path / name
            f.parent.mkdir(exist_ok=True)
            f.write_text("")
        got = [str(p.relative_to(tmp_path)) for p in map(type(tmp_path), parser.get_pills(str(tmp_path)))]
        assert got == ["c.pill", "a/m.pill", "b/a.pill", "b/z.pill"]

    def test_word_json_sorted(self):
        parser.yacc.parse("t:w [z] [a] [m] #y #b")
        w = model.World.lang("t").get_word("w")
        assert w.to_json()["comments"] == ["a", "m", "z"]
        assert w.to_json()["tags"] == ["b", "y"]

    def test_relationships_sorted(self):
        parser.yacc.parse("c -> a")
        parser.yacc.parse("b = a")
        parser.yacc.parse("a -> b")
        pairs = [(r.left.key(), r.right.key()) for r in model.Derived.all()]
        assert pairs == [("en:a", "en:b"), ("en:c", "en:a")]
