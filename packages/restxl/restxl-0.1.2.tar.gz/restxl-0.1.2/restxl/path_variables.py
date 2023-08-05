"""    
Default Header objects
"""
from validators import *

from base import CharVariableMixin,IntegerVariableMixin,BaseVariable
__all__ = [
    "CharPathVariable",
    "IntegerPathVariable",
    "PathVariable"
    ]

class PathVariable(BaseVariable):
    """
    Base Path Variable. All PathVariable types are subclassed from this class.
    """
    
    def __init__(
        self,
        position,
        default_value=None,
        required=True,
        validators=[],
        verbose_name=None,*args,**kwargs
        ):
        self.position = position
        super(PathVariable,self).__init__(default_value=default_value,
        required=required,
        validators=validators,
        verbose_name=verbose_name,*args, **kwargs)
        
class CharPathVariable(CharVariableMixin,PathVariable):
    
    def __init__(
        self,
        position,
        default_value=None,
        required=True,
        validators=[],
        verbose_name=None,
        max_length=None,
        min_length=None,
        *args, **kwargs
        ):
        self.max_length = max_length
        self.min_length = min_length
        self.required = required
        self.default_value = default_value
        super(CharPathVariable, self).__init__(position,default_value=default_value,
        required=required,
        validators=validators,
        verbose_name=verbose_name,*args, **kwargs)
        
class IntegerPathVariable(IntegerVariableMixin,PathVariable):
    
    def __init__(
        self,position,
        default_value=None,
        required=True,
        validators=[],
        verbose_name=None,
        max_value=None,min_value=None,
        *args, **kwargs
        ):
        self.max_value = max_value
        self.min_value = min_value
        self.default_value = default_value
        super(IntegerPathVariable, self).__init__(default_value=default_value,
        required=required,
        validators=validators,
        verbose_name=verbose_name,*args, **kwargs)
        