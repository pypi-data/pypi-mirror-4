"""Tests operators
"""

import unittest

class TestOperators(unittest.TestCase):

    def test_not_(self):
        from restinmagento.operators import not_
        op = not_('name', 'dummy_name')
        expected_result = {'filter[0][attribute]': 'name', 'filter[0][neq]': 'dummy_name'}
        self.assertEqual(expected_result, op.serialize(0))

    def test_notin_(self):
        from restinmagento.operators import notin_
        op = notin_('name', 'dummy_name')
        expected_result = {'filter[0][attribute]': 'name', 'filter[0][nin]': 'dummy_name'}
        self.assertEqual(expected_result, op.serialize(0))

    def test_gt_(self):
        from restinmagento.operators import gt_
        op = gt_('name', 'dummy_name')
        expected_result = {'filter[0][attribute]': 'name', 'filter[0][gt]': 'dummy_name'}
        self.assertEqual(expected_result, op.serialize(0))
    
    def test_lt_(self):
       from restinmagento.operators import lt_
       op = lt_('name', 'dummy_name')
       expected_result = {'filter[0][attribute]': 'name', 'filter[0][lt]': 'dummy_name'}
       self.assertEqual(expected_result, op.serialize(0))

    def test_range_(self):
       from restinmagento.operators import range_
       op = range_('name', 'dummy_name1', 'dummy_name2')
       expected_result = {'filter[0][attribute]': 'name', 
        'filter[0][from]': 'dummy_name1',
        'filter[0][to]': 'dummy_name2'}
       self.assertEqual(expected_result, op.serialize(0))

    def test_in_(self):
       from restinmagento.operators import in_
       op = in_('name', 'dummy_name')
       expected_result = {'filter[0][attribute]': 'name', 
        'filter[0][in]': 'dummy_name'}
       self.assertEqual(expected_result, op.serialize(0))

    def test_operator_equality(self):
        from restinmagento.operators import Operator
        op1 = Operator('name', 'dummy_name')
        op2 = Operator('name', 'dummy_name')
        self.assertEqual(op1, op2)
    