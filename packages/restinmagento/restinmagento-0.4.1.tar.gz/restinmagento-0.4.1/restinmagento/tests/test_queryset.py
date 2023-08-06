from collections import OrderedDict
import unittest


class TestQuerySet(unittest.TestCase):
    """Tests the QuerySet class.
    """
    def test_init(self):
        from restinmagento.collectionmanager import CollectionManager
        from restinmagento.model import Model
        from restinmagento.queryset import QuerySet
        from restinmagento.tests import create_default_backend
        backend = create_default_backend()
        cm = CollectionManager('/objects', inst_cls=Model)
        queryset = QuerySet(cm)
        self.assertEqual(cm, queryset.cm)
        self.assertEqual(list(), queryset._criterions)

    def test_clone(self):
        from restinmagento.collectionmanager import CollectionManager
        from restinmagento.model import Model
        from restinmagento.queryset import QuerySet
        from restinmagento.tests import create_default_backend
        backend = create_default_backend()
        cm = CollectionManager('/objects', inst_cls=Model)
        queryset1 = QuerySet(cm)
        queryset1._criterions = dict(toto='tata')
        queryset2 = queryset1._clone()
        self.assertNotEqual(queryset1, queryset2)
        self.assertEqual(cm, queryset1.cm)
        self.assertEqual(dict(toto='tata'), queryset1._criterions)

    def test_queryset_len(self):
        from restinmagento.collectionmanager import CollectionManager
        from restinmagento.model import Model
        from restinmagento.queryset import QuerySet
        from restinmagento.tests import create_default_backend
        backend = create_default_backend()
        backend.set_dictdata('objects',{'1': dict(toto='2', id_attr='1')})
        Model.id_attr = 'id_attr'
        Model.cm_path = '/objects'
        cm = CollectionManager('/objects', inst_cls=Model)
        queryset = QuerySet(cm)
        self.assertEqual(1, len(queryset))


    def test_queryset_iteration(self):
        from restinmagento.collectionmanager import CollectionManager
        from restinmagento.model import Model
        from restinmagento.queryset import QuerySet
        from restinmagento.tests import create_default_backend
        backend = create_default_backend()
        backend.set_dictdata('objects',{'1': dict(toto='2', id_attr='1')})
        Model.id_attr = 'id_attr'
        Model.cm_path = '/objects'
        cm = CollectionManager('/objects', inst_cls=Model)
        queryset = QuerySet(cm)
        for index, obj in enumerate(iter(queryset)):
            pass
        self.assertEqual(0, index)
        self.assertEqual('1', obj.pk)

    def test_simple_filtering(self):
        from restinmagento.collectionmanager import CollectionManager
        from restinmagento.model import Model
        from restinmagento.queryset import QuerySet
        from restinmagento.tests import create_default_backend
        backend = create_default_backend()
        backend.set_dictdata('objects',{'1': dict(toto='toto', id_attr='1'),
            '2': dict(toto='tata', id_attr='2')})
        Model.id_attr = 'id_attr'
        Model.cm_path = '/objects'
        cm = CollectionManager('/objects', inst_cls=Model)
        queryset = QuerySet(cm).filter(toto='toto')
        for index, obj in enumerate(iter(queryset)):
            pass
        self.assertEqual(0, index)
        self.assertEqual('1', obj.pk)


    def test_operator_filtering(self):
        from restinmagento.collectionmanager import CollectionManager
        from restinmagento.model import Product
        from restinmagento.operators import range_
        from restinmagento.queryset import QuerySet
        from restinmagento.tests import create_default_backend, mock
        backend = mock.Mock()
        data = [dict(toto='toto', entity_id='1')]
        backend.get.return_value = data
        create_default_backend(backend)
        cm = CollectionManager(path= '/products', inst_cls=Product)
        queryset = QuerySet(cm)
        result = [prod for prod in queryset.filter(range_('toto', 'toto', 'toto'))]
        self.assertEqual(1, len(result))
        product = result[0]
        self.assertEqual('toto', product.toto)
        params1={'limit': 100, 'page': 1, 'filter[0][attribute]': 'toto',
                'filter[0][from]': 'toto', 'filter[0][to]': 'toto'}
        params2={'limit': 100, 'page': 2, 'filter[0][attribute]': 'toto',
                'filter[0][from]': 'toto', 'filter[0][to]': 'toto'}
        expected_calls = [mock.call.get('/products', params=params1),
            mock.call.get('/products', params=params2)]
        self.assertEqual(expected_calls, backend.mock_calls)

    def test_raw_filter(self):
        from restinmagento.collectionmanager import CollectionManager
        from restinmagento.model import Model
        from restinmagento.queryset import QuerySet
        from restinmagento.tests import create_default_backend
        backend = create_default_backend()
        backend.set_dictdata('objects',{'1': dict(toto='toto', id_attr='1'),
            '2': dict(toto='tata', id_attr='2')})
        Model.id_attr = 'id_attr'
        Model.cm_path = '/objects'
        cm = CollectionManager('/objects', inst_cls=Model)
        criterion = {'filter[1][attribute]': 'id_attr',
                     'filter[1][in]': '1',}
        queryset = QuerySet(cm).raw_filter(criterion)
        for index, obj in enumerate(iter(queryset)):
            pass
        self.assertEqual(0, index)
        self.assertEqual('1', obj.pk)

    def test_simple_slicing(self):
        from restinmagento.collectionmanager import CollectionManager
        from restinmagento.model import Model
        from restinmagento.queryset import QuerySet
        from restinmagento.tests import create_default_backend
        backend = create_default_backend()
        backend.set_dictdata('objects',{'1': dict(toto='2', id_attr='1')})
        Model.id_attr = 'id_attr'
        Model.cm_path = '/objects'
        cm = CollectionManager('/objects', inst_cls=Model)
        queryset = QuerySet(cm)
        obj = queryset[0]
        self.assertEqual('1', obj.pk)
        
    def test_multiple_indice_slicing(self):
        from restinmagento.collectionmanager import CollectionManager
        from restinmagento.model import Model
        from restinmagento.queryset import QuerySet
        from restinmagento.tests import create_default_backend, mock
        backend = mock.Mock()
        data =  OrderedDict([('1', dict(toto='2', id_attr='1')),
                ('2', dict(toto='2', id_attr='2'))])
        backend.get.return_value = data
        create_default_backend(backend)
        Model.id_attr = 'id_attr'
        Model.cm_path = '/objects'
        cm = CollectionManager('/objects', inst_cls=Model)
        queryset = QuerySet(cm)
        obj = queryset[1:2][0]
        self.assertEqual('2', obj.pk)        


class TestQuerySetFiltering(unittest.TestCase):
    """Tests the QuerySet inner filtering operations.
    """

    def test_simple_filter(self):
        from restinmagento.operators import in_
        from restinmagento.queryset import QuerySet
        queryset = QuerySet(None)
        res = queryset.filter(toto='tata')
        criterion = in_('toto', 'tata')
        self.assertEqual([criterion], res._criterions)

    def test_in_filter(self):
        from restinmagento.operators import in_
        from restinmagento.queryset import QuerySet
        queryset = QuerySet(None)
        res = queryset.filter(in_('toto', 'tata'))
        criterion = in_('toto', 'tata')
        self.assertEqual([criterion], res._criterions)

    def test_notin_filter(self):
        from restinmagento.operators import notin_
        from restinmagento.queryset import QuerySet
        queryset = QuerySet(None)
        res = queryset.filter(notin_('toto', 'tata'))
        criterion = notin_('toto', 'tata')
        self.assertEqual([criterion], res._criterions)

    def test_order_by(self):
        from restinmagento.queryset import QuerySet
        queryset = QuerySet(None)
        res = queryset.order_by('name')
        self.assertEqual(dict(order='name', dir='asc'), res._raw_criterions)

    def test_order_by(self):
        from restinmagento.queryset import QuerySet
        queryset = QuerySet(None)
        res = queryset.order_by('name', direction='dsc')
        self.assertEqual(dict(order='name', dir='dsc'), res._raw_criterions)


        