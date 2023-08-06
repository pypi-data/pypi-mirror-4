"""
"""
import collections

from restinmagento.resource import Resource

class BackEndRegistry(object):

    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state

    def get_backend(self, name):
        return self.name

    def get_default_backend(self):
        return self.default

    def set_backend(self, name, backend):
        self.name = backend

    def set_default_backend(self, backend):
        self.default = backend


class BackEnd(object):

    def __init__(self, name, url, oauth):
        self.name = name
        self.url = url
        self.oauth = oauth

    def _get_url(self, path):
        return "%s%s" % (self.url, path)

    def _call(self, segments, request_meth, **kwargs):
        url = self._get_url(segments)
        resource = Resource(url, self.oauth)
        meth = getattr(resource, request_meth)
        response = meth(**kwargs)
        result = response.json(object_pairs_hook=collections.OrderedDict)
        return result

    def get(self, segments, **kwargs):
        return self._call(segments, 'get', **kwargs)

    def put(self, path, data):
        url = self._get_url(path)
        resource = Resource(url, self.oauth)
        response = resource.put(data)
        return 

    def create(self, path, data):
        """Creates a new object by issuing a POST request on the resource.
        """
        url = self._get_url(path)
        resource = Resource(url, self.oauth)
        response  = resource.post(data)
        location = response.headers['location']
        segments = location.split('/')
        segments = segments[3:]
        return "/%s" % ('/'.join(segments))

    def delete(self, path):
        url = self._get_url(path)
        resource = Resource(url, self.oauth)
        response = resource.delete()
        

def set_default_backend(url, oauth):
    registry = BackEndRegistry()
    registry.set_default_backend(
        BackEnd('default', url, oauth))

def get_default_backend():
    registry = BackEndRegistry()
    return registry.default
    
    
