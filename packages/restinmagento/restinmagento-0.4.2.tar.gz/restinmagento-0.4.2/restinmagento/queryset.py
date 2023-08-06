"""QuerySet class.
"""
from restinmagento.operators import in_

def serialize_criterion(criterions):
    """Transform an cirterin dict in a magento GET params:
    >>>serialize_criterion({'name': 'tata'})
    {'filter[0][attribute]': 'name', 'filter[0][in]': 'tata'}
    """
    result = dict()
    for (index, (attr, attr_value)) in enumerate(criterions.items()):
        key1 = 'filter[%s][attribute]' % index
        result[key1] = attr
        key2 = 'filter[%s][in]' % index
        result[key2] = attr_value
    return result


class QuerySet(object):

    def __init__(self, cm):
        self.cm = cm
        self._criterions = list()
        self._raw_criterions = dict()

    def _clone(self):
        res = self.__class__(self.cm)
        res._criterions.extend(self._criterions)
        return res

    def _apply_filter(self, *args, **criterion):
        for attr, value in criterion.items():
            self._criterions.append(in_(attr, value))
        for crit in args:
            self._criterions.append(crit)
        
    def _apply_raw_filter(self, raw_crit):
        self._raw_criterions.update(raw_crit)

    def _serialize_criterion(self):
        result = dict()
        for index, criterion in enumerate(self._criterions):
            result.update(criterion.serialize(index))
        return result

    def filter(self, *args, **criterion):
        """Filter the queryset with the given argument or criterion

        :param criterion: the filtering criterion
        :type criterion: a .. class::Operator
        """
        queryset = self._clone()
        queryset._apply_filter(*args, **criterion)
        return queryset

    def raw_filter(self, raw_crit):
        """Lets you specify raw filtering criterion as you would directionif you were directly
        interacting with a Magento server.
        See http://www.magentocommerce.com/api/rest/get_filters.html.

        :param raw_crit: the filtering criterion
        :type raw_crit: a dictionnary
        """
        queryset = self._clone()
        queryset._apply_raw_filter(raw_crit)
        return queryset

    def iterator(self):
        """Provides an iterator over the result objects.
        """
        criterions = self._serialize_criterion()
        criterions.update(self._raw_criterions)
        for obj in self.cm.all(criterions=criterions):
            yield obj

    def order_by(self, attr, direction='asc'):
        """Orders the result by attr.

        :param direction: direction of the sort. Can be 'asc' or 'dsc'.
        """
        return self.raw_filter(dict(order=attr, dir=direction))

    def __len__(self): 
        return len([item for item in self.iterator()])  

    def __iter__(self):
        return self.iterator()

    def __getitem__(self, key):
         return [obj for obj in self.iterator()][key]
        
