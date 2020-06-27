class TestAtJoinNode:

    def __init__(self, field_of_arg1, condition_number_of_arg2, field_of_arg2):
        self.field_of_arg1 = field_of_arg1
        self.condition_number_of_arg2 = condition_number_of_arg2
        self.field_of_arg2 = field_of_arg2

    def __repr__(self):
        return "<TestAtJoinNode WME.%s=Condition%s.%s?>" % (
            self.field_of_arg1, self.condition_number_of_arg2, self.field_of_arg2)

    def __eq__(self, other):
        return isinstance(other, TestAtJoinNode) and \
               self.field_of_arg1 == other.field_of_arg1 and \
               self.field_of_arg2 == other.field_of_arg2 and \
               self.condition_number_of_arg2 == other.condition_number_of_arg2
