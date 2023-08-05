import restxl

class GoogleMapsRequest(restxl.Request):
    sensor = restxl.CharVariable(required=True)
    avoid = restxl.CharVariable(required=False)
    units = restxl.CharVariable(required=False)
    mode = restxl.CharVariable(default_value='driving')
    
    class Meta(restxl.Request.Meta):
        response_type = 'json'
        
class DirectionsRequest(GoogleMapsRequest):
    origin = restxl.CharVariable()
    destination = restxl.CharVariable()
    waypoints = restxl.CharVariable(required=False)
    alternatives = restxl.CharVariable(required=False)
    region = restxl.CharVariable(required=False)
        
    class Meta(GoogleMapsRequest.Meta):
        request_url = 'https://maps.googleapis.com/maps/api/directions/json'
        
class DistanceMatrixRequest(restxl.Request):
    origins = restxl.CharVariable()
    destinations = restxl.CharVariable()
    language = restxl.CharVariable(required=False)
    
    class Meta(GoogleMapsRequest.Meta):
        request_url = 'http://maps.googleapis.com/maps/api/distancematrix/json'