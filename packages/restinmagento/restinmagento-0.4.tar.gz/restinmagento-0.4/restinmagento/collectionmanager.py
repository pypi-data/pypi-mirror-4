"""
"""
import sys

from restinmagento.backend import BackEndRegistry
from restinmagento import compat
from restinmagento.queryset import QuerySet


class CollectionManager(object):
    """Provides operations to work on a collection of model objects.
    Usually you don't instanciate a collection manager, you access it through the 
    `objects` property of a Model.
    """
    
    def __init__(self, path, inst_cls, backend='default'):
        self.backend = getattr(BackEndRegistry(), backend)
        self.path = path
        self.inst_cls = inst_cls

    def raw(self, page=1, limit=10, criterions=dict()):
        """Return the raw deserialze json data returned by the server in response to a GET request.
        The returned data can be a dict or a list depending on the type of resources.

        :param page: Magento splits its data in `pages`
        :param limit: Number of objects contained in a page
        """       
        params=dict(page=page, limit=limit)
        params.update(criterions)
        return self.backend.get(self.path, params=params)

    def list(self, maxitems=compat.maxint, buffer=100, criterions=dict()):
        """Return a list of dictionnary object.

        It takes care of iterating trough every `page` for you.

        :param maxitems: Maximum number of objects you want in the response.
        :param buffer: Number of objects buffered in each reponse of the server.
        """
        result = list()
        page = 1
        prev_items = None
        while 1:
            items = self.raw(page, limit=buffer, criterions=criterions)
            if isinstance(items, dict):
                items = items.values()
                if not isinstance(items, list):
                    items = list(items)
            if prev_items == items:
                break
            result.extend(items)
            if len(result) >= maxitems:
                break
            page += 1
            prev_items = items
        if len(result) > maxitems:
            result = result[:maxitems]
        return result
        

    def all(self, maxitems=compat.maxint, buffer=100, criterions=dict()):
        """Returns the list of every resource instances.

        :param maxitems: Maximum number of objects you want in the response.
        :param buffer: Number of objects buffered in each reponse of the server.
        """
        result = list()
        for resource in self.list(maxitems, buffer, criterions):
            inst = self._create_instance(resource)
            inst.persist()
            result.append(inst)
        return result
            
    def filter(self, *args, **kwargs):
        """Filter the queryset with the given argument or criterion

        :param criterion: the filtering criterion
        :type criterion: See :ref:`operators_module`
        """
        queryset = QuerySet(self)
        return queryset.filter(*args, **kwargs)

    def raw_filter(self, raw_filters):
        """Lets you specify raw filtering criterion as you would directionif you were directly
        interacting with a Magento server.
        See http://www.magentocommerce.com/api/rest/get_filters.html.

        :param raw_crit: the filtering criterion
        :type raw_crit: a dictionnary
        """
        queryset = QuerySet(self)
        return queryset.raw_filter(raw_filters)

    def order_by(self, attr, direction='asc'):
        """Orders the result by attr.

        :param direction: direction of the sort. Can be 'asc' or 'dsc'.
        """
        queryset = QuerySet(self)
        return queryset.order_by(attr, direction)

    def _create_instance(self, data):
        """Factory method that creates an instance
        of a resource.
        """
        return self.inst_cls(data=data)

    def get(self, pk):
        """Get the object whose primary key is pk.

        Example:

        .. code-block:: python
            :linenos:

            from restinmagento.model import Product

            product = Product.objects.get(pk='12')
        """
        path = self._get_resource_suffix(pk)
        obj_dict = self.backend.get(path)
        inst = self._create_instance(obj_dict)
        inst.persist()
        return inst

    def create(self, data):
        """Creates an instance, save it to the backend and returns it.

        Example:

        .. code-block:: python
            :linenos:

            from restinmagento.model import Product

            product = Product.objects.create(data=dict(name='myproduct',..))
        """
        inst = self._create_instance(data)
        inst.save()
        return inst
        
    def _get_resource_suffix(self, pk):
        return "%s/%s" % (self.path, pk)

 
class ImageCollectionManager(CollectionManager):
    """Collection of images related to a given product.
    """

    def __init__(self, product_id, inst_cls, backend='default'):
        self.product_id = product_id
        path = "/products/%s/images" % product_id
        super(ImageCollectionManager, self).__init__(path, inst_cls, backend)

    def _create_instance(self, data):
        return self.inst_cls(product_id=self.product_id, data=data)
        
