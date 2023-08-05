'''
Created on Jul 28, 2012

@author: brian
'''

from restxl import request

__all__ = [
    'LoginReq']

class LoginReq(request.Request):
    '''
    Log into to your CloudFiles account
    '''
    auth_user = request.CharHeader(required=True,verbose_name='X-Auth-User')
    auth_key = request.CharHeader(required=True,verbose_name='X-Auth-Key')
    
    class Meta(request.Request.Meta):
        response_type = 'raw'
        request_url = 'https://auth.api.rackspacecloud.com'
        request_path = '/v1.0'