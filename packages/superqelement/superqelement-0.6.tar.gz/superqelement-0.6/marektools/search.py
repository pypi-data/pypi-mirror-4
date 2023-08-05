from django.db.models import Q
import re

class SuperOperator(object):
    def __init__(self, key):
        self.key = key

class OperatorList(SuperOperator):
    def __call__(self, data):
        return data.getlist(self.key)

class OperatorSimple(SuperOperator):
    def __call__(self, data):
        return data[self.key]

class SQFilter(object):
    def __init__(self, data_key, orm_filter, operator=OperatorSimple):
        self.orm_filter = orm_filter
        self.data_key = data_key
        self.operator = operator(data_key)
        
    def get_value(self, data):
        return self.operator(data)

class SuperQElement(object):
    def __init__(self, request, filters, **kwargs):
        self.data = request.GET if request.GET else request.POST
        self.filters = filters
        self.main_Q = kwargs.pop('q', Q())
        self._create_q()

    def _create_q(self):
        for su_filter in self.filters:
            if self.data.has_key(su_filter.data_key):
                self.main_Q.add(Q(**dict(
                        map(lambda x: (x[0], x[1]), [(su_filter.orm_filter, su_filter.get_value(self.data))])
                        )), Q.AND
                )
    
    def __call__(self):
        return self.main_Q
