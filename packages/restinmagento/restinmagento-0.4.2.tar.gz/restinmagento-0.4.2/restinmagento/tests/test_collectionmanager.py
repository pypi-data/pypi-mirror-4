import unittest

#from restinmagento.collectionmanager import CollectionManager
#from restinmagento.tests import create_default_backend



class TestRawMethod(unittest.TestCase):
    """Tests the ResourceCollection's raw method
    """
    def test_raw_dict(self):
        """CM's raw method returns an emtpy dict 
        when the data of the backend is an empty dict.
        """
        from restinmagento.collectionmanager import CollectionManager
        from restinmagento.model import Model
        from restinmagento.tests import create_default_backend
        backend = create_default_backend()
        backend.set_dictdata('objects', dict())
        cm = CollectionManager('/objects', inst_cls=Model)
        self.assertEqual(dict(), cm.raw())

    def test_raw_list(self):
        """CM's raw method returns an emtpy list 
        when the data of the backend is an empty list.
        """
        from restinmagento.collectionmanager import CollectionManager
        from restinmagento.model import Model
        from restinmagento.tests import create_default_backend
        backend = create_default_backend()
        backend.set_listdata('objects', dict())
        cm = CollectionManager('/objects', inst_cls=Model)
        self.assertEqual(list(), cm.raw())

    def test_raw_returns_the_unmodified_data(self):
        from restinmagento.collectionmanager import CollectionManager
        from restinmagento.model import Model
        from restinmagento.tests import create_default_backend
        backend = create_default_backend()
        backend.set_dictdata('objects', dict(a=1))
        cm = CollectionManager('/objects', inst_cls=Model)
        self.assertEqual(dict(a=1), cm.raw())

    def test_pagination_and_limit(self):
        from restinmagento.collectionmanager import CollectionManager
        from restinmagento.model import Model
        from restinmagento.tests import create_default_backend
        data = [1, 2]
        backend = create_default_backend()
        backend.set_dictdata('objects', {item: item for item in data})
        cm = CollectionManager('/objects', inst_cls=Model)
        result1 = cm.raw(page=1, limit=1)
        self.assertEqual({1: 1}, result1)
        result2 = cm.raw(page=2, limit=1)
        self.assertEqual({2: 2}, result2)
        


class TestListMethod(unittest.TestCase):
    """Tests the ResourceCollection's list method
    """
    def test_list_returns_list_if_data_is_dict(self):
        from restinmagento.collectionmanager import CollectionManager
        from restinmagento.model import Model
        from restinmagento.tests import create_default_backend
        backend = create_default_backend()
        backend.set_dictdata('objects', dict(a=1))
        cm = CollectionManager('/objects', inst_cls=Model)
        self.assertEqual([1], cm.list())

    def test_list_returns_list_if_data_is_list(self):
        from restinmagento.collectionmanager import CollectionManager
        from restinmagento.model import Model
        from restinmagento.tests import create_default_backend
        backend = create_default_backend()
        backend.set_listdata('objects', dict(a=1))
        cm = CollectionManager('/objects', inst_cls=Model)
        self.assertEqual([1], cm.list())

    def test_buffering(self):
        from restinmagento.collectionmanager import CollectionManager
        from restinmagento.model import Model
        from restinmagento.tests import create_default_backend
        backend = create_default_backend()
        backend.set_dictdata('objects', dict(a=1, b=2, c=3))
        cm = CollectionManager('/objects', inst_cls=Model)
        result = cm.list(buffer=1)
        self.assertEqual(3, len(result))
        for item in [1, 2, 3]:
            self.assertIn(item, result)

    def test_maxitems_with_buffer(self):
        from restinmagento.collectionmanager import CollectionManager
        from restinmagento.model import Model
        from restinmagento.tests import create_default_backend
        backend = create_default_backend()
        backend.set_dictdata('objects', dict(a=1, b=2, c=3))
        cm = CollectionManager('/objects', inst_cls=Model)
        result = cm.list(buffer=1, maxitems=2)
        self.assertEqual(2, len(result))
        for item in result:
            self.assertIn(item, [1, 2, 3])
        
        
class TestGetMethod(unittest.TestCase):
    """Tests the ResourceCollection's get method
    """
    def test_get(self):
        from restinmagento.collectionmanager import CollectionManager
        from restinmagento.model import Model
        from restinmagento.tests import create_default_backend
        backend = create_default_backend()
        backend.set_dictdata('objects',{'1': dict(toto='2', id_attr='1')})
        Model.id_attr = 'id_attr'
        Model.cm_path = '/objects'
        cm = CollectionManager('/objects', inst_cls=Model)
        model  = cm.get('1')
        self.assertIsInstance(model, Model)
        self.assertEqual('2', model.toto)
        self.assertEqual(False, model.transient)
        Model.id_attr = None
        Model.cm_path = None
        


class TestCreateMethod(unittest.TestCase):
    """Tests the ResourceCollection's create method
    """
    def test_create(self):
        from restinmagento.collectionmanager import CollectionManager
        from restinmagento.model import Model
        from restinmagento.tests import create_default_backend, mock
        backend = mock.Mock()
        backend.create.return_value = '/objects/1'
        backend.get.return_value = dict(toto='2', id_attr='1')
        create_default_backend(backend)
        Model.id_attr = 'id_attr'
        Model.cm_path = '/objects'
        cm = CollectionManager('/objects', inst_cls=Model)
        model = cm.create(data=dict(toto='2'))
        self.assertIsInstance(model, Model)
        self.assertEqual('1', model.pk)
        self.assertEqual('/objects/1', model.path)
        self.assertEqual('2', model.toto)
        Model.id_attr = None
        Model.cm_path = None
        

    def test_create_also_populates_default_attibutes(self):
        from restinmagento.collectionmanager import CollectionManager
        from restinmagento.model import Model
        from restinmagento.tests import create_default_backend, mock
        backend = mock.Mock()
        backend.create.return_value = '/objects/1'
        backend.get.return_value = dict(toto='2', tata='3', id_attr=1)
        create_default_backend(backend)
        Model.id_attr = 'id_attr'
        Model.cm_path = '/objects'
        cm = CollectionManager('/objects', inst_cls=Model)
        model = cm.create(data=dict(toto='2'))
        self.assertEqual('3', model.tata)
        Model.id_attr = None
        Model.cm_path = None

class TestAllMethod(unittest.TestCase):
    """Tests the ResourceCollection's all method
    """
    def test_all(self):
        from restinmagento.collectionmanager import CollectionManager
        from restinmagento.model import Model
        from restinmagento.tests import create_default_backend
        backend = create_default_backend()
        backend.set_dictdata('objects', {'1': dict(entity_id='1', name='toto')})
        Model.id_attr = 'entity_id'
        Model.cm_path = '/objects'
        cm = CollectionManager('/objects', inst_cls=Model)
        models = cm.all()
        self.assertEqual(1, len(models))
        model = models[0]
        self.assertIsInstance(model, Model)
        self.assertEqual('1', model.pk)
        self.assertEqual('/objects/1', model.path)
        self.assertEqual('toto', model.name)
        Model.id_attr = None
        Model.cm_path = None


class TestImageCollectionManager(unittest.TestCase):
    """Tests ImageCollectionManager
    """
    def test_initialization(self):
        from restinmagento.collectionmanager import ImageCollectionManager
        from restinmagento.model import Image
        cm = ImageCollectionManager(product_id=1, inst_cls=Image)
        self.assertEqual("/products/1/images", cm.path)

    def test_list(self):
        from restinmagento.collectionmanager import ImageCollectionManager
        from restinmagento.model import Image
        from restinmagento.tests import create_default_backend, mock
        backend = mock.Mock()
        image_list = [{u'exclude': u'0',
            u'id': u'610',
            u'label': u'',
            u'position': u'1',
            u'types': [u'image', u'small_image', u'thumbnail'],
            u'url': u'http://whateverhost.com/media/toto.jpg'}]
        backend.get.return_value = image_list
        create_default_backend(backend)
        cm = ImageCollectionManager(product_id=1, inst_cls=Image)
        self.assertEqual(image_list, cm.list())
        expected_calls = [mock.call.get('/products/1/images', params={'limit': 100, 'page': 1}),
            mock.call.get('/products/1/images', params={'limit': 100, 'page': 2})]
        self.assertEqual(expected_calls, backend.mock_calls)

    def test_all(self):
        from restinmagento.collectionmanager import ImageCollectionManager
        from restinmagento.model import Image
        from restinmagento.tests import create_default_backend, mock
        backend = mock.Mock()
        image_list = [{u'exclude': u'0',
            u'id': u'610',
            u'label': u'',
            u'position': u'1',
            u'types': [u'image', u'small_image', u'thumbnail'],
            u'url': u'http://whateverhost.com/media/toto.jpg'}]
        backend.get.return_value = image_list
        create_default_backend(backend)
        cm = ImageCollectionManager(product_id=1, inst_cls=Image)
        image = cm.all()[0]
        self.assertIsInstance(image, Image)
        self.assertEqual('/products/1/images/610', image.path)
        self.assertEqual('610', image.pk)
        self.assertEqual('1', image.position)
        self.assertEqual(u'http://whateverhost.com/media/toto.jpg', image.url)

    def test_obtain_cm_from_img_class(self):
        from restinmagento.collectionmanager import ImageCollectionManager
        from restinmagento.model import Image
        self.assertIsInstance(Image.objects(product_id=1), ImageCollectionManager)



        


        