"""
CLI helpers must terminate on cyclic data (a -> b -> a)
"""

from . util import *

import model
import details
import dict as dictmod
import parser


class TestCycles(TestCase):

    def setup_cycle(self):
        parser.yacc.parse("t:a -> t:b")
        parser.yacc.parse("t:b -> t:a")
        return model.World.lang("t").get_word("a")

    def test_derived_paths(self):
        a = self.setup_cycle()
        assert len(dictmod.derived_paths(a)) == 1

    def test_details(self, capsys):
        a = self.setup_cycle()
        details.details(a)
        details.parents(a)
        assert capsys.readouterr().out
