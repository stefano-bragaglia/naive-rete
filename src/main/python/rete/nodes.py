import copy
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from rete.common import FIELDS
from rete.common import NegativeJoinResult
from rete.common import Token
from rete.common import WME


class AlphaMemory:
    from rete.common import WME

    def __init__(self, memory: List[WME] = None, children: List[Union['JoinNode', 'NegativeNode']] = None):
        """ Constructor.

        :param memory: the content of the WME memory
        :param children: the children nodes
        """
        self._memory = memory or []
        self._children = children or []

    @property
    def children(self) -> Iterable[Union['JoinNode', 'NegativeNode']]:
        return self._children

    @property
    def memory(self) -> Iterable[WME]:
        return self._memory

    def activation(self, wme: WME) -> None:
        """

        :param wme: the activation WME
        """
        if wme not in self.memory:
            self._memory.append(wme)
            wme.add_amem(self)
            for child in reversed(self._children):
                child.right_activation(wme)

    def append_child(self, child: Union['JoinNode', 'NegativeNode']) -> None:
        if child not in self._children:
            self._children.append(child)

    def remove_child(self, child: Union['JoinNode', 'NegativeNode']) -> None:
        if child not in self._children:
            raise ValueError('unknown child')

        self._children.append(child)

    def replace_children(self, *child: Union['JoinNode', 'NegativeNode']) -> List[Union['JoinNode', 'NegativeNode']]:
        result = self._children
        self._children = list(child)

        return result


class ConstantTestNode:

    @staticmethod
    def build_or_share_alpha_memory(node: 'ConstantTestNode', path: List[Tuple[str, str]] = None) -> AlphaMemory:
        """ Build or share AlphaMemory from given `node` for given `path`.

        :param node: the current node
        :param path: the list of constraints
        :return: the desired `AlphaMemory`
        """
        if not path:
            if node._amem is None:
                node._amem = AlphaMemory()

            return node._amem

        field, symbol = path.pop(0)
        assert field in FIELDS, f"'{field}' not in {FIELDS}"
        next_node = ConstantTestNode.build_or_share_constant_test_node(node, field, symbol)

        return ConstantTestNode.build_or_share_alpha_memory(next_node, path)

    @staticmethod
    def build_or_share_constant_test_node(parent: 'ConstantTestNode', field: str, symbol: str) -> 'ConstantTestNode':
        """ Build or share ConstantTestNode from given `parent` for given `field` and `symbol`.

        :param parent: the parent node
        :param field: the field to test
        :param symbol: the symbol to match
        :return: the desired `ConstantTestNode`
        """
        for child in parent.children:
            if child._field == field and child._symbol == symbol:
                return child

        new_node = ConstantTestNode(field, symbol, children=[])
        parent._children.append(new_node)

        return new_node

    def __init__(
            self,
            field: str,
            symbol: str = None,
            amem: AlphaMemory = None,
            children: List['ConstantTestNode'] = None,
    ) -> None:
        """ Constructor.

        :param field: the field to test
        :param symbol: the symbol to match, if any
        :param amem: the corresponding `AlphaMemory`
        :param children: the list of ConstantTestNode successors
        """
        self._field = field
        self._symbol = symbol
        self._amem = amem
        self._children = children or []

    def __repr__(self) -> str:
        if not self._symbol and self._field == 'no-test':
            return "<ConstantTestNode>"

        return f"<ConstantTestNode {self.field}=={self.symbol}?>"

    @property
    def field(self) -> str:
        return self._field

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def amem(self) -> Optional[AlphaMemory]:
        return self._amem

    @amem.setter
    def amem(self, value: AlphaMemory) -> None:
        self._amem = value

    @property
    def children(self) -> Iterable['ConstantTestNode']:
        return self._children

    def dump(self) -> str:
        """ Return the descriptor for this node.

        :return: the descriptor for this node
        """
        return f"{self.field}=={self.symbol}?"

    def activation(self, wme: WME) -> Optional[bool]:
        """ Activate this node.

        :param wme: the activating payload
        """
        if self._field != 'no-test':
            symbol = getattr(wme, self._field)
            if symbol != self._symbol:
                return False

        if self._amem:
            self._amem.activation(wme)
        for child in self._children:
            child.activation(wme)


class BetaNode(object):

    def __init__(self, children: List[Any] = None, parent: Any = None) -> None:
        self._children = children or []
        self._parent = parent

    @property
    def children(self) -> Iterable[Any]:
        return self._children

    @property
    def parent(self) -> Any:
        return self._parent

    def dump(self):
        return f"{self.__class__.__name__} {id(self)}"

    def add_child(self, child: Any) -> None:
        if child not in self._children:
            self._children.append(child)

    def remove_child(self, child: Any) -> None:
        if child not in self._children:
            raise ValueError('unknown child')

        self._children.append(child)

    def replace_children(self, *child: Any) -> List[Any]:
        result = self._children
        self._children = list(child)

        return result

    def append_child(self, child: Any) -> None:
        self._children.append(child)

    def left_activation(self, token, wme, binding=None):
        """
        :type binding: dict
        :type wme: WME
        :type token: Token
        """
        new_token = Token(token, wme, node=self, binding=binding)
        for child in self.children:
            child.left_activation(new_token)


class BetaMemory(BetaNode):

    def __init__(self, children: List[Any] = None, parent=None, memory: List[Token] = None):
        """
        :type memory: list of Token
        """
        super(BetaMemory, self).__init__(children=children, parent=parent)
        self._children = children or []
        self._memory = memory or []

    @property
    def memory(self) -> Iterable[Token]:
        return self._memory

    def left_activation(self, token, wme, binding=None):
        """
        :type binding: dict
        :type wme: WME
        :type token: Token
        """
        new_token = Token(token, wme, node=self, binding=binding)
        self._memory.append(new_token)
        for child in self.children:
            child.left_activation(new_token)

    def append_token(self, token: Token) -> None:
        self._memory.append(token)

    def remove_token(self, token: Token) -> None:
        self._memory.remove(token)


class BindNode(BetaNode):

    def __init__(self, children, parent, template, to):
        """
        :type children:
        :type parent: BetaNode
        :type to: str
        """
        super(BindNode, self).__init__(children=children, parent=parent)
        self.template = template
        self.bind = to

    def left_activation(self, token, wme, binding=None):
        """
        :type binding: dict
        :type wme: WME
        :type token: Token
        """
        code = self.template
        all_binding = token.all_binding()
        all_binding.update(binding)
        for k in all_binding:
            code = code.replace(k, str(all_binding[k]))
        result = eval(code)
        binding[self.bind] = result
        for child in self.children:
            binding = copy.deepcopy(binding)
            child.left_activation(token, wme, binding)


class FilterNode(BetaNode):

    def __init__(self, children, parent, template):
        """ Constructor.

        :param children:
        :param parent: BetaNode
        :param template:
        """
        super(FilterNode, self).__init__(children=children, parent=parent)
        self.template = template

    def left_activation(self, token, wme, binding=None):
        """
        :type binding: dict
        :type wme: WME
        :type token: Token
        """
        code = self.template
        all_binding = token.all_binding()
        all_binding.update(binding)
        for k in all_binding:
            code = code.replace(k, str(all_binding[k]))
        result = eval(code)
        if bool(result):
            for child in self.children:
                child.left_activation(token, wme, binding)


class JoinNode(BetaNode):
    from rete.common import WME

    def __init__(self, children, parent, amem, tests, has):
        """
        :type children:
        :type parent: BetaNode
        :type amem: AlphaMemory
        :type tests: list of TestAtJoinNode
        :type has: Has
        """
        super(JoinNode, self).__init__(children=children, parent=parent)
        self.amem = amem
        self.tests = tests
        self.has = has

    def right_activation(self, wme: WME) -> None:
        """

        :param wme: the activation WME
        """
        for token in self.parent.memory:
            if self.perform_join_test(token, wme):
                binding = self.make_binding(wme)
                for child in self.children:
                    child.left_activation(token, wme, binding)

    def left_activation(self, token: Token) -> None:
        """

        :param token: the activation Token
        """
        for wme in self.amem.memory:
            if self.perform_join_test(token, wme):
                binding = self.make_binding(wme)
                for child in self.children:
                    child.left_activation(token, wme, binding)

    def perform_join_test(self, token: Token, wme: WME) -> bool:
        """

        :param token: the Token on which to try to perform the join
        :param wme: the WME on which to try to perform the join
        :return: True if the the join is possible, False otherwise
        """
        for this_test in self.tests:
            arg1 = getattr(wme, this_test.field1)
            wme2 = token.wmes[this_test.condition2]
            arg2 = getattr(wme2, this_test.field2)
            if arg1 != arg2:
                return False

        return True

    def make_binding(self, wme: WME) -> Dict[str, str]:
        """

        :param wme: the WME to bind
        :return:
        """
        return {v: getattr(wme, f) for f, v in self.has.vars}


class NccNode(BetaNode):

    def __init__(
            self,
            children: List[Any] = None,
            parent: Any = None,
            memory: List[Token] = None,
            partner: 'NccPartnerNode' = None,
    ) -> None:
        """

        :param children:
        :param parent:
        :param memory: list of Token
        :param partner: NccPartnerNode
        """
        super(NccNode, self).__init__(children=children, parent=parent)
        self._memory = memory or []
        self.partner = partner

    @property
    def memory(self) -> Iterable[Any]:
        return self._memory

    def left_activation(self, t, w, binding=None):
        """
        :type w: rete.WME
        :type t: rete.Token
        :type binding: dict
        """
        new_token = Token(t, w, self, binding)
        self._memory.append(new_token)
        for result in self.partner.new_result_buffer:
            self.partner.new_result_buffer.remove(result)
            new_token.ncc_results.append(result)
            result.owner = new_token
        if not new_token.ncc_results:
            for child in self.children:
                child.left_activation(new_token, None)

    def remove_token(self, token: Token) -> None:
        self._memory.remove(token)


class NccPartnerNode(BetaNode):

    def __init__(self, children=None, parent=None, ncc_node=None,
                 number_of_conditions=0, new_result_buffer=None):
        """
        :type new_result_buffer: list of rete.Token
        :type ncc_node: rete.nodes.NccNode
        """
        super(NccPartnerNode, self).__init__(children=children, parent=parent)
        self.ncc_node = ncc_node
        self.number_of_conditions = number_of_conditions
        self.new_result_buffer = new_result_buffer if new_result_buffer else []

    def left_activation(self, t, w, binding=None):
        """
        :type w: rete.WME
        :type t: rete.Token
        :type binding: dict
        """
        new_result = Token(t, w, self, binding)
        owners_t = t
        owners_w = w
        for i in range(self.number_of_conditions):
            owners_w = owners_t.wme
            owners_t = owners_t.parent
        for token in self.ncc_node.memory:
            if token.parent == owners_t and token.wme == owners_w:
                token.ncc_results.append(new_result)
                new_result.owner = token
                Token.delete_token_and_descendants(token)
        self.new_result_buffer.append(new_result)


class NegativeNode(BetaNode):

    def __init__(self, children=None, parent=None, amem=None, tests=None):
        """
        :type amem: rete.alpha.AlphaMemory
        """
        super(NegativeNode, self).__init__(children=children, parent=parent)
        self._memory = []
        self.amem = amem
        self.tests = tests if tests else []

    @property
    def memory(self) -> Iterable[Any]:
        return self._memory

    def left_activation(self, token, wme, binding=None):
        """
        :type wme: rete.WME
        :type token: rete.Token
        :type binding: dict
        """
        new_token = Token(token, wme, self, binding)
        self._memory.append(new_token)
        for item in self.amem.memory:
            if self.perform_join_test(new_token, item):
                jr = NegativeJoinResult(new_token, item)
                new_token.join_results.append(jr)
                item.append_negative_join_results(jr)
        if not new_token.join_results:
            for child in self.children:
                child.left_activation(new_token, None)

    def right_activation(self, wme):
        """
        :type wme: rete.WME
        """
        for t in self.memory:
            if self.perform_join_test(t, wme):
                if not t.join_results:
                    Token.delete_token_and_descendants(t)
                jr = NegativeJoinResult(t, wme)
                t.join_results.append(jr)
                wme.negative_join_results.append(jr)

    def perform_join_test(self, token, wme):
        """
        :type token: rete.Token
        :type wme: rete.WME
        """
        for this_test in self.tests:
            arg1 = getattr(wme, this_test.field1)
            wme2 = token.wmes[this_test.condition2]
            arg2 = getattr(wme2, this_test.field2)
            if arg1 != arg2:
                return False
        return True

    def remove_token(self, token: Token) -> None:
        self._memory.remove(token)


class ProductionNode(BetaNode):

    def __init__(self, children=None, parent=None, memory=None, **kwargs):
        """
        :type memory: list of Token
        """
        super(ProductionNode, self).__init__(children=children, parent=parent)
        self._memory = memory or []
        # self.children = children if children else []
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def memory(self) -> Iterable[Token]:
        return self._memory

    def left_activation(self, token, wme, binding=None):
        """
        :type wme: WME
        :type token: Token
        :type binding: dict
        """
        new_token = Token(token, wme, node=self, binding=binding)
        self._memory.append(new_token)

    def execute(self, *args, **kwargs):
        raise NotImplementedError

    def remove_token(self, token: Token) -> None:
        self._memory.remove(token)
