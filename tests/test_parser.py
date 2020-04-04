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


class TestParser:

    def test_word_basic(self):
        parser.yacc.parse("test:w")
        w = word("w", "test")
        assert w.value == "w"
        assert w.lang.name == "test"
        assert_total_word("test", 1)

    def test_word_basic_default_lang(self):
        l = config.default_lang
        parser.yacc.parse("w")
        w = word("w", l)
        assert w.value == "w"
        assert w.lang.name == l
        assert_total_word(config.default_lang, 1)

    def test_word_complex(self):
        parser.yacc.parse("test:w z")
        w = word("w z", "test")
        assert w.value == "w z"
        assert w.lang.name == "test"
        assert_total_word("test", 1)
        assert_total_word(config.default_lang, 0)

    def test_word_complex_overwrite_default_lang(self):
        parser.yacc.parse(f"test:w {config.default_lang}:z")
        w = word("w z", "test")
        assert w.value == "w z"
        assert w.lang.name == "test"
        assert_total_word("test", 1)
        assert_total_word(config.default_lang, 0)

    def word_word_word_rule(self):
        parser.yacc.parse("w1 = w2 w3; w4")
        l = config.default_lang
        assert f"{l}:w1={l}:w2 w3" in model.Equals.Table
        assert f"{l}:w1={l}:w4" in model.Equals.Table
        assert len(model.World.Relationships) == 2
        assert_total_word(config.default_lang, 4)

    # Groups

    def test_group(self):
        parser.yacc.parse("w1; w2")
        l = lang(config.default_lang)
        assert l.get_word("w1")
        assert l.get_word("w2")
        l = config.default_lang
        word("w1", l).value == "w1"
        word("w1", l).lang.name == config.default_lang
        word("w2", l).value == "w2"
        word("w2", l).lang.name == config.default_lang
        assert_total_word(config.default_lang, 2)

    def test_group(self):
        parser.yacc.parse("w1; w2; w3")
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


    # Relationships

    def test_rel_related(self):
        parser.yacc.parse("test:w1 ~ w2")
        assert_related_lr("w1", "w2", ll="test")

    def test_rel_derived(self):
        parser.yacc.parse("test:w1 -> w2")
        assert_derived_lr("w1", "w2", ll="test")

    def test_rel_rel(self):
        parser.yacc.parse("w1 -> w2 = w3")
        assert_derived_lr("w1", "w2")
        assert_equals_lr("w2", "w3")

    def test_rel_rel_groups(self):
        parser.yacc.parse("w1;w2 -> w3")
        assert_derived_lr("w2", "w3")
        assert_total_rels(1)

    def test_rel_rel_groups2(self):
        parser.yacc.parse("w2 -> w3;w4")
        assert_derived_lr("w2", "w3")
        assert_derived_lr("w2", "w4")
        assert_total_rels(2)

    def test_rel_rel_groups3(self):
        parser.yacc.parse("w1;w2 -> w3;w4")
        assert_derived_lr("w2", "w3")
        assert_derived_lr("w2", "w4")
        assert_total_rels(2)

    def test_rel_rel_complex(self):
        parser.yacc.parse("w1 -> w2;w3 = w5 -> w6")
        assert_derived_lr("w1", "w2")
        assert_derived_lr("w1", "w3")
        assert_equals_lr("w3", "w5")

    def test_rel_rel_complex2(self):
        parser.yacc.parse("w1 ~ w2 = w3 -> w4; w5")
        assert_related_lr("w1", "w2")
        assert_equals_lr("w2", "w3")
        assert_derived_lr("w3", "w4")
        assert_derived_lr("w3", "w5")

    def test_rel_rel_complex3(self):
        parser.yacc.parse("w1 ~ w2; w3 = w4 -> w5")
        assert_related_lr("w1", "w2")
        assert_related_lr("w1", "w3")
        assert_equals_lr("w3", "w4")
        assert_derived_lr("w4", "w5")

    def test_rel_rel_complex4(self):
        parser.yacc.parse("w1 -> w2; w3 = w4 ~ w5")
        l = config.default_lang
        assert_derived_lr("w1", "w2")
        assert_derived_lr("w1", "w3")
        assert_equals_lr("w3", "w4")
        assert_related_lr("w4", "w5")

    def test_rel_rel_complex5(self):
        parser.yacc.parse("w0; w1 = w2 -> w3 ~ w4; w5")
        l = config.default_lang
        assert_equals_lr("w1", "w2")
        assert_derived_lr("w2", "w3")
        assert_related_lr("w3", "w4")
        assert_related_lr("w3", "w5")


    def test_rel_bidirectional(self):
        parser.yacc.parse("w1 = w2")
        assert_equals_lr("w1", "w2")
        assert_equals_lr("w2", "w1")
        parser.yacc.parse("w2 = w1")

    def test_union(self):
        parser.yacc.parse("a + b -> c")
        l = lang(config.default_lang)
        a = l.get_word("a")
        b = l.get_word("b")
        key = (a, b)
        assert key in model.Union.Table
        value = model.Union.Table[key]
        assert (str(value), f"{config.default_lang}:c") in model.Derived.Table.keys()

    # Comments

    def test_comment(self):
        comment = "dynasty in which Lord Rama took birth"
        parser.yacc.parse(f"sa:Raghu [{comment}]")
        w = word("Raghu", "sa")
        assert comment in w.comments

    def test_derivation_comment(self):
        comment = "direction, where the sun first appears "
        parser.yacc.parse(f"sa:purva = [{comment}] east")
        assert lang("sa").get_word("purva")
        purva = word("purva", "sa")
        east = word("east", config.default_lang)
        r = model.Equals.get(purva, east)
        assert comment in r.comments

    def test_inline_comment(self):
        parser.yacc.parse("a = b (comment) c d")
        l = config.default_lang
        assert_total_word(config.default_lang, 2)
        assert lang(l).get_word("a")
        assert lang(l).get_word("b c d")
        assert not lang(l).get_word("comment")

    def test_inline_comment_group(self):
        parser.yacc.parse(f"sa:purva = east (comment); first")
        assert_total_word(config.default_lang, 2)
        assert lang("en").get_word("east")
        assert lang("en").get_word("first")
        assert not lang("en").get_word("comment")

    # Meta

    def test_meta_ignore(self):
        parser.yacc.parse("# do nothing")
        assert len(model.World.Languages) == 0
        assert_total_rels(0)

    def test_meta_src(self):
        # first test default
        parser.yacc.parse("w1")
        w = word("w1", config.default_lang)
        assert w.source is None
        # now test setting a source
        source = "http://www.somewhere.com"
        parser.yacc.parse(f"# SRC {source}")
        parser.yacc.parse("w2")
        w = word("w2", config.default_lang)
        assert w.source == source
        assert len(model.Derived.Table) == 0
        assert len(model.Equals.Table) == 0
        assert len(model.Related.Table) == 0

    @pytest.fixture(autouse=True)
    def run_around_test(self):
        reset_model()
        yield
