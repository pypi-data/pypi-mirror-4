"""Operators to fiter a queryset
"""


class Operator(object):
    """Baseclass for an operator
    """

    def __init__(self, attribute, value):
        self.attribute = attribute
        self.value = value

    def __eq__(self, other):
        return self.attribute == other.attribute \
            and self.value == other.value

    __hash__ = object.__hash__

    def serialize(self, index):
        base_key = "filter[%s]" %index
        key1 = base_key + '[attribute]'
        key2 = base_key + '[%s]' % self.op_str
        return {key1: self.attribute, key2: self.value}


class not_(Operator):
    """Not equal operator.
    Filter objects whose attribute is not equal to value.
    """

    op_str = "neq"

class in_(Operator):
    """In operator.
    Filter objects whose attribute is 'in'  value.
    """

    op_str = "in"

class notin_(Operator):
    """Not in operator.
    Filter objects whose attribute is not 'in'  value.
    """

    op_str = "nin"

class gt_(Operator):
    """Greater than operator.
    Filter objects whose attribute is greater than value.
    """

    op_str = "gt"

class lt_(Operator):
    """Lesser than operator.
    Filter objects whose attribute is lesser than value.
    """

    op_str = "lt"

class range_(Operator):
    """Range operator.
    Filter objects whose attribute greater than low_limit,
    and lesser than up_limit.
    """

    def __init__(self, attribute, low_limit, up_limit):
        self.attribute = attribute
        self.low_limit = low_limit
        self.up_limit = up_limit

    def serialize(self, index):
        base_key = "filter[%s]" %index
        key1 = base_key + '[attribute]'
        key2 = base_key + '[from]'
        key3 = base_key + '[to]'
        return {key1: self.attribute, key2: self.low_limit, key3: self.up_limit}
        