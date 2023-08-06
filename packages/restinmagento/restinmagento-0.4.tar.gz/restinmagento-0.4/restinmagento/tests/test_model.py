"""Test the testutils functions and classes.
"""

import unittest


class TestModel(unittest.TestCase):
    """Tests the Model class.
    """

    def test_instanciation_with_random_attribute(self):
        from restinmagento.model import Model
        model = Model(foo='bar')
        self.assertEqual('bar', model.foo)
        self.assertEqual(dict(), model.data)

    def test_instanciation_with_data_keyword(self):
        from restinmagento.model import Model
        model = Model(data=dict(foo='bar'))
        self.assertEqual('bar', model.foo)
        self.assertEqual(dict(foo='bar'), model.data)        

    def test_save_method_on_transient_object(self):
        from restinmagento.model import Model
        from restinmagento.tests import create_default_backend, mock
        backend = mock.Mock()
        backend.create.return_value = '/objects/1'
        backend.get.return_value = dict(toto='2')
        create_default_backend(backend)
        Model.cm_path = '/objects'
        model = Model(data=dict(toto='2'))
        model.save()
        expected_calls = [mock.call.create('/objects', dict(toto='2')),
            mock.call.get('/objects/1')]
        self.assertEqual(expected_calls, backend.mock_calls)
        self.assertEqual('1', model.pk)
        self.assertEqual('/objects/1', model.path)
        self.assertEqual('2', model.toto)
        Model.cm_path = None

    def test_save_method_on_persistent_object(self):
        """Only send to the backend the data that need to be updated.
        """
        from restinmagento.model import Model
        from restinmagento.tests import create_default_backend, mock
        backend = mock.Mock()
        create_default_backend(backend)
        model = Model(data=dict(toto='2', tata='tata'))
        model.transient = False
        model.pk = '1'
        model.tata = 'aa'
        Model.cm_path  = '/objects'
        model.save(reload=False)
        expected_calls = [mock.call.put('/objects/1', dict(tata='aa'))]
        self.assertEqual(expected_calls, backend.mock_calls)
        Model.cm_path = None

    def test_raise_attribute_exception(self):
        """Accessing an unkown attribute must raise an Attribute,
        which is not granted as mess with attribute access.
        """
        from restinmagento.model import Model
        model = Model()
        self.assertRaises(AttributeError, getattr, model, 'toto')

    def test_special_attributes(self):
        """These attributes must never populate model.attrs
        """
        attrs = ('pk', 'transient')
        from restinmagento.model import Model
        model = Model()
        model.pk = '1'
        model.transient = True
        for attr in attrs:
            self.assertNotIn(attr, model.data)

    def test_set_unknown_attribute_on_persistent_obj(self):
        """A persistent model knows what attributes are supported by the backend.
        Setting an unkown attribute is allowed but must not populate model._attrs,
        neither model._updated_atttrs.
        """
        from restinmagento.model import Model
        model = Model(data=dict(toto='2'))
        model.transient = False
        model.tata = 'tata'
        self.assertEqual('tata', model.tata)
        self.assertNotIn('tata', model.data)

    def test_set_known_attribute_on_persistent_obj(self):
        """A persistent model knows what attributes are supported by the backend.
        Setting a kown attribute must affect only model._updated_attrs.
        """
        from restinmagento.model import Model
        Model.cm_path = '/objects'
        model = Model(data=dict(toto='2'))
        model.transient = False        
        model.toto = '0'
        self.assertEqual('0', model.toto)
        self.assertIn('toto', model.updated_data)
        self.assertNotIn('toto', model.__dict__)
        
    def test_set_unkown_attribute_on_transient_obj(self):
        """The attribute must nost end in obj.data
        """
        from restinmagento.model import Model
        model = Model()
        model.toto = 'toto'
        self.assertNotIn('toto', model.data)
        self.assertIn('toto', model.__dict__)
        self.assertEqual('toto', model.toto)

    def test_persist(self):
        """Test the persist method.
        """
        from restinmagento.model import Model
        Model.id_attr = 'id_attr'
        Model.cm_path = '/objects'
        model = Model(data=dict(id_attr='1'))
        model.persist()
        self.assertEqual('/objects/1', model.path)
        self.assertEqual('1', model.pk)
        self.assertEqual(False, model.transient)
        Model.id_attr = None
        Model.cm_path = None
        

class TestModelState(unittest.TestCase):
    """Tests the Model states.
    """

    def test_transcient_state_on_instanciation(self):
        from restinmagento.model import Model
        model = Model(foo='bar')
        self.assertTrue(model.transient)


class TestDeleteMethod(unittest.TestCase):
    """Tests the Model delete method.
    """

    def test_transcient_state_on_instanciation(self):
        from restinmagento.model import Model
        from restinmagento.tests import create_default_backend, mock
        backend = mock.Mock()
        create_default_backend(backend)
        model = Model()
        model.transient = False
        model.pk = '1'
        model.cm_path = '/objects'
        backend.delete.return_value = None
        model.delete()
        expected_calls = [mock.call.delete('/objects/1')]
        self.assertEqual(expected_calls, backend.mock_calls)
        model.cm_path = 'None'


class TestReloadMethod(unittest.TestCase):
    """Tests the Model reload method.
    """

    def test_reload_raise_exception_if_transient(self):
        from restinmagento.model import Model, ModelException
        from restinmagento.tests import create_default_backend, mock
        backend = mock.Mock()
        create_default_backend(backend)
        model = Model()
        model.transient = True
        model.pk = '1'
        model.cm_path = '/objects'
        self.assertRaises(ModelException, model.reload)
        model.cm_path = 'None'

    def test_reload_populates_data(self):
        from restinmagento.model import Model, ModelException
        from restinmagento.tests import create_default_backend, mock
        backend = mock.Mock()
        backend.get.return_value = dict(toto="toto")
        create_default_backend(backend)
        model = Model()
        model.transient = False
        model.pk = '1'
        model.cm_path = '/objects'
        model.reload()
        self.assertEqual("toto", model.toto)
        model.cm_path = 'None'


class TestProduct(unittest.TestCase):
    """Test the product class
    """

    def test_get_websites(self):
        from restinmagento.tests import create_default_backend, mock
        from restinmagento.model import Product
        prod = Product(data=dict())
        prod.pk = '1'
        prod.transient = False
        backend = mock.Mock()
        create_default_backend(backend)
        backend.get.return_value = [{"website_id":"1"}]
        expected_calls = [mock.call.get('/products/1/websites')]
        self.assertEqual(['1'], prod.get_websites())
        self.assertEqual(expected_calls, backend.mock_calls)

    def test_set_websites(self):
        from restinmagento.tests import create_default_backend, mock
        from restinmagento.model import Product
        prod = Product(data=dict())
        prod.pk = '1'
        prod.transient = False
        backend = mock.Mock()
        create_default_backend(backend)
        expected_calls = [mock.call.post('/products/1/websites', data=[{"website_id":"1"}])]
        prod.set_websites(['1'])
        self.assertEqual(expected_calls, backend.mock_calls)

    def test_get_categories(self):
        from restinmagento.tests import create_default_backend, mock
        from restinmagento.model import Product
        prod = Product(data=dict())
        prod.pk = '1'
        prod.transient = False
        backend = mock.Mock()
        create_default_backend(backend)
        backend.get.return_value = [{'category_id': '8'}]
        expected_calls = [mock.call.get('/products/1/categories')]
        self.assertEqual(['8'], prod.get_categories())
        self.assertEqual(expected_calls, backend.mock_calls)

    def test_set_categories(self):
        from restinmagento.tests import create_default_backend, mock
        from restinmagento.model import Product
        prod = Product(data=dict())
        prod.pk = '1'
        prod.transient = False
        backend = mock.Mock()
        create_default_backend(backend)
        expected_calls = [mock.call.post('/products/1/categories', data={'category_id': '8'})]
        prod.set_categories('8')
        self.assertEqual(expected_calls, backend.mock_calls)

    def test_get_images_collection_manager(self):
        from restinmagento.collectionmanager import ImageCollectionManager
        from restinmagento.model import Product
        prod = Product(data=dict())
        prod.pk = '1'
        prod.transient = False
        images = prod.images
        self.assertIsInstance(images, ImageCollectionManager)
        self.assertEqual('/products/1/images', images.path)
       
       
class TestProductImage(unittest.TestCase):
    """Tests the Image class.
    """
    
    def test_initialization_without_data(self):
        from restinmagento.model import Image
        image = Image(product_id='1', data=dict())
        self.assertEqual('1', image.product_id)
        self.assertNotIn('product_id', image.data)
        self.assertTrue(image.transient)

    def test_initialization_with_data(self):
        from restinmagento.model import Image
        image = Image(product_id='1', data=dict(toto='toto'))
        self.assertEqual('toto', image.toto)
        self.assertIn('toto', image.data)
        self.assertNotIn('toto', image.__dict__)

    def test_cm_path(self):
        from restinmagento.model import Image
        image = Image(product_id='1')
        self.assertEqual('/products/1/images', image.cm_path)
        
    def test_save(self):
        from restinmagento.model import Image
        from restinmagento.tests import create_default_backend, mock
        backend = mock.Mock()
        backend.create.return_value = '/products/1/images/1'
        backend.get.return_value = dict(dummy='aa')
        create_default_backend(backend)
        image = Image(product_id='1', data=dict(toto='toto'))
        image.save(reload=False)
        expected_calls = [mock.call.create('/products/1/images', {'toto': 'toto'})]
        self.assertEqual(expected_calls, backend.mock_calls)


class TestOrder(unittest.TestCase):
    """Test the order class
    """

    def test_addresses(self):
        from restinmagento.tests import create_default_backend, mock
        from restinmagento.model import Order
        order = Order(data=dict())
        order.pk = '1'
        order.transient = False
        backend = mock.Mock()
        create_default_backend(backend)
        data = [{u'address_type': u'billing',
                 u'city': u'TAMPON',
                 u'company': None,
                 u'country_id': u'RE',
                 u'email': u'toto@gmail.com',
                 u'firstname': u'Stephane',
                 u'lastname': u'TONTON',
                 u'middlename': None,
                 u'postcode': u'97430',
                 u'prefix': None,
                 u'region': None,
                 u'street': u'185, rue du docteur gerard',
                 u'suffix': None,
                 u'telephone': u'0606060606'},
                {u'address_type': u'shipping',
                 u'city': u'TAMPON',
                 u'company': None,
                 u'country_id': u'RE',
                 u'email': u'toto@gmail.com',
                 u'firstname': u'Stephane',
                 u'lastname': u'TONTON',
                 u'middlename': None,
                 u'postcode': u'97430',
                 u'prefix': None,
                 u'region': None,
                 u'street': u'185, rue du docteur gerard',
                 u'suffix': None,
                 u'telephone': u'0606060606'}]

        backend.get.return_value = data
        expected_calls = [mock.call.get('/orders/1/addresses')]
        self.assertEqual(data, order.addresses)

    def test_billing_addresses(self):
        from restinmagento.tests import create_default_backend, mock
        from restinmagento.model import Order
        order = Order(data=dict())
        order.pk = '1'
        order.transient = False
        backend = mock.Mock()
        create_default_backend(backend)
        data = {u'address_type': u'billing',
                 u'city': u'TAMPON',
                 u'company': None,
                 u'country_id': u'RE',
                 u'email': u'toto@gmail.com',
                 u'firstname': u'Stephane',
                 u'lastname': u'TONTON',
                 u'middlename': None,
                 u'postcode': u'97430',
                 u'prefix': None,
                 u'region': None,
                 u'street': u'185, rue du docteur gerard',
                 u'suffix': None,
                 u'telephone': u'0606060606'}

        backend.get.return_value = data
        expected_calls = [mock.call.get('/orders/1/addresses/billing')]
        self.assertEqual(data, order.billing_addresses)

    def test_shipping_addresses(self):
        from restinmagento.tests import create_default_backend, mock
        from restinmagento.model import Order
        order = Order(data=dict())
        order.pk = '1'
        order.transient = False
        backend = mock.Mock()
        create_default_backend(backend)
        data = {u'address_type': u'shipping',
                 u'city': u'TAMPON',
                 u'company': None,
                 u'country_id': u'RE',
                 u'email': u'toto@gmail.com',
                 u'firstname': u'Stephane',
                 u'lastname': u'TONTON',
                 u'middlename': None,
                 u'postcode': u'97430',
                 u'prefix': None,
                 u'region': None,
                 u'street': u'185, rue du docteur gerard',
                 u'suffix': None,
                 u'telephone': u'0606060606'}

        backend.get.return_value = data
        expected_calls = [mock.call.get('/orders/1/addresses/shipping')]
        self.assertEqual(data, order.shipping_addresses)

    def test_comments(self):
        from restinmagento.tests import create_default_backend, mock
        from restinmagento.model import Order
        order = Order(data=dict())
        order.pk = '1'
        order.transient = False
        backend = mock.Mock()
        create_default_backend(backend)
        data = [{u'comment': None,
                 u'created_at': u'2012-04-29 03:57:38',
                 u'is_customer_notified': u'0',
                 u'is_visible_on_front': u'0',
                 u'status': u'pending_payment'},
                {u'comment': None,
                 u'created_at': u'2012-04-29 03:59:17',
                 u'is_customer_notified': u'2',
                 u'is_visible_on_front': u'0',
                 u'status': u'canceled'}]

        backend.get.return_value = data
        expected_calls = [mock.call.get('/orders/1/comments')]
        self.assertEqual(data, order.comments)

    def test_items(self):
        from restinmagento.tests import create_default_backend, mock
        from restinmagento.model import Order
        order = Order(data=dict())
        order.pk = '1'
        order.transient = False
        backend = mock.Mock()
        create_default_backend(backend)
        data = [{u'base_discount_amount': u'0.0000',
                 u'base_original_price': u'0.5000',
                 u'base_price': u'0.5000',
                 u'base_price_incl_tax': u'0.6000',
                 u'base_row_total': u'2.5000',
                 u'base_row_total_incl_tax': u'3.0000',
                 u'base_tax_amount': u'0.5000',
                 u'discount_amount': u'0.0000',
                 u'item_id': u'70',
                 u'name': u'Some item',
                 u'original_price': u'0.5000',
                 u'parent_item_id': None,
                 u'price': u'0.5000',
                 u'price_incl_tax': u'0.6000',
                 u'qty_canceled': u'5.0000',
                 u'qty_invoiced': u'0.0000',
                 u'qty_ordered': u'5.0000',
                 u'qty_refunded': u'0.0000',
                 u'qty_shipped': u'0.0000',
                 u'row_total': u'2.5000',
                 u'row_total_incl_tax': u'3.0000',
                 u'sku': u'fsjsvsnvln',
                 u'tax_amount': u'0.5000',
                 u'tax_percent': u'19.6000'}]

        backend.get.return_value = data
        expected_calls = [mock.call.get('/orders/1/items')]
        self.assertEqual(data, order.items)











        
