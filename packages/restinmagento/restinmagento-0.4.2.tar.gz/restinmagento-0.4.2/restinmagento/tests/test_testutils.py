"""Test the tests functions and classes.
"""

import unittest

class TestFakeBackEnd(unittest.TestCase):
    """Tests the FakeBackEnd class.
    """

    def test_get_empty_dict(self):
        from restinmagento.tests import FakeBackEnd
        fb = FakeBackEnd()
        fb.set_dictdata('objects', dict())
        self.assertEqual(dict(), fb.get('/objects'))

    def test_get_empty_list(self):
        from restinmagento.tests import FakeBackEnd
        fb = FakeBackEnd()
        fb.set_listdata('objects', dict())
        self.assertEqual(list(), fb.get('/objects'))

    def test_get_dictcollection(self):
        from restinmagento.tests import FakeBackEnd
        fb = FakeBackEnd()
        fb.set_dictdata('objects', {'1': 1})
        self.assertEqual({'1': 1}, fb.get('/objects'))

    def test_get_listcollection(self):
        from restinmagento.tests import FakeBackEnd
        fb = FakeBackEnd()
        fb.set_listdata('objects', {'1': 1})
        self.assertEqual([1], fb.get('/objects'))

    def test_limit(self):
        from restinmagento.tests import FakeBackEnd
        fb = FakeBackEnd()
        fb.set_dictdata('objects', {value: value for value in range(10)})
        self.assertEqual({0: 0, 1: 1}, fb.get('/objects', params=dict(limit=2)))

    def test_last_page_returned_if_out_of_page(self):
        from restinmagento.tests import FakeBackEnd
        fb = FakeBackEnd()
        fb.set_dictdata('objects', {value: value for value in range(10)})
        self.assertEqual({8: 8, 9: 9}, fb.get('/objects', params=dict(page=100, limit=2)))

    def test_get_single_obj(self):
        from restinmagento.tests import FakeBackEnd
        fb = FakeBackEnd()
        fb.set_dictdata('objects', {'1': 1, '2': 2})
        self.assertEqual(1, fb.get('/objects/1'))

    def test_filtering(self):
        from restinmagento.tests import FakeBackEnd
        fb = FakeBackEnd()
        fb.set_dictdata('objects', {'1': dict(entity_id='1', name='tata'), 
            '2': dict(entity_id='2', name='toto')})
        params={'filter[0][attribute]': 'name',
                'filter[0][in]': 'tata'}
        self.assertEqual({'1': dict(entity_id='1', name='tata')}, fb.get('/objects', params=params))




class TestParseCriterion(unittest.TestCase):


    def test(self):
        from restinmagento.tests import parse_criterion
        criterion = {'filter[0][attribute]': 'name', 'filter[0][in]': 'tata'}
        self.assertEqual({'name': 'tata'}, parse_criterion(criterion))