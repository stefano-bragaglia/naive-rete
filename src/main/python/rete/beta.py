import copy

from rete.common import Token


# done
from rete.common import Token
from rete.common import Token
from rete.common import Token
from rete.common import Token
from rete.common import Token
from rete.common import Token
from rete.negative_node import NegativeJoinResult
from rete.negative_node import NegativeJoinResult


class BetaNode(object):

    def __init__(self, children=None, parent=None):
        self.children = children if children else []
        self.parent = parent

    def dump(self):
        return "%s %s" % (self.__class__.__name__, id(self))


# done
class BetaMemory(BetaNode):

    def __init__(self, children=None, parent=None, items=None):
        """
        :type items: list of Token
        """
        super(BetaMemory, self).__init__(children=children, parent=parent)
        self.items = items if items else []
        self.children = children if children else []

    def left_activation(self, token, wme, binding=None):
        """
        :type binding: dict
        :type wme: WME
        :type token: Token
        """
        new_token = Token(token, wme, node=self, binding=binding)
        self.items.append(new_token)
        for child in self.children:
            child.left_activation(new_token)


# TODO
class BindNode(BetaNode):

    def __init__(self, children, parent, tmpl, to):
        """
        :type children:
        :type parent: BetaNode
        :type to: str
        """
        super(BindNode, self).__init__(children=children, parent=parent)
        self.tmpl = tmpl
        self.bind = to

    def left_activation(self, token, wme, binding=None):
        """
        :type binding: dict
        :type wme: WME
        :type token: Token
        """
        code = self.tmpl
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

    def __init__(self, children, parent, tmpl):
        """
        :type children:
        :type parent: BetaNode
        :type bind: str
        """
        super(FilterNode, self).__init__(children=children, parent=parent)
        self.tmpl = tmpl

    def left_activation(self, token, wme, binding=None):
        """
        :type binding: dict
        :type wme: WME
        :type token: Token
        """
        code = self.tmpl
        all_binding = token.all_binding()
        all_binding.update(binding)
        for k in all_binding:
            code = code.replace(k, str(all_binding[k]))
        result = eval(code)
        if bool(result):
            for child in self.children:
                child.left_activation(token, wme, binding)


class JoinNode(BetaNode):

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

    def right_activation(self, wme):
        """
        :type wme: rete.WME
        """
        for token in self.parent.items:
            if self.perform_join_test(token, wme):
                binding = self.make_binding(wme)
                for child in self.children:
                    child.left_activation(token, wme, binding)

    def left_activation(self, token):
        """
        :type token: rete.Token
        """
        for wme in self.amem.items:
            if self.perform_join_test(token, wme):
                binding = self.make_binding(wme)
                for child in self.children:
                    child.left_activation(token, wme, binding)

    def perform_join_test(self, token, wme):
        """
        :type token: rete.Token
        :type wme: rete.WME
        """
        for this_test in self.tests:
            arg1 = getattr(wme, this_test.field_of_arg1)
            wme2 = token.wmes[this_test.condition_number_of_arg2]
            arg2 = getattr(wme2, this_test.field_of_arg2)
            if arg1 != arg2:
                return False
        return True

    def make_binding(self, wme):
        """
        :type wme: WME
        """
        binding = {}
        for field, v in self.has.vars:
            val = getattr(wme, field)
            binding[v] = val
        return binding


class NccNode(BetaNode):

    def __init__(self, children=None, parent=None, items=None, partner=None):
        """
        :type partner: NccPartnerNode
        :type items: list of rete.Token
        """
        super(NccNode, self).__init__(children=children, parent=parent)
        self.items = items if items else []
        self.partner = partner

    def left_activation(self, t, w, binding=None):
        """
        :type w: rete.WME
        :type t: rete.Token
        :type binding: dict
        """
        new_token = Token(t, w, self, binding)
        self.items.append(new_token)
        for result in self.partner.new_result_buffer:
            self.partner.new_result_buffer.remove(result)
            new_token.ncc_results.append(result)
            result.owner = new_token
        if not new_token.ncc_results:
            for child in self.children:
                child.left_activation(new_token, None)


class NccPartnerNode(BetaNode):

    def __init__(self, children=None, parent=None, ncc_node=None,
                 number_of_conditions=0, new_result_buffer=None):
        """
        :type new_result_buffer: list of rete.Token
        :type ncc_node: rete.beta.NccNode
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
        for token in self.ncc_node.items:
            if token.parent == owners_t and token.wme == owners_w:
                token.ncc_results.append(new_result)
                new_result.owner = token
                Token.delete_token_and_descendents(token)
        self.new_result_buffer.append(new_result)


class NegativeNode(BetaNode):

    def __init__(self, children=None, parent=None, amem=None, tests=None):
        """
        :type amem: rete.alpha.AlphaMemory
        """
        super(NegativeNode, self).__init__(children=children, parent=parent)
        self.items = []
        self.amem = amem
        self.tests = tests if tests else []

    def left_activation(self, token, wme, binding=None):
        """
        :type wme: rete.WME
        :type token: rete.Token
        :type binding: dict
        """
        new_token = Token(token, wme, self, binding)
        self.items.append(new_token)
        for item in self.amem.items:
            if self.perform_join_test(new_token, item):
                jr = NegativeJoinResult(new_token, item)
                new_token.join_results.append(jr)
                item.negative_join_result.append(jr)
        if not new_token.join_results:
            for child in self.children:
                child.left_activation(new_token, None)

    def right_activation(self, wme):
        """
        :type wme: rete.WME
        """
        for t in self.items:
            if self.perform_join_test(t, wme):
                if not t.join_results:
                    Token.delete_token_and_descendents(t)
                jr = NegativeJoinResult(t, wme)
                t.join_results.append(jr)
                wme.negative_join_result.append(jr)

    def perform_join_test(self, token, wme):
        """
        :type token: rete.Token
        :type wme: rete.WME
        """
        for this_test in self.tests:
            arg1 = getattr(wme, this_test.field_of_arg1)
            wme2 = token.wmes[this_test.condition_number_of_arg2]
            arg2 = getattr(wme2, this_test.field_of_arg2)
            if arg1 != arg2:
                return False
        return True


class PNode(BetaNode):

    def __init__(self, children=None, parent=None, items=None, **kwargs):
        """
        :type items: list of Token
        """
        super(PNode, self).__init__(children=children, parent=parent)
        self.items = items if items else []
        self.children = children if children else []
        for k, v in kwargs.items():
            setattr(self, k, v)

    def left_activation(self, token, wme, binding=None):
        """
        :type wme: WME
        :type token: Token
        :type binding: dict
        """
        new_token = Token(token, wme, node=self, binding=binding)
        self.items.append(new_token)

    def execute(self, *args, **kwargs):
        raise NotImplementedError