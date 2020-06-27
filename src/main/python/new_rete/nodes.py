from typing import Any
from typing import Iterable
from typing import List

from rete.common import Token
from rete.common import WME


class Node(object):
    pass


class AlphaMemory(Node):
    def __init__(self, items: List[WME] = None, children: List['BetaNode'] = None) -> None:
        """ Constructor.

        :param items: initial list of WMEs
        :param children: initial list of Beta nodes
        """
        self._children = children or []
        self._items = items or []

    @property
    def children(self) -> Iterable['BetaNode']:
        return self._children

    @property
    def items(self) -> Iterable[WME]:
        return self._items

    def activation(self, wme: WME) -> None:
        """

        :param wme: the WME to propagate
        :return:
        """
        if wme not in self._items:
            self._items.append(wme)
            wme.amems.append(self)
            for child in reversed(self._children):
                child.right_activation(wme)


class BetaNode(Node):

    def __init__(self, children=None, parent=None):
        """ Constructor.

        :param children: initial list of children nodes
        :param parent: the parent node
        """
        self._children = children or []
        self._parent = parent

    @property
    def children(self) -> Iterable[Any]:
        return self._children

    @property
    def parent(self) -> Any:
        return self._parent

    def dump(self):
        return "%s %s" % (self.__class__.__name__, id(self))


class BetaMemory(BetaNode):

    def __init__(self, children=None, parent=None, tokens=None):
        """ Constructor.

        :param children: initial list of children nodes
        :param parent: the parent node
        :param tokens: initial list of tokens
        """
        super().__init__(children=children, parent=parent)
        self._tokens = tokens or []

    @property
    def tokens(self) -> Iterable[Token]:
        return self._tokens

    def left_activation(self, token: Token, wme: WME, binding=None):
        """
        :type binding: dict
        :type wme: WME
        :type token: Token
        """
        new_token = Token(token, wme, node=self, binding=binding)
        self._tokens.append(new_token)
        for child in self._children:
            child.left_activation(new_token)
