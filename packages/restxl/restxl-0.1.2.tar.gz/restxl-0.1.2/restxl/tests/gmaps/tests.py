'''
Created on Jan 25, 2012

@author: brian
'''
import unittest
from client import GoogleMapsClient

class GoogleMapsClientTestCase(unittest.TestCase):
    """Google Maps Client Test Case"""

    def setUp(self):
        self.client = GoogleMapsClient()
        
    def test_directions_attr(self):
        tt = self.client.directions(origin='Miami,FL',
            destination='New York,NY',sensor='false')
        
        self.assertDictContainsSubset({'status':'OK'}, tt.content)
        self.assertDictContainsSubset(
            {u'end_address': u'New York, NY, USA',
             u'start_address': u'Miami, FL, USA'},
            tt.content['routes'][0]['legs'][0])
    
    def test_directions_str(self):
        tt = self.client('directions',origin='Miami,FL',
            destination='New York,NY',sensor='false')
        
        self.assertDictContainsSubset({'status':'OK'}, tt.content)
        self.assertDictContainsSubset(
            {u'end_address': u'New York, NY, USA',
             u'start_address': u'Miami, FL, USA'},
            tt.content['routes'][0]['legs'][0])

if __name__ == "__main__":
    
    unittest.main()