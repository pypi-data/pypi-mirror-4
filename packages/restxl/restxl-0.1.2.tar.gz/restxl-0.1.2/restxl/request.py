from urllib import urlencode
from operator import attrgetter


import requests
import json
import simplexmlapi
from BeautifulSoup import BeautifulSoup

from url_variables import *
from headers import *
from path_variables import *
from exceptions import RequestError

__all__ = [
    'Request',
    'BaseRequest',
    'DeclarativeVariablesMetaclass',
    'RestXLResponse'    
    ]

class RestXLResponse(object):
    def __init__(self,response,content):
        self.response = response
        self.content = content

    
def get_declared_variables(bases, attrs):
    variables = {}
    v_update = variables.update
    headers = {}
    h_update = headers.update
    path_variables = {}
    p_update = path_variables.update
    attrs_pop = attrs.pop
    for variable_name, obj in attrs.items():
        if isinstance(obj, URLVariable):
            v_update({variable_name:attrs_pop(variable_name)})
        if isinstance(obj, Header):
            h_update({variable_name:attrs_pop(variable_name)})
        if isinstance(obj, PathVariable):
            p_update({variable_name:attrs_pop(variable_name)})
        
    for base in bases:
        if hasattr(base, 'base_variables'):
            if len(base.base_variables) > 0:
                v_update(base.base_variables)
        if hasattr(base, 'base_headers'):
            if len(base.base_headers) > 0:
                h_update(base.base_headers)
        if hasattr(base, 'base_path_variables'):
            if len(base.base_path_variables) > 0:
                p_update(base.base_path_variables)

    return variables,headers,path_variables

class DeclarativeVariablesMetaclass(type):
    """
    Partially ripped off from Django's forms.
    http://code.djangoproject.com/browser/django/trunk/django/forms/forms.py
    """
    def __new__(cls, name, bases, attrs):
        attrs['base_variables'],attrs['base_headers']\
        ,attrs['base_path_variables'] \
        = get_declared_variables(bases, attrs)
        new_class = super(DeclarativeVariablesMetaclass,
            cls).__new__(cls, name, bases, attrs)

        return new_class


class BaseRequest(object):
    """
    Base class for all RestXL request classes.
    """       
    computations = list()
    
    def __init__(self,*args,**kwargs):
        self.args = args
        self.kwargs = kwargs
        
    def __new__(cls, *args, **kwargs):
        request = cls.new(*args, **kwargs)
        return request.get_response()
        
    @classmethod
    def new(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj.__init__(*args, **kwargs)
        return obj
    
    def get_response(self):
        self._variables = dict()
        self._headers = dict()
        self._path_variables = dict()
        self.load_base_variables('headers')
        self.load_base_variables('variables')
        self.run_computations()
        request_url = self.kwargs.get('request_url',None) \
            or getattr(self.Meta, 'request_url',None)
        request_path = getattr(self.Meta, 'request_path',None)
        if not request_path:
            request_path = self.load_pathvars()
        else:
            pathvars = self.load_pathvars()
            
            if pathvars:
                request_path = request_path+self.load_pathvars()
        if not request_url:
            raise RequestError('There is no request_url specified. You must set one.')
        if request_path:
            return self.rest_request(request_url, request_path)
        return self.rest_request(request_url)
    
    def load_base_variables(self,type):
        for key,value in getattr(self,'base_{0}'.format(type)).items():
            var = self.kwargs.get(key,None)
            if not var and value.default_value:
                var = value.default_value
            value.validate(var)
            if var != None:
                var_dict_update = getattr(self, '_{0}'.format(type)).update
                if hasattr(value, 'verbose_name'):
                    var_dict_update({value.verbose_name:var})
                else:
                    var_dict_update({key:var})
        
    def load_pathvars(self):
        if len(self.base_path_variables) < 1:
            return None
        pathv_list = list()
        pl_append = pathv_list.append
        for key,value in self.base_path_variables.items():
            pathvar = self.kwargs.get(key,None)
            required = getattr(pathvar, 'required',False)
            if required:
                value.validate(pathvar)
            if pathvar != None:
                setattr(value, 'value', pathvar)
                pl_append(value)
                
            if not pathvar and value.default_value:
                setattr(value, 'value', value.default_value)
                
                pl_append(value)
                
        
            
        tt = sorted(pathv_list,key=attrgetter('position'))
        
        sorted_values = [i.value for i in tt]
        
        return '/'.join(sorted_values)
    
    def load_content(self,type,content):
        nd = content
        if type == 'xml':
            nd = simplexmlapi.loads(content)
        if type == 'json':
            nd = json.loads(content)
        if type == 'html':
            nd = BeautifulSoup(content)
        return nd
    
    def get_request(self,request_url,method,data,headers):
        resp = requests.request(method,request_url,data=data,headers=headers)
        return resp
    
    def run_computations(self):
        for i in self.computations:
            value = i.run(*self.args,**self.kwargs)
            if issubclass(i.variable_class,URLVariable):
                self._variables.update({i.verbose_name:value})
            if issubclass(i.variable_class,Header):
                self._headers.update({i.verbose_name:value})
            if issubclass(i.variable_class,PathVariable):
                self._headers.update({i.verbose_name:value})
    
    def rest_request(self,request_url,request_path=None):
        method = getattr(self.Meta, 'method','GET')
        
        response_type = getattr(self.Meta, 'response_type','xml')
        
        if not request_url:
            raise RequestError('request_url needs to be defined')
        
        if request_path:
            request_url = '{0}/{1}'.format(request_url,request_path)
            
        else:
            request_url = '{0}'.format(request_url)
        
        if len(self._variables) != 0:
            body = urlencode(self._variables)
            if method == 'GET': 
                request_url = '{0}?{1}'.format(request_url,body)
                body = None
        else:
            body = None
            
        headers = getattr(self, '_headers',{})
        
        resp = self.get_request(request_url, method, body, headers)
        nd = self.load_content(response_type,resp.text)
        response_class = getattr(self.Meta, 'response_class',RestXLResponse)
        return response_class(resp,nd)

    class Meta:
        """
        This class holds important information about how the request is made.
        """
        method = 'GET'
        response_type = 'xml'
        
class Request(BaseRequest):
    __metaclass__ = DeclarativeVariablesMetaclass 
    