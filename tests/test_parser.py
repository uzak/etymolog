# Author   : Martin Užák <martin.uzak@gmail.com>
# Creation : 2020-03-28 20:49

"""
test the parser, obviously
"""

from . util import *

import pytest

import model
import parser
import config


class TestWords(TestCase):

    def test_basic_default_lang(self):
        l = config.default_lang
        parser.yacc.parse("w")
        w = word("w", l)
        assert w.value == "w"
        assert w.lang.name == l
        assert_total_word(config.default_lang, 1)

    def test_basic(self):
        parser.yacc.parse("test:w")
        w = word("w", "test")
        assert w.value == "w"
        assert w.lang.name == "test"
        assert_total_word("test", 1)

    def test_composite_implicit_lang(self):
        parser.yacc.parse("w z")
        w = word("w z")
        assert w.value == "w z"
        assert w.lang.name == config.default_lang
        assert_total_word(config.default_lang, 1)

    def test_composite_explicit_lang(self):
        parser.yacc.parse("test:w z")
        w = word("w z", "test")
        assert w.value == "w z"
        assert w.lang.name == "test"
        assert_total_word("test", 1)
        assert_total_word(config.default_lang, 0)

    def test_composite_different_lang(self):
        with pytest.raises(SyntaxError):
            parser.yacc.parse("en:big de:Schiff")

    def test_composite_explicit_lang_both(self):
        with pytest.raises(SyntaxError):
            parser.yacc.parse("en:big en:ship")

    def test_invalid_lang(self):
        with pytest.raises(SyntaxError):
            parser.yacc.parse(".lang:word")

class TestGroups(TestCase):

    def test_group(self):
        parser.yacc.parse("w1, w2, w3")
        l = lang(config.default_lang)
        assert l.get_word("w1")
        assert l.get_word("w2")
        assert l.get_word("w3")
        word("w1", l.name).value == "w1"
        word("w1", l.name).lang.name == config.default_lang
        word("w2", l.name).value == "w2"
        word("w2", l.name).lang.name == config.default_lang
        word("w3", l.name).value == "w3"
        word("w3", l.name).lang.name == config.default_lang
        assert_total_word(config.default_lang, 3)


class TestRelationships(TestCase):

    def test_rel_derived(self):
        parser.yacc.parse("test:w1 -> w2")
        assert_derived_lr("w1", "w2", ll="test")

    def test_rel_derived_triple(self):
        parser.yacc.parse("w1 -> w2 -> w3")
        assert_derived_lr("w1", "w2")
        assert_derived_lr("w2", "w3")

    def test_rel_related(self):
        parser.yacc.parse("test:w1 ~ w2 ~ w3")
        assert_related_lr("w1", "w2", ll="test")

    def test_rel_related_group(self):
        parser.yacc.parse("w1 ~ w2, w3")
        assert_related_lr("w1", "w2")
        assert_related_lr("w1", "w3")

    def test_rel_derived_equals(self):
        parser.yacc.parse("w1 -> w2 = w3")
        assert_derived_lr("w1", "w2")
        assert_equals_lr("w2", "w3")

    def test_rel_groups(self):
        parser.yacc.parse("w1,w2 -> w3")    # on the left only right-most group member is taken
        assert_derived_lr("w2", "w3")
        assert_total_rels(1)

    def test_rel_rel_groups2(self):
        parser.yacc.parse("w2 -> w3,w4")
        assert_derived_lr("w2", "w3")
        assert_derived_lr("w2", "w4")
        assert_total_rels(2)

    def test_rel_rel_groups3(self):
        parser.yacc.parse("w1,w2 -> w3,w4")
        assert_derived_lr("w2", "w3")
        assert_derived_lr("w2", "w4")
        assert_total_rels(2)

    def test_word_word_word_rule(self):
        parser.yacc.parse("w1 = w2 w3, w4")
        assert_equals_lr("w1", "w2 w3")
        assert_equals_lr("w1", "w4")
        assert_total_rels(4)            # 2x2 because Equals is bidirectional
        assert_total_word(config.default_lang, 3)

    def test_rel_rel_complex(self):
        parser.yacc.parse("w1 -> w2,w3 = w5 -> w6")
        assert_derived_lr("w1", "w2")
        assert_derived_lr("w1", "w3")
        assert_equals_lr("w3", "w5")
        assert_derived_lr("w5", "w6")
        assert_total_rels(5)

    def test_rel_rel_complex2(self):
        parser.yacc.parse("w1 ~ w2 = w3 -> w4, w5")
        assert_related_lr("w1", "w2")
        assert_equals_lr("w2", "w3")
        assert_derived_lr("w3", "w4")
        assert_derived_lr("w3", "w5")
        assert_total_rels(6)

    def test_rel_rel_complex3(self):
        parser.yacc.parse("w1 ~ w2, w3 = w4 -> w5")
        assert_related_lr("w1", "w2")
        assert_related_lr("w1", "w3")
        assert_equals_lr("w3", "w4")
        assert_derived_lr("w4", "w5")
        assert_total_rels(7)

    def test_rel_rel_complex4(self):
        parser.yacc.parse("w1 -> w2, w3 = w4 ~ w5")
        assert_derived_lr("w1", "w2")
        assert_derived_lr("w1", "w3")
        assert_equals_lr("w3", "w4")
        assert_related_lr("w4", "w5")
        assert_total_rels(6)

    def test_rel_rel_complex5(self):
        parser.yacc.parse("w0, w1 = w2 -> w3 ~ w4, w5")
        assert_equals_lr("w1", "w2")
        assert_equals_lr("w2", "w1")
        assert_derived_lr("w2", "w3")
        assert_related_lr("w3", "w4")
        assert_related_lr("w4", "w3")
        assert_related_lr("w3", "w5")
        assert_related_lr("w5", "w3")
        assert_total_rels(7)

    def test_rel_bidirectional(self):
        parser.yacc.parse("w1 = w2")
        assert_equals_lr("w1", "w2")
        assert_equals_lr("w2", "w1")
        parser.yacc.parse("w2 = w1")
        assert_total_rels(2)

    def test_circular_equals(self):
        with pytest.raises(ValueError):
            parser.yacc.parse("a = a")

    def test_circular_derive(self):
        with pytest.raises(ValueError):
            parser.yacc.parse("a -> a")

    def test_circular_related(self):
        with pytest.raises(ValueError):
            parser.yacc.parse("a ~ a")


class TestComments(TestCase):

    def test_comment(self):
        comment = "dynasty in which Lord Rama took birth"
        parser.yacc.parse(f"sa:Raghu [{comment}]")
        w = word("Raghu", "sa")
        assert comment in w.comments
        assert_total_word("sa", 1)

    def test_derivation_comment(self):
        comment = "direction, where the sun first appears "
        parser.yacc.parse(f"sa:purva = [{comment}] east")
        assert lang("sa").get_word("purva")
        purva = word("purva", "sa")
        east = word("east", config.default_lang)
        r = model.Equals.get(purva, east)
        assert comment in r.comments
        assert_total_word("sa", 1)
        assert_total_word(config.default_lang, 1)

    def test_quotes_in_comment(self):
        comment = 'b "c" d'
        parser.yacc.parse(f'a [{comment}]')
        a = word("a")
        assert comment in a.comments

    def test_multiple(self):
        with pytest.raises(SyntaxError):
            parser.yacc.parse("a ->[c1][c2] b")

    def test_multiple_word(self):
        with pytest.raises(SyntaxError):
            parser.yacc.parse("[c1][c2]")

    def test_multiple_word2(self):
        parser.yacc.parse("a -> b [c1][c2]")
        b = lang().get_word("b")
        assert "c1" in b.comments
        assert "c2" in b.comments

    def test_circular_equals(self):
        with pytest.raises(ValueError):
            parser.yacc.parse("a =[c1] a")

    def test_circular_derive(self):
        with pytest.raises(ValueError):
            parser.yacc.parse("a ->[c1] a")

    def test_circular_related(self):
        with pytest.raises(ValueError):
            parser.yacc.parse("a ~[c1] a")

    def test_rel_comment_group(self):
        parser.yacc.parse("a ->[b] c, d, e ")
        left = word("a")
        assert left
        for right_value in "cde":
            right = word(right_value)
            assert right
            rel = model.Derived.Table[(str(left), str(right))]
            assert rel
            assert "b" in rel.comments
        assert_total_word(config.default_lang, 4)


class TestUnion(TestCase):

    def test_union(self):
        parser.yacc.parse("value {a + b+c+d}")
        l = lang()
        value = l.get_word("value")
        assert value is not None
        assert len(value.unions) == 1
        u = get_union(value)
        assert l.get_word("a") in u
        assert l.get_word("b") in u
        assert l.get_word("c") in u
        assert l.get_word("d") in u
        assert str(u) == "a+b+c+d"

    def test_union_diff_lang(self):
        parser.yacc.parse("a {de:b + sk:c}")
        de = lang("de")
        sk = lang("sk")
        b = de.get_word("b")
        c = sk.get_word("c")
        assert b is not None
        assert c is not None
        a = lang().get_word("a")
        assert len(a.unions) == 1
        u = get_union(a)
        assert b in u
        assert c in u
        assert str(u) == "de:b+sk:c"

    def test_union_diff_lang2(self):
        parser.yacc.parse("a {b + test:c}")
        a = lang().get_word("a")
        b = lang().get_word("b")
        c = lang("test").get_word("c")
        assert a is not None
        assert b is not None
        assert c is not None
        assert len(a.unions) == 1
        u = get_union(a)
        assert b in u
        assert c in u
        assert str(u) == "b+test:c"

    def test_union_diff_lang3(self):
        parser.yacc.parse("a {test:b + c}")
        a = lang().get_word("a")
        b = lang("test").get_word("b")
        c = lang().get_word("c")
        assert a is not None
        assert b is not None
        assert c is not None
        assert len(a.unions) == 1
        u = get_union(a)
        assert b in u
        assert c in u
        assert str(u) == "test:b+c"

    def test_union_default_lang(self):
        parser.yacc.parse("sa:a {b + c}")
        a = lang("sa").get_word("a")
        b = lang("sa").get_word("b")
        c = lang("sa").get_word("c")
        assert a is not None
        assert b is not None
        assert c is not None

class TestMeta(TestCase):

    def test_meta_eol_cmment(self):
        parser.yacc.parse("a -> b // comment")
        assert_total_word(config.default_lang, 2)
        assert_total_rels(1)

    def test_inline_comment(self):
        parser.yacc.parse("a = b (comment) c d")
        l = config.default_lang
        assert_total_word(config.default_lang, 2)
        assert lang(l).get_word("a")
        assert lang(l).get_word("b c d")
        assert not lang(l).get_word("comment")
        assert_total_word(config.default_lang, 2)

    def test_inline_comment_group(self):
        parser.yacc.parse(f"sa:purva = east (comment), first")
        assert_total_word(config.default_lang, 2)
        assert lang("en").get_word("east")
        assert lang("en").get_word("first")
        assert not lang("en").get_word("comment")
        assert_total_word("sa", 1)
        assert_total_word(config.default_lang, 2)

    def test_meta_src(self):
        # first test default
        parser.yacc.parse("w1")
        w = word("w1", config.default_lang)
        assert w.source is None
        # now test setting a source
        source = "http://www.somewhere.com"
        parser.yacc.parse(f"// SRC {source}")
        parser.yacc.parse("w2")
        w = word("w2", config.default_lang)
        assert w.source == source
        assert_total_rels(0)

    def test_meta_lang(self):
        parser.yacc.parse("// LANG sk")
        parser.yacc.parse("en:fire ~ sa:agni -> oheň")
        assert_total_word("en", 1)
        assert_total_word("sa", 1)
        assert_total_word("sk", 1)
        assert_total_rels(3)
        parser.yacc.parse("// LANG de")
        parser.yacc.parse("a -> b")
        assert_total_word("de", 2)
        parser.finish_file()
        assert config.default_lang == "en"


class TestTag(TestCase):
    def test_basic(self):
        parser.yacc.parse("a #b")
        assert "b" in lang().get_word("a").tags

    def test_basic_two_tags(self):
        parser.yacc.parse("a #b # c")
        assert "b" in lang().get_word("a").tags
        assert "c" in lang().get_word("a").tags
        assert len(model.World.Tags) == 2

    def test_rel(self):
        parser.yacc.parse("a ->b # c")
        assert "c" in lang().get_word("b").tags
        assert len(lang().get_word("a").tags) == 0

    def test_group(self):
        parser.yacc.parse("a,b # c")
        assert "c" in lang().get_word("b").tags


class TestMisc(TestCase):

    def test_delete_ignores_existing_words(self):
        parser.yacc.parse("a")
        parser.yacc.parse("a b")
        l = lang(config.default_lang)
        assert l.get_word("a") is not None
        assert l.get_word("a b") is not None
        assert_total_word(config.default_lang, 2)
        assert len(lang().get_word("a").tags) == 0
