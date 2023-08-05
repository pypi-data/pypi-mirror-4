from restxl.client import RestXLer
from auth_requests import *
from storage_requests import *
from cdn_requests import *

class CloudFiles(RestXLer):
    
    def __init__(self, auth_user,auth_key,*args,**kwargs):
        
        super(CloudFiles,self).__init__(*args,**kwargs)
        
        self.login(auth_user,auth_key)
            
#    START AUTHENTICATION NAMESPACE        
    def login(self,auth_user,auth_key):
        """
        Login
        """
        cs = LoginReq(
            auth_user=auth_user,
            auth_key=auth_key)
        
        self.server_management_url = cs.response.headers.get('x-server-management-url')
        self.auth_token = cs.response.headers.get('x-auth-token')
        self.storage_token = cs.response.headers.get('x-storage-token')
        self.cdn_management_url = cs.response.headers.get('x-cdn-management-url')
        
        self.storage_url = cs.response.headers.get('x-storage-url')
        
        self.kwargs.update(
            {'storage_credentials':{'auth_token':cs.response.headers.get('x-auth-token'),
                'auth_user':auth_user,
                'request_url':cs.response.headers.get('x-storage-url')}})
        
        return cs
    #Storage Service Requests
    list_containers = ListContainers
    account_info = AccountInfo
    container_info = ContainerInfo
    list_container_objects = ListContainerObjects
    create_container = CreateContainer
    delete_container = DeleteContainer
    delete_object = DeleteObject
    object_metadata_headers = ObjectMetaHeaders
    object_info = ObjectInfo
    create_meta_data = CreateMetadata
    #CDN Service Requests
    get_cdn_containers = GetCDNContainers
    get_cdn_container_info = GetCDNContainerInfo
    initialize_cdn_container = IntializeCDNContainer
    edit_cdn_container_info = EditCDNContainerInfo