from unittest import TestCase

from assertpy import assert_that

from rete import Bind
from rete import Filter
from rete import Has
from rete import Ncc
from rete import Rule
from rete.common import WME
# class TestBetaNode(TestCase):
#     def test_dump(self):
#         self.fail()
from rete.network import Network


class TestHas(TestCase):
    def test__vars(self):
        for i, (cond, exp) in enumerate([
            (Has('$x', 'is', '$y'), ['$x', '$y']),
        ]):
            with self.subTest(i=i, cond=cond, exp=exp):
                result = [e[1] for e in cond.vars]

                assert_that(result, 'vars').contains_only(*exp)

    def test__contain(self):
        for i, (cond, var, exp) in enumerate([
            (Has('$a', '$b', '$c'), '$a', 'identifier'),
            (Has('$a', '$b', '$c'), '$b', 'attribute'),
            (Has('$a', '$b', '$c'), '$c', 'value'),
            (Has('$a', '$b', '$c'), '$d', None),
        ]):
            with self.subTest(i=i, cond=cond, var=var, exp=exp):
                result = cond.contain(var)

                assert_that(result, 'contain').is_equal_to(exp)

    def test__test(self):
        for i, (cond, obj, exp) in enumerate([
            (Has('$x', 'color', 'red'), WME('B1', 'color', 'red'), True),
            (Has('$x', 'color', 'red'), WME('B1', 'color', 'blue'), False),
        ]):
            with self.subTest(i=i, cond=cond, obj=obj, exp=exp):
                result = cond.match(obj)

                assert_that(result, 'test').is_equal_to(exp)


class TestNcc(TestCase):
    def test__number_of_conditions(self):
        for i, (cond, exp) in enumerate([
            (Ncc(Has('$x', 'color', 'red')), 1),
            (Ncc(Has('$a', '$b', '$c'), Ncc(Has('$x', 'color', 'red'))), 2),
        ]):
            with self.subTest(i=i, cond=cond, exp=exp):
                result = cond.number_of_conditions

                assert_that(result, 'test').is_equal_to(exp)


# class TestToken(TestCase):
#     def test_is_root(self):
#         self.fail()
#
#     def test_wmes(self):
#         self.fail()
#
#     def test_get_binding(self):
#         self.fail()
#
#     def test_all_binding(self):
#         self.fail()
#
#     def test_delete_token_and_descendents(self):
#         self.fail()


class TestFilter(TestCase):

    def test__integration(self):
        for i, (rule, wmes, exp_len, var, exp_val) in enumerate([
            (Rule(Has('spu:1', 'price', '$x'), Filter('$x>100'), Filter('$x<200')),
             [WME('spu:1', 'price', '100'), WME('spu:1', 'price', '150'), WME('spu:1', 'price', '300')],
             1,
             '$x',
             '150'),
            (Rule(Has('spu:1', 'price', '$x'), Filter('$x>200 and $x<400')),
             [WME('spu:1', 'price', '100'), WME('spu:1', 'price', '150'), WME('spu:1', 'price', '300')],
             1,
             '$x',
             '300'),
            (Rule(Has('spu:1', 'price', '$x'), Filter('$x>300')),
             [WME('spu:1', 'price', '100'), WME('spu:1', 'price', '150'), WME('spu:1', 'price', '300')],
             0,
             None,
             None),
        ]):
            with self.subTest(i=i, exp_len=exp_len, var=var, exp_val=exp_val):
                network = Network()
                production = network.add_production(rule)
                for wme in wmes:
                    network.add_wme(wme)

                assert_that(production.memory, 'filter').is_length(exp_len)
                if production.memory:
                    token = production.memory[0]
                    assert_that(token.get_binding(var), 'filter').is_equal_to(exp_val)


class TestBind(TestCase):

    def test__integration(self):
        for i, (rule, wmes, exp_len, var, exp_val) in enumerate([
            (Rule(Has('spu:1', 'sales', '$x'), Bind('len(set($x) & set(range(1, 100)))', '$num'), Filter('$num > 0')),[WME('spu:1', 'sales', 'range(50, 110)')], 1, '$num', 50),
            (Rule(Has('spu:1', 'sales', '$x'), Bind('len(set($x) & set(range(100, 200)))', '$num'), Filter('$num > 0')),[WME('spu:1', 'sales', 'range(50, 110)')], 1, '$num', 10),
            (Rule(Has('spu:1', 'sales', '$x'), Bind('len(set($x) & set(range(300, 400)))', '$num'), Filter('$num > 0')),[WME('spu:1', 'sales', 'range(50, 110)')], 0, None, None),
        ]):
            with self.subTest(i=i, exp_len=exp_len, var=var, exp_val=exp_val):
                network = Network()
                production = network.add_production(rule)
                for wme in wmes:
                    network.add_wme(wme)

                assert_that(production.memory, 'filter').is_length(exp_len)
                if production.memory:
                    token = production.memory[0]
                    assert_that(token.get_binding(var), 'filter').is_equal_to(exp_val)
