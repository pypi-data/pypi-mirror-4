'''
Created on Jan 21, 2012

@author: brian
'''
from validators import *

class BaseVariable(object):
    
    def __init__(
        self,
        default_value=None,
        required=True,
        validators=[],
        verbose_name=None
        ):
        self.default_value = default_value
        self.required = required
        self.validators = list()
        self.get_validators()
        if verbose_name:
            self.verbose_name = verbose_name
            
    def validate(self,value):
        for i in self.validators:
            i.validate(value)

class VariableMixin(object):
    def get_validators(self):
        if self.required:
            self.validators.insert(0,RequiredValidator())
    
class CharVariableMixin(VariableMixin):
    
    def get_validators(self):
        
        VariableMixin.get_validators(self)
        self.validators.append(StringValidator())
        if self.max_length:
            self.validators.append(MaxLengthValidator(self.max_length))
        if self.min_length:
            self.validators.append(MinLengthValidator(self.min_length))
                
class IntegerVariableMixin(VariableMixin):
    
    def get_validators(self):
        VariableMixin.get_validators(self)
        self.validators.append(IntegerValidator())
        if self.max_value:
            self.validators.append(MaxValueValidator(self.max_value))
        if self.min_value:
            self.validators.append(MinValueValidator(self.min_value))