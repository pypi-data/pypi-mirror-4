"""    
Default Header objects
"""
from validators import *
from base import CharVariableMixin,IntegerVariableMixin,BaseVariable
__all__ = [
    "CharVariable",
    "IntegerVariable",
    "URLVariable"
    ]

class URLVariable(BaseVariable):
    """
    Base RestXL URL Variable. All field types are subclassed from this class.
    """
    
class CharVariable(CharVariableMixin,URLVariable):
    def __init__(
        self,
        default_value=None,
        required=True,
        validators=[],
        verbose_name=None,
        max_length=None,
        min_length=None,
        *args,
        **kwargs
        ):
        self.max_length = max_length
        self.min_length = min_length
        self.required = required
        
        super(CharVariable, self).__init__(default_value=default_value,
        required=required,
        validators=validators,
        verbose_name=verbose_name,*args, **kwargs)
        
class IntegerVariable(IntegerVariableMixin,URLVariable):
    def __init__(
        self,default_value=None,
        required=False,
        validators=[],verbose_name=None,max_value=None,min_value=None,
        *args, **kwargs
        ):
        self.max_value = max_value
        self.min_value = min_value
        super(IntegerVariable, self).__init__(default_value=default_value,
        required=required,
        validators=validators,
        verbose_name=verbose_name,*args, **kwargs)