from __future__ import absolute_import

import unittest
import logging
from plyplus.plyplus import Grammar, STree
from plyplus.template import Template, Var

logging.basicConfig(level=logging.INFO)

class TestSelectors(unittest.TestCase):
    def setUp(self):
        pass

    def test_vars(self):
        t = Template('a', [Var('x'), STree('b', [Var('y')])])
        t2 = STree('a', [STree('c', ['e', 'f']), STree('b', ['d'])])
        assert t2 == t.template(x=STree('c', ['e', 'f']), y='d')

    def test_string_vars(self):
        t = Template('{head1}', ['{str1}', STree('head{h2}', ['str{s1}'])])
        t2 = STree('a', ['b', STree('head2', ['string'])])
        assert t2 == t.template(head1='a', str1='b', h2='2', s1='ing')

    def test_parse_template(self):
        t = Template.from_str('a(x, {b}, "hi{c}")')
        t2 = Template.from_str('a(x, y(b,c), "hi2")')
        assert t2 == t.template(b=STree('y', ['b', 'c']), c=2)

if __name__ == '__main__':
    unittest.main()
