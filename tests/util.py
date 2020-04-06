# Author   : Martin Užák <martin.uzak@gmail.com>
# Creation : 2020-04-03 20:39

"""
Supporting functions for tests
"""

import model
import config
import pytest


class TestCase:
    @pytest.fixture(autouse=True)
    def run_around_test(self):
        reset_model()
        yield


def reset_model():
    model.Derived.Table = {}
    model.Union.Table = {}
    model.Related.Table = {}
    model.Equals.Table = {}
    model.World.Languages = {}


def lang(language=None):
    language = language or config.default_lang
    return model.World.lang(language)


def word(value, language=None):
    language = language or config.default_lang
    return lang(language).get_word(value)


def _assert_rel_lr(rel, left, right, ll=config.default_lang, rl=config.default_lang):
    """"ll -> left lang"
    rl -> right lang """
    left = model.World.lang(ll).get_word(left)
    right = model.World.lang(rl).get_word(right)
    key = (left.key(), right.key())
    assert key in rel.Table


def assert_equals_lr(left, right, ll=config.default_lang, rl=config.default_lang):
    _assert_rel_lr(model.Equals, left, right, ll=ll, rl=rl)


def assert_derived_lr(left, right, ll=config.default_lang, rl=config.default_lang):
    _assert_rel_lr(model.Derived, left, right, ll=ll, rl=rl)


def assert_related_lr(left, right, ll=config.default_lang, rl=config.default_lang):
    _assert_rel_lr(model.Related, left, right, ll=ll, rl=rl)


def assert_total_rels(count):
    assert count == (len(model.Equals.Table) + len(model.Related.Table) + len(model.Derived.Table))


def assert_total_word(lang, count):
    assert count == len(model.World.lang(lang))
