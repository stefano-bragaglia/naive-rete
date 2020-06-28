from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Tuple
from typing import Union
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from rete.utils import is_var

FIELDS = ['identifier', 'attribute', 'value']


class Triple(object):

    def __init__(self, identifier: str = None, attribute: str = None, value: str = None) -> None:
        """ Constructor.

        For example:
            (<x> ^self <y>)
        is  represented as:
            ('$x', 'self', '$y')

        :param identifier: a Var or str for the subject
        :param attribute: a Var or str for the predicate
        :param value: a Var or str for the object
        """
        self._identifier = identifier
        self._attribute = attribute
        self._value = value

    def __eq__(self, other: Any) -> bool:
        """ Check this and the other object are the same.

        :param other: the other object to compare
        :return: `True` if this and the other object are the same, `False` otherwise
        """
        if not isinstance(other, Triple):
            return False

        if self is other:
            return True

        return (self._identifier, self._attribute, self._value) == (other._identifier, other._attribute, other._value)

    def __repr__(self) -> str:
        """ Return a serialization of this object.

        :return: a serialization of this object
        """
        return f"({self._identifier} {self._attribute} {self._value})"

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def attribute(self) -> str:
        return self._attribute

    @property
    def value(self) -> str:
        return self._value

    @property
    def vars(self) -> List[Tuple[str, str]]:
        return [(k[1:], v) for k, v in self.__dict__.items() if is_var(v)]

    def contain(self, val: str) -> Optional[str]:
        """ Return the position where the given `val` is found, or None.

        :param val: the value to check
        :return: the position where the given `val` is found, or None
        """
        for key, value in self.__dict__.items():
            if val == value:
                return key[1:]

        return None


class WME(Triple):

    def __init__(self, identifier: str = None, attribute: str = None, value: str = None) -> None:
        super().__init__(identifier, attribute, value)

        self._amems = []  # amems: the ones containing this WME
        self._tokens = []  # tokens: the ones containing this WME
        self._negative_join_results = []  # negative_join_result

    def __eq__(self, other: Any) -> bool:
        """ Check this and the other object are the same.

        :param other: the other object to compare
        :return: `True` if this and the other object are the same, `False` otherwise
        """
        if not isinstance(other, WME):
            return False

        if self is other:
            return True

        return (self._identifier, self._attribute, self._value) == (other._identifier, other._attribute, other._value)

    def __repr__(self) -> str:
        """ Return a serialization of this object.

        :return: a serialization of this object
        """
        return f"({self._identifier} ^{self._attribute} {self._value})"

    @property
    def amems(self) -> Iterable[Any]:  # TODO
        return self._amems

    def add_amem(self, amem: 'AlphaMemory') -> None:
        self._amems.append(amem)

    @property
    def tokens(self) -> Iterable['Token']:
        return self._tokens

    @property
    def negative_join_results(self) -> Iterable[Any]:  # TODO
        return self._negative_join_results

    def add_memory(self, memory: 'Memory') -> None:
        if memory not in self._amems:
            self._amems.append(memory)

    def remove_memory(self, memory: 'Memory') -> None:
        if memory in self._amems:
            self._amems.remove(memory)

    def add_token(self, token: 'Token') -> None:
        if token not in self._tokens:
            self._tokens.append(token)

    def remove_token(self, token: 'Token') -> None:
        if token in self._tokens:
            self._tokens.remove(token)

    def add_negative_join_result(self, negative_join_result: Any) -> None:
        if negative_join_result not in self._negative_join_results:
            self._negative_join_results.append(negative_join_result)

    def remove_negative_join_result(self, negative_join_result: Any) -> None:
        if negative_join_result in self._negative_join_results:
            self._negative_join_results.remove(negative_join_result)

    def append_negative_join_results(self, join_result: 'NegativeJoinResult'):
        self._negative_join_results.append(join_result)

    def append_token(self, token: 'Token') -> None:
        self._tokens.append(token)


class Token:

    def __init__(self, parent, wme, node=None, binding=None):
        """
        :type wme: WME
        :type parent: Token
        :type binding: dict
        """
        self.parent = parent
        self.wme = wme
        self.node = node  # points to memory this token is in
        self.children = []  # the ones with parent = this token
        self.join_results = []  # used only on tokens in negative nodes
        self.ncc_results = []
        self.owner = None  # Ncc
        self.binding = binding if binding else {}  # {"$x": "B1"}

        if self.wme:
            self.wme.append_token(self)
        if self.parent:
            self.parent.children.append(self)

    def __repr__(self):
        return "<Token %s>" % self.wmes

    def __eq__(self, other):
        return isinstance(other, Token) and \
               self.parent == other.parent and self.wme == other.wme

    def is_root(self):
        return not self.parent and not self.wme

    @property
    def wmes(self):
        ret = [self.wme]
        t = self
        while t.parent and not t.parent.is_root():
            t = t.parent
            ret.insert(0, t.wme)
        return ret

    def get_binding(self, v):
        t = self
        ret = t.binding.get(v)
        while not ret and t.parent:
            t = t.parent
            ret = t.binding.get(v)
        return ret

    def all_binding(self):
        path = [self]
        if path[0].parent:
            path.insert(0, path[0].parent)
        binding = {}
        for t in path:
            binding.update(t.binding)
        return binding

    @staticmethod
    def delete_token_and_descendants(token: 'Token') -> None:
        """
        :type token: Token
        """
        from rete.nodes import NegativeNode
        from rete.nodes import NccPartnerNode
        from rete.nodes import NccNode

        for child in token.children:
            Token.delete_token_and_descendants(child)

        if not isinstance(token.node, NccPartnerNode):
            token.node.remove_token(token)
        if token.wme:
            token.wme.remove_token(token)
        if token.parent:
            token.parent.children.remove(token)
        if isinstance(token.node, NegativeNode):
            for jr in token.join_results:
                jr.wme.negative_join_results.remove(jr)
        elif isinstance(token.node, NccNode):
            for result_tok in token.ncc_results:
                result_tok.wme.tokens.remove(result_tok)
                result_tok.parent.children.remove(result_tok)
        elif isinstance(token.node, NccPartnerNode):
            token.owner.ncc_results.remove(token)
            if not token.owner.ncc_results:
                for child in token.node.ncc_node.children:
                    child.left_activation(token.owner, None)


class NegativeJoinResult(NamedTuple):
    owner: Token
    wme: WME


class JoinNodeTest(NamedTuple):
    field1: str
    condition2: int
    field2: str

    def __repr__(self) -> str:
        """ Return a serialization of this object.

        :return: a serialization of this object
        """
        return f"<JoinNodeTest WME.{self.field1}=Condition[{self.condition2}].{self.field2}?>"


class Condition(object):
    pass


class Has(Triple):

    def match(self, wme) -> bool:
        """ Check if the given `wme` matches this condition.

        :param wme: the `wme` to check
        :return: True if the given `wme` matches this condition, False otherwise
        """
        for key, value in self.__dict__.items():
            if value.startswith('$'):
                continue

            if value != wme.__dict__[key]:
                return False

        return True


class Neg(Has):

    def __repr__(self):
        return f"-({self._identifier} {self._attribute} {self._value})"


class Rule(list):

    def __init__(self, *args):
        super().__init__()
        self.extend(args)


class Ncc(Rule):

    def __repr__(self):
        return "-%s" % super(Ncc, self).__repr__()

    @property
    def number_of_conditions(self):
        return len(self)


class Filter:
    def __init__(self, template):
        self._template = template

    def __eq__(self, other):
        return isinstance(other, Filter) and self._template == other._template

    @property
    def template(self) -> str:
        return self._template


class Bind:
    def __init__(self, template: str, symbol: str) -> None:
        self._template = template
        self._symbol = symbol

    def __eq__(self, other: Any) -> bool:
        """ Check this and the other object are the same.

        :param other: the other object to compare
        :return: `True` if this and the other object are the same, `False` otherwise
        """
        if not isinstance(other, Bind):
            return False

        if self is other:
            return True

        return (self.template, self.symbol) == (other.template, other.symbol)

    @property
    def template(self) -> str:
        return self._template

    @property
    def symbol(self) -> str:
        return self._symbol


def parse_xml(content: str) -> List[Tuple[Rule, Dict[Any, Any]]]:
    result = []
    root = ElementTree.fromstring(content)
    for production in root:
        lhs = Rule()
        lhs.extend(parsing(production[0]))
        rhs = production[1].attrib
        result.append((lhs, rhs))

    return result


def parsing(root: Element) -> List[Union[Has, Neg, Filter, Bind, Ncc]]:
    result = []
    for item in root:
        if item.tag == 'has':
            result.append(Has(**item.attrib))
        elif item.tag == 'neg':
            result.append(Neg(**item.attrib))
        elif item.tag == 'filter':
            result.append(Filter(item.text))
        elif item.tag == 'bind':
            to = item.attrib.get('to')
            result.append(Bind(item.text, to))
        elif item.tag == 'ncc':
            n = Ncc()
            n.extend(parsing(item))
            result.append(n)

    return result
