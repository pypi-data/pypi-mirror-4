'''
Created on Jul 28, 2012

@author: brian
'''
from restxl import request
__all__ = [
    'CloudFilesResponseError',
    'DynamicAuthTokenReq', 
    'StorageAccountServicesReq'  
    ]

class CloudFilesResponseError(Exception):
    def __init__(self,value,error_message):
        self.value = value
        self.error_message = error_message
    def __str__(self):
        return repr("Response Code: %s Error Message: %s" % \
                    (self.value, self.error_message))
    
class DynamicAuthTokenReq(request.Request):
    """
    CloudFiles Auth Token Request
    """
    auth_token = request.CharHeader(required=True,verbose_name='X-Auth-Token')    
    
    class Meta:
        constant = 'storage_credentials'
        request_url = 'https://auth.api.rackspacecloud.com'
        
    
class StorageAccountServicesReq(DynamicAuthTokenReq):
#    limit = request.CharVariable(required=False)
#    marker = request.CharVariable(required=False)
    format = request.CharVariable(default_value='json',required=False)
    
    class Meta(DynamicAuthTokenReq.Meta):
        response_type = 'json'
    
    