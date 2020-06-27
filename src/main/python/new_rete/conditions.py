from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

from rete.beta import BetaMemory


class Triple(object):

    def __init__(self, identifier: str = None, attribute: str = None, value: str = None) -> None:
        """ Constructor.

        :param identifier: the identifier
        :param attribute: the attribute
        :param value:  the value
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
    def vars(self):
        return [v for v in self.__dict__.values() if v.startswith('$')]

    def contain(self, val: str) -> Optional[str]:
        for key, value in self.__dict__.items():
            if val == value:
                return key[1:]

        return None


class WME(Triple):

    def __init__(self, identifier: str = None, attribute: str = None, value: str = None) -> None:
        super().__init__(identifier, attribute, value)
        self._memories = []  # the ones containing this WME
        self._tokens = []  # the ones containing this WME
        self._neg_joins = []

    def __repr__(self) -> str:
        """ Return a serialization of this object.

        :return: a serialization of this object
        """
        return f"({self._identifier} ^{self._attribute} {self._value})"

    @property
    def memories(self) -> Iterable['Memory']:
        return self._memories

    @property
    def tokens(self) -> Iterable['Token']:
        return self._tokens

    @property
    def neg_joins(self) -> Iterable['NegJoin']:
        return self._neg_joins

    def add_memory(self, memory: 'Memory') -> 'WME':
        if memory not in self._memories:
            self._memories.append(memory)

        return self

    def add_token(self, token: 'Token') -> 'WME':
        if token not in self._tokens:
            self._tokens.append(token)

        return self

    def add_neg_join(self, neg_join: 'NegJoin') -> 'WME':
        if neg_join not in self._neg_joins:
            self._neg_joins.append(neg_join)

        return self

    def remove_token(self, token: 'Token') -> None:
        if token in self._tokens:
            self._tokens.remove(token)


class Token(object):

    def __init__(self, wme: WME, parent: 'Token' = None, node: BetaMemory = None,
                 binding: Dict[str, str] = None) -> None:
        """ Constructor.

        :param wme: the WME to hold
        :param parent: to parent Token, if any
        :param node: the memory this token is in
        :param binding:
        """
        self._wme = wme
        self._parent = parent
        self._node = node
        self._binding = binding or {}  # {"$x": "B1"}

        self._children = []  # the ones with parent = this token
        self._join_results = []  # used only on tokens in negative nodes
        self._ncc_results = []
        self._owner = None  # Ncc

        if self._wme:
            self._wme.add_token(self)
        if self._parent:
            self._parent.add_child(self)

    def __eq__(self, other: Any) -> bool:
        """ Check this and the other object are the same.

        :param other: the other object to compare
        :return: `True` if this and the other object are the same, `False` otherwise
        """
        if not isinstance(other, Token):
            return False

        if self is other:
            return True

        return (self._wme, self._parent) == (other._wme, other._parent)

    def __repr__(self) -> str:
        """ Return a serialization of this object.

        :return: a serialization of this object
        """
        return f"<Token: {self.wmes}>"

    @property
    def wme(self) -> WME:
        return self._wme

    @property
    def parent(self) -> 'Token':
        return self._parent

    @property
    def node(self) -> BetaMemory:
        return self._node

    @property
    def wmes(self):
        result = [self._wme]
        current = self
        while current._parent and not current._parent.is_root():
            current = current.parent
            result.insert(0, current.wme)

        return result

    def add_child(self, child: 'Token') -> None:
        self._children.append(child)

    def remove_child(self, child: 'Token') -> None:
        if child in self._children:
            self._children.remove(child)

    def add_ncc_results(self, ncc_result: 'NegCompoundCondition') -> None:
        self._ncc_results.append(ncc_result)

    def remove_ncc_results(self, ncc_result: 'NCC') -> None:
        if ncc_result in self._ncc_results:
            self._ncc_results.remove(ncc_result)

    def get_all_binding(self, var: str) -> Dict[str, str]:
        path = [self]
        if self._parent:
            path.insert(0, self._parent)

        result = {}
        for current in path:
            result.update(current._binding)

        return result

    def get_binding(self, var: str) -> Optional[str]:
        result = self._binding.get(var)
        current = self
        while not result and current._parent:
            current = current._parent
            result = current._binding.get(var)

        return result

    def is_root(self) -> bool:
        return not (self._parent or self._wme)

    @staticmethod
    def delete_token_and_descendents(token):
        """
        :type token: Token
        """
        from rete.beta import NegativeNode
        from rete.beta import NccPartnerNode
        from rete.beta import NccNode

        for child in token._children:
            Token.delete_token_and_descendents(child)

        if not isinstance(token._node, NccPartnerNode):
            token.node.items.remove(token)

        if token._wme:
            token._wme.remove_token(token)

        if token._parent:
            token._parent.remove_child(token)

        if isinstance(token._node, NegativeNode):
            for jr in token._join_results:
                jr.wme.negative_join_result.remove(jr)

        elif isinstance(token.node, NccNode):
            for result_tok in token._ncc_results:
                result_tok._wme.remove_tokens(result_tok)
                result_tok._parent.remove_child(result_tok)

        elif isinstance(token.node, NccPartnerNode):
            token._owner.ncc_results.remove(token)
            if not token._owner._ncc_results:
                for child in token._node._ncc_node._children:
                    child.left_activation(token._owner, None)


class Condition(object):
    pass


class Has(Condition, Triple):

    def match(self, wme: 'WME') -> bool:
        for key, value in self.__dict__.items():
            if value.startswith('$'):
                continue

            if value != wme.__dict__[key]:
                return False

        return True


class Neg(Has):

    def __repr__(self) -> str:
        """ Return a serialization of this object.

        :return: a serialization of this object
        """
        return f"-({self._identifier} {self._attribute} {self._value})"


class Bind(object):
    def __init__(self, template: str, var: str) -> None:
        self._template = template
        self._var = var

    def __eq__(self, other: Any) -> bool:
        """ Check this and the other object are the same.

        :param other: the other object to compare
        :return: `True` if this and the other object are the same, `False` otherwise
        """
        if not isinstance(other, Bind):
            return False

        if self is other:
            return True

        return (self._template, self._var) == (other._template, other._var)

    @property
    def template(self) -> str:
        return self._template

    @property
    def var(self) -> str:
        return self._var


class Filter(object):

    def __init__(self, template: str) -> None:
        self._template = template

    def __eq__(self, other: Any) -> bool:
        """ Check this and the other object are the same.

        :param other: the other object to compare
        :return: `True` if this and the other object are the same, `False` otherwise
        """
        if not isinstance(other, Filter):
            return False

        if self is other:
            return True

        return self._template == other._template

    @property
    def template(self) -> str:
        return self._template


class Rule(Condition):
    def __init__(self, conditions: List[Condition]):
        self._conditions = conditions

    def __getitem__(self, pos: int) -> Condition:
        return self._conditions[pos]

    def __len__(self) -> int:
        return len(self._conditions)


class NegCompoundCondition(Rule):

    def __repr__(self) -> str:
        """ Return a serialization of this object.

        :return: a serialization of this object
        """
        return f"-{self._conditions}"
