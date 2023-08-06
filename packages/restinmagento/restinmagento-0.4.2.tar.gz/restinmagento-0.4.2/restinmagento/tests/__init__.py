"""Utility classes and function to ease unit testing
"""
from collections import defaultdict
import sys

from restinmagento.backend import BackEndRegistry


# True if we are running on Python 3.
PY3 = sys.version_info[0] == 3

if PY3:
    import unittest.mock as mock
else:
    import mock
    

def parse_criterion(get_params):
    """Transform some magento get filters in
    a dict friendly form.
    >>>parse_criterion({'filter[0][attribute]': 'name', 'filter[0][in]': 'tata'})
    {'name': 'tata'}
    """
    tmp_result = defaultdict(dict)
    for key, value in get_params.items():
        if key not in ('page', 'limit'):
            crit_num = key[7:8]
            discr = key[10:12]
            if discr == 'in':
                tmp_result[crit_num]['value'] = value
            else:
                tmp_result[crit_num]['attr'] = value
    result = dict()
    for crit_dict in tmp_result.values():
        result[crit_dict['attr']] = crit_dict['value']
    return result


def apply_filters(data, params):
    crit_dict = parse_criterion(params)
    for key, value in data.items():
        match = True
        for attr, attr_value in crit_dict.items():
            if value[attr] != attr_value:
                match = False
                break
        if match:
            yield key, value

class FakeBackEnd(object):
    """Resgister data to it, you can then query it with the get method 
    as if it is the real gateway to a magento REST server. 
    """

    def __init__(self, size=10):
        self.size = size

    def _get_collection(self, data, params=dict()):
        page = params.get('page', 1)
        limit = params.get('limit', self.size)
        actual_page = 0
        result = dict()
        prev_result = result
        for key, item in apply_filters(data, params):
            result[key] = item
            if len(result) == limit:
                actual_page += 1
                if actual_page == page:
                    break
                else:
                    prev_result = result
                    result = dict()
        if not result:
            result = prev_result
        return result

    def _to_list(self, data):
        return [value for (item, value) in data.items()]

    def set_dictdata(self, key, data):
        """Set the data that will be queried through the get method.
        key specifies the first segment of the url to use to query this data.
        For example backend.set_dictdata('foo', somedata) will be available using
        backend.get('/foo'). Also using backend 
        data has to bey a dictionnary: {string_id1: obj1, string_id2: obj2}

        Using set_dictdata(key, dictdata) ensure that a call to get(/key) will return a
        dictionnary: {string_id1: obj1, string_id2: obj2}
        """
        self.data = {key: ('dict', data)}

    def set_listdata(self, key, data):
        """Set the data that will be queried through the get method.
        key specifies the first segment of the url to use to query this data.
        For example backend.set_dictdata('foo', somedata) will be available using
        backend.get('/foo'). Also using backend 
        data has to bey a dictionnary: {string_id1: obj1, string_id2: obj2}

        Using set_listdata(key, dictdata) ensure that a call to get(/key) will return a
        list: [obj1, obj2]
        """
        self.data = {key: ('list', data)}

    def get(self, path, **kwargs):
        """Emulates the BackEnd's get method.
        path is a relative url like (/objects)
        Currently supports only 2 segments in the URL (/foo or /bar/1)

        Returns a always a dictionnary if path has two segments: /bar/1
        If the path has ones segment (/foo),
         returns a dictionnary or a list dependind what method were used to set the data 
         (set_dictdata('foo', data) or set_listdata('foo', data)).
        """
        path = path[1:]
        segments = path.split('/')
        objtype = segments[0]
        (datatype, data)  = self.data[objtype]
        if len(segments) == 1:
            result = self._get_collection(data, **kwargs)
            if datatype == 'list':
                return self._to_list(result)
            return result
        else:
            objid = segments[1]
            return data[objid]


def create_default_backend(backend=None):
    if backend is None:
        backend = FakeBackEnd()
    backend_registry = BackEndRegistry()
    backend_registry.set_default_backend(backend)
    return backend
