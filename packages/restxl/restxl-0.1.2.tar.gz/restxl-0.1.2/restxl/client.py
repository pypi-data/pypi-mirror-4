'''
Created on Jun 25, 2010

@author: brianjinwright
'''
from request import Request
from inspect import isclass
__all__ = [
    'RestXLer',
    'BaseRestXLer'
    ]
class RestXLerError(Exception):
    def __init__(self,msg):
        self.error_msg = msg
        
    def __str__(self):
        return self.error_msg
    
def get_declared_variables(bases, attrs):
    requests = {}
    r_update = requests.update
    for variable_name, obj in attrs.items():
        if isclass(obj) and issubclass(obj, Request):
            r_update({variable_name:obj})

    for base in bases:
        if hasattr(base, 'base_requests'):
            if len(base.base_requests) > 0:
                r_update(base.base_requests)

    return requests

class RequestsDeclarativeVariablesMetaclass(type):
    """
    Partially ripped off from Django's forms.
    http://code.djangoproject.com/browser/django/trunk/django/forms/forms.py
    """
    def __new__(cls, name, bases, attrs):
        attrs.update(dict(base_requests = get_declared_variables(bases, attrs)))
        new_class = super(RequestsDeclarativeVariablesMetaclass,
            cls).__new__(cls, name, bases, attrs)
        
        return new_class


class BaseRestXLer(object):
    """
    Base class for all RestXLer client classes.
    """       
    def __init__(self,*args,**kwargs):
        self.args = args
        self.kwargs = kwargs
        
    def __call__(self,method_name,**kwargs):
        cs = self.base_requests.get(method_name,None)
        try:
            if cs.Meta.constant:
                if isinstance(cs.Meta.constant, tuple):
                    for i in cs.Meta.constant:
                        kwargs.update(self.kwargs.get(i))
                else:
                    kwargs.update(self.kwargs.get(cs.Meta.constant))
                    
        except AttributeError:
            pass
        if cs:
            req_cls = cs(**kwargs)
        else:
            raise RestXLerError('This method does not exists')
        return req_cls
        
class RestXLer(BaseRestXLer):
    __metaclass__ = RequestsDeclarativeVariablesMetaclass
