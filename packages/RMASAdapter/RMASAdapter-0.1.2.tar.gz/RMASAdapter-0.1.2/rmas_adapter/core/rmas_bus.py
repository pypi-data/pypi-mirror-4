'''
This module encapsulates the functionality for interacting with RMAS bus

@author: jasonmarshall
'''

from suds.client import Client
from rmas_adapter.conf import settings
class RMASBus():
    
    def __init__(self):
        
        self.rmas_bus_wsdl = settings.RMAS_BUS_WSDL
        self.client = Client(self.rmas_bus_wsdl, cache=None)
        
    def get_events(self, timestamp):
        '''
            Returns all the events that have occured since the timestamp
        '''
        return self.client.service.getEvents(timestamp)
        
    def push_event(self, event):
        '''
            Pushes the event to the RMAS bus.
        '''
        return self.client.service.pushEvent(event)
