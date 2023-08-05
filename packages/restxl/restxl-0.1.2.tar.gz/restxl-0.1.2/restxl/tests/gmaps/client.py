'''
Created on Jan 25, 2012

@author: brian
'''
import restxl
from requests import DistanceMatrixRequest,DirectionsRequest

class GoogleMapsClient(restxl.RestXLer):
    distance_matrix = DistanceMatrixRequest
    directions = DirectionsRequest