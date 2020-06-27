from unittest import TestCase

from rete.alpha import ConstantTestNode
from rete.common import WME


class TestConstantTestNode(TestCase):
    # def test_dump(self):
    #     self.fail()

    # def test_activation(self):
    #     self.fail()

    # def test_build_or_share_alpha_memory(self):
    #     self.fail()

    # def test_build_or_share_constant_test_node(self):
    #     self.fail()

    def test_root(self):
        # (Var('a'), Var('b'), Var('c')
        root = ConstantTestNode('no-test')
        path = []
        am0 = ConstantTestNode.build_or_share_alpha_memory(root, path)
        assert am0 is not None

        am1 = ConstantTestNode.build_or_share_alpha_memory(root, path)
        assert am0 == am1

    def test_level1(self):
        # (Var('x'), 'on', Var('y'))
        root = ConstantTestNode('no-test')
        path = [('attribute', 'on')]
        ConstantTestNode.build_or_share_alpha_memory(root, path)
        assert root.children[0].field_to_test == 'attribute'
        assert root.children[0].field_must_equal == 'on'
        assert len(path) == 0

    def test_level2(self):
        # (Var('x'), 'on', 'table')
        root = ConstantTestNode('no-test')
        path = [('attribute', 'on'), ('value', 'table')]
        ConstantTestNode.build_or_share_alpha_memory(root, path)
        assert root.children[0].field_to_test == 'attribute'
        assert root.children[0].children[0].field_to_test == 'value'

        path = [('attribute', 'color'), ('value', 'red')]
        ConstantTestNode.build_or_share_alpha_memory(root, path)
        path = [('attribute', 'color'), ('value', 'blue')]
        ConstantTestNode.build_or_share_alpha_memory(root, path)
        assert len(root.children[1].children) == 2

    def test_add_wme(self):
        root = ConstantTestNode('no-test')
        am1 = ConstantTestNode.build_or_share_alpha_memory(root, [('attribute', 'on')])
        am2 = ConstantTestNode.build_or_share_alpha_memory(root, [('attribute', 'on'), ('value', 'table')])

        root.activation(WME('x', 'on', 'table'))
        assert len(am1.items) == 1
        assert len(am2.items) == 1

# class TestAlphaMemory(TestCase):
#     def test_activation(self):
#         self.fail()
