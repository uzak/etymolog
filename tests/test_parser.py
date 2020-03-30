# Author   : Martin Užák <martin.uzak@gmail.com>
# Creation : 2020-03-28 20:49

"""
test the parser, obviously
"""

import pytest

import model
import parser
import config


lang = model.World.lang
r = lambda : model.World.Relationships
rk = lambda : model.World.Relationships.keys()


class TestParser:

    def test_word_basic(self):
        parser.yacc.parse("test:w")
        w = lang("test").word("w")
        assert w.value == "w"
        assert w.lang.name == "test"

    def test_word_basic_default_lang(self):
        l = config.default_lang
        parser.yacc.parse("w")
        w = lang(l).word("w")
        assert w.value == "w"
        assert w.lang.name == l

    def test_word_complex(self):
        parser.yacc.parse("test:w z")
        w = lang("test").word("w z")
        assert w.value == "w z"
        assert w.lang.name == "test"

    def test_word_prio(self):
        parser.yacc.parse("(test:w)")
        w = lang("test").word("w")
        assert w.value == "w"
        assert w.lang.name == "test"

    def test_word_prio_default_lang(self):
        parser.yacc.parse("(w)")
        w = lang(config.default_lang).word("w")
        assert w.value == "w"
        assert w.lang.name == config.default_lang

    def word_word_word_rule(self):
        parser.yacc.parse("w1 = w2 w3, w4")
        l = config.default_lang
        assert f"{l}:w1={l}:w2 w3" in rk()
        assert f"{l}:w1={l}:w4" in rk()
        assert len(model.World.Relationships) == 2

    # Groups

    def test_group(self):
        parser.yacc.parse("w1, w2")
        l = lang(config.default_lang)
        assert "w1" in l.words
        assert "w2" in l.words
        l.word("w1").value == "w1"
        l.word("w1").lang.name == config.default_lang
        l.word("w2").value == "w2"
        l.word("w2").lang.name == config.default_lang

    def test_group(self):
        parser.yacc.parse("w1, w2, w3")
        l = lang(config.default_lang)
        assert "w1" in l.words
        assert "w2" in l.words
        assert "w3" in l.words
        l.word("w1").value == "w1"
        l.word("w1").lang.name == config.default_lang
        l.word("w2").value == "w2"
        l.word("w2").lang.name == config.default_lang
        l.word("w3").value == "w3"
        l.word("w3").lang.name == config.default_lang


    def test_group_prio(self):
        parser.yacc.parse("(w1,test:w2)")
        l = lang(config.default_lang)
        l_test = lang("test")
        assert "w1" in l.words
        assert "w2" in l_test.words
        l.word("w1").value == "w1"
        l.word("w1").lang.name == config.default_lang
        l_test.word("w2").value == "w2"
        l_test.word("w2").lang.name == "test"


    # Relationships

    def test_rel_related(self):
        parser.yacc.parse("test:w1 ~ w2")
        assert f"test:w1~{config.default_lang}:w2" in model.World.Relationships

    def test_rel_derived(self):
        parser.yacc.parse("test:w1 -> w2")
        assert f"test:w1->{config.default_lang}:w2" in model.World.Relationships

    def test_rel_derived_prio(self):
        parser.yacc.parse("(test:w1 -> w2)")
        assert f"test:w1->{config.default_lang}:w2" in model.World.Relationships

    def test_rel_rel(self):
        parser.yacc.parse("w1 -> w2 = w3")
        l = config.default_lang
        assert f"{l}:w2={l}:w3" in model.World.Relationships
        assert f"{l}:w1->{l}:w2" in model.World.Relationships

    def test_rel_rel_prio(self):
        parser.yacc.parse("((w1 -> w2) = w3)")
        l = config.default_lang
        assert f"{l}:w2={l}:w3" in model.World.Relationships
        assert f"{l}:w1->{l}:w2" in model.World.Relationships

    def test_rel_rel_prio(self):
        parser.yacc.parse("((w1 -> w2) = w3)")
        l = config.default_lang
        assert f"{l}:w2={l}:w3" in model.World.Relationships
        assert f"{l}:w1->{l}:w2" in model.World.Relationships

    def test_rel_rel_groups(self):
        parser.yacc.parse("w1,w2 -> w3")
        l = config.default_lang
        assert f"{l}:w2->{l}:w3" in model.World.Relationships
        assert len(model.World.Relationships) == 1

    def test_rel_rel_groups2(self):
        parser.yacc.parse("w2 -> w3,w4")
        l = config.default_lang
        assert f"{l}:w2->{l}:w3" in model.World.Relationships
        assert f"{l}:w2->{l}:w4" in model.World.Relationships
        assert len(model.World.Relationships) == 2

    def test_rel_rel_groups3(self):
        parser.yacc.parse("w1,w2 -> w3,w4")
        l = config.default_lang
        assert f"{l}:w2->{l}:w3" in model.World.Relationships
        assert f"{l}:w2->{l}:w4" in model.World.Relationships
        assert len(model.World.Relationships) == 2

    def test_rel_rel_complex(self):
        parser.yacc.parse("w1 -> w2,w3 = w5 -> w6")
        l = config.default_lang
        assert f"{l}:w1->{l}:w2" in model.World.Relationships
        assert f"{l}:w1->{l}:w3" in model.World.Relationships
        assert f"{l}:w3={l}:w5" in model.World.Relationships
        assert len(model.World.Relationships) == 4

    def test_rel_rel_complex2(self):
        parser.yacc.parse("w1 ~ (w2 = w3) -> w4, w5")
        l = config.default_lang
        assert f"{l}:w2={l}:w3" in rk()
        assert f"{l}:w1~{l}:w3" in rk()
        assert f"{l}:w3->{l}:w4" in rk()
        assert f"{l}:w3->{l}:w5" in rk()
        assert len(model.World.Relationships) == 4

    def test_rel_rel_complex3(self):
        parser.yacc.parse("w1 ~ w2, w3 = w4 -> w5")
        l = config.default_lang
        assert f"{l}:w1~{l}:w2" in model.World.Relationships
        assert f"{l}:w1~{l}:w3" in model.World.Relationships
        assert f"{l}:w3={l}:w4" in model.World.Relationships
        assert f"{l}:w4->{l}:w5" in model.World.Relationships
        assert len(model.World.Relationships) == 4

    def test_rel_rel_complex4(self):
        parser.yacc.parse("w1 -> w2, w3 = w4 ~ w5")
        l = config.default_lang
        assert f"{l}:w1->{l}:w2" in model.World.Relationships
        assert f"{l}:w1->{l}:w3" in model.World.Relationships
        assert f"{l}:w3={l}:w4" in model.World.Relationships
        assert f"{l}:w4~{l}:w5" in model.World.Relationships
        assert len(model.World.Relationships) == 4

    def test_rel_rel_complex5(self):
        parser.yacc.parse("w0, w1 = w2 -> w3 ~ w4, w5")
        l = config.default_lang
        assert f"{l}:w1={l}:w2" in rk()
        assert f"{l}:w2->{l}:w3" in rk()
        assert f"{l}:w3~{l}:w4" in rk()
        assert f"{l}:w3~{l}:w5" in rk()
        assert len(model.World.Relationships) == 4

    def test_rel_bidirectional(self):
        parser.yacc.parse("w1 = w2")
        parser.yacc.parse("w2 = w1")
        l = config.default_lang
        assert f"{l}:w1={l}:w2" in rk()
        assert len(model.World.Relationships) == 1

    def test_union(self):
        parser.yacc.parse("a + b -> c")
        l = config.default_lang
        assert f"{l}:a+{l}:b" in rk()
        assert f"+({l}:a, {l}:b)->{l}:c" in rk()

    # Comments

    def test_comment(self):
        comment = "dynasty in which Lord Rama took birth"
        parser.yacc.parse(f"sa:Raghu [{comment}]")
        w = lang("sa").word("Raghu")
        assert comment in w.comments

    def test_derivation_comment(self):
        comment = "direction, where the sun first appears "
        parser.yacc.parse(f"sa:purva -> [{comment}] east")
        assert "purva" in lang("sa").words
        purva = lang("sa").word("purva")
        assert len(purva.rels) > 0
        found = 0
        for r in purva.rels:
            if r.right.value == "east" and type(r) is model.Derive:
                assert comment in r.comments
                found = 1
        assert found

    # Meta

    def test_meta_ignore(self):
        parser.yacc.parse("# do nothing")
        assert len(model.World.Relationships) == 0
        assert len(model.World.Languages) == 0

    def test_meta_src(self):
        # first test default
        parser.yacc.parse("w1")
        w = lang(config.default_lang).word("w1")
        assert w.source is None
        # now test setting a source
        source = "http://www.somewhere.com"
        parser.yacc.parse(f"# SRC {source}")
        parser.yacc.parse("w2")
        w = lang(config.default_lang).word("w2")
        assert w.source == source
        assert len(model.World.Relationships) == 0


    @pytest.fixture(autouse=True)
    def run_around_test(self):
        model.World.Relationships = {}
        model.World.Languages = {}
        yield
