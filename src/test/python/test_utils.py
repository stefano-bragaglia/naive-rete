import os
from unittest import TestCase

from assertpy import assert_that

from rete import Bind
from rete import Filter
from rete import Has
from rete import Ncc
from rete import Rule
from rete.common import parse_xml
from rete.utils import is_var

FIXTURES = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fixtures'))


class Test(TestCase):
    def test__parse_xml(self):
        for i, (name, exp) in enumerate([
            ('example.xml', Rule(
                Has('$x', 'on', '$y'),
                Bind('1+1', '$test'),
                Filter('$y != "table"'),
                Ncc(Has('$z', 'color', 'red'),
                    Has('$z', 'on', '$w')))),
        ]):
            with self.subTest(i=i, name=name, exp=exp):
                with open(os.path.join(FIXTURES, 'example.xml'), 'r')as file:
                    content = file.read()
                    result = parse_xml(content)[0][0]

                    assert_that(result, 'parse_xml').is_equal_to(exp)

    def test__is_var(self):
        for i, (name, exp) in enumerate([
            ('$s', True),
            ('a', False),
        ]):
            with self.subTest(i - i, name=name, exp=exp):
                result = is_var(name)

                assert_that(result, 'is_var').is_equal_to(exp)
