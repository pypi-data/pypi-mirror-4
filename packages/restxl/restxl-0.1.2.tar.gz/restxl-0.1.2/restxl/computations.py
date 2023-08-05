'''
Created on Jan 27, 2012

@author: brian
'''
from url_variables import URLVariable

__all__ = (
    'BaseComputation',
    )
class BaseComputation(object):
    variable_class = URLVariable
    verbose_name = None
    
    def run(self,**kwargs):
        raise NotImplementedError