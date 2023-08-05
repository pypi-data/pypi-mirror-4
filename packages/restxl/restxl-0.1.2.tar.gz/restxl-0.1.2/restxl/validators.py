from exceptions import ValidationException
__all__ = [
    "Validator",
    "RequiredValidator",
    "StringValidator",
    "IntegerValidator",
    "MaxValueValidator",
    "MinValueValidator",
    "MinLengthValidator",
    "MaxLengthValidator",
    ]

class Validator(object):
        
    def validate(self,value):
        raise NotImplementedError
    
class RequiredValidator(Validator):
    
    def validate(self,value):
        if not value:
            raise ValidationException(
                'This value is required'
                )

class StringValidator(Validator):
    def validate(self,value):
        
        if value and not isinstance(value, str):
            raise ValidationException(
                'This value should '
                'be a string'
                )

class IntegerValidator(Validator):
    def validate(self,value):
        if value and not isinstance(value, int):
            raise ValidationException(
                'This value should '
                'be a integer'
                )
            
class MaxValueValidator(Validator):
    def __init__(self,compare_value):
        self.compare_value = compare_value
        
    def validate(self,value):
        if not isinstance(value, int) and self.value > self.compare_value:
            raise ValidationException(
                'This value should '
                'have a value lesser than '
                '%s. Currently %s' % (self.compare_value, self.value)
                )

class MinValueValidator(MaxValueValidator):
        
    def validate(self,value):
        if not isinstance(value, int) and self.value < self.compare_value:
            raise ValidationException(
                'This value should '
                'have a value greater than '
                '%s. Currently %s' % (self.compare_value, self.value)
                )

class MaxLengthValidator(Validator):
    
    def __init__(self,length):
        self.length = length
        
    def validate(self,value):
        if not isinstance(value, int) and len(self.value) > self.length:
            raise ValidationException(
                'This value should '
                'have a length lesser than '
                '%s. Currently %s' % (self.length, self.value)
                )

class MinLengthValidator(MaxLengthValidator):
        
    def validate(self,value):
        if not isinstance(value, int) and self.value < self.length:
            raise ValidationException(
                'This value should '
                'have a length greater than '
                '%s. Currently %s' % (self.length, self.value)
                )