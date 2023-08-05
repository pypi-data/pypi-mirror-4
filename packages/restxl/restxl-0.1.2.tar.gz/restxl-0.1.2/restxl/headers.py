"""    
Default Header objects
"""

from base import CharVariableMixin,IntegerVariableMixin,BaseVariable
__all__ = [
    "CharHeader",
    "IntegerHeader",
    "Header"
    ]

class Header(BaseVariable):
    """
    Base RestXL Header. All Header types are subclassed from this class.
    """
    
class CharHeader(CharVariableMixin,Header):
    def __init__(
        self,
        default_value=None,
        required=True,
        validators=[],
        verbose_name=None,max_length=None,min_length=None,
        *args, **kwargs
        ):
        self.max_length = max_length
        self.min_length = min_length
        super(CharHeader, self).__init__(default_value=default_value,
        required=required,
        validators=validators,
        verbose_name=verbose_name,*args, **kwargs)
        
        
class IntegerHeader(IntegerVariableMixin,Header):
    def __init__(
        self,default_value=None,
        required=True,
        validators=[],
        verbose_name=None,max_value=None,min_value=None,
        *args, **kwargs
        ):
        self.max_value = max_value
        self.min_value = min_value
        super(CharHeader, self).__init__(default_value=default_value,
        required=required,
        validators=validators,
        verbose_name=verbose_name,*args, **kwargs)
        