'''
Created on Jul 28, 2012

@author: brian
'''
from restxl import request
from cloudfiles_requests import *

__all__ = [
    'GetCDNContainers',
    'GetCDNContainerInfo',
    'IntializeCDNContainer',
    'EditCDNContainerInfo'
    ]

class GetCDNContainers(DynamicAuthTokenReq):
    enabled_only = request.CharVariable(default_value='false',required=False)
    limit = request.CharVariable(required=False)
    marker = request.CharVariable(required=False)
    format = request.CharVariable(default_value='json',required=False)
    class Meta(DynamicAuthTokenReq.Meta):
        response_type = 'json'
        method = 'GET'
        

class GetCDNContainerInfo(DynamicAuthTokenReq):
    container = request.CharPathVariable(1,required=True)
    class Meta(DynamicAuthTokenReq.Meta):
        method = 'HEAD'
        response_type = 'raw'
        
class IntializeCDNContainer(GetCDNContainerInfo):
    ttl = request.CharHeader(verbose_name='X-TTL')
    log_retention = request.CharHeader(verbose_name='X-Log-Retention')
    class Meta(GetCDNContainerInfo.Meta):
        method = 'PUT'
        response_type = 'raw'
        
class EditCDNContainerInfo(IntializeCDNContainer):
    cdn_enabled = request.CharHeader(verbose_name='X-CDN-Enabled')
    class Meta(IntializeCDNContainer.Meta):
        method = 'POST'