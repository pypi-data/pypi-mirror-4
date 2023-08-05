'''
Created on Jan 21, 2012

@author: brian
'''
class RequiredException(Exception):
    def __init__(self,msg):
        self.error_msg = msg
        
    def __str__(self):
        return self.error_msg
    
class ValidationException(Exception):
    def __init__(self,msg):
        self.error_msg = msg
        
    def __str__(self):
        return self.error_msg
    
class RequestError(Exception):
    def __init__(self,msg):
        self.error_msg = msg
        
    def __str__(self):
        return self.error_msg