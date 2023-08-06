"""resource module that expose the Resource class.
"""

import requests
import simplejson

class RIMException(Exception):
    pass

class Resource(object):
    """A Resource is defined by its url and oauth tokens.
    It provides a straightforward API to manipulate a resource through standard 
    get, post, put and delete methods.
    """

    def __init__(self, url, oauth):
        self.url = url
        self.oauth =  oauth
        self._response = None

    def _handle_error(self):
        """Raise an exception to notify that an error append.
        """
        error_dict = self._response.json()['messages']['error'][0]
        raise RIMException("Error %(code)s: %(message)s" % error_dict)

    def _call(self, request_meth, **kwargs):
        """Perform the HTTP query, using the request_meth callable.
        """
        self._response = request_meth(url=self.url, auth=self.oauth, 
            headers = {'Content-Type': 'application/json', 'Content_Type': 'application/json', 
            'Accept': 'application/json'}, **kwargs)
        if self._response.status_code != 200:
            self._handle_error()
        return self._response

    def get(self, **kwargs):
        """HTTP GET method on the resource.
        params is a dictionnary of GET parameters.
        """
        return self._call(requests.get, **kwargs) 
    
    def put(self, data, **kwargs):
        """HTTP PUT method on the resource
        """
        return self._call(requests.put, data=simplejson.dumps(data), **kwargs)

    def post(self, data=None, **kwargs):
        """HTTP PUT method on the resource
        """
        return self._call(requests.post, data=simplejson.dumps(data), **kwargs)

    def delete(self, **kwargs):
        """HTTP DELTE method on the resource
        """
        return self._call(requests.delete, **kwargs)

        
