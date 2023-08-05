'''
    This module handles the polling of the RMAS ESB
'''


from threading import Timer

import datetime
import logging
from rmas_adapter.core.rmas_bus import RMASBus
from rmas_adapter.conf import settings
from rmas_adapter.core.parser import parse_event

import importlib

last_poll = None
bus = None

def start_polling():
    '''
        This function starts the poller polling, it will poll immediately
        and then repeat the poll after the settings.POLL_INTERVAL. When a
        event is received from the bus, it will see if the event is in the 
        settings.EVENTS list and call the appropriate event handler
    '''
    global bus, last_poll
    last_poll = datetime.datetime.now()
    bus = RMASBus()
    poll_for_events()
    
def _get_handlers(event_type):
    '''
        Attempts to get any event handlers based on the settings.EVENTS list
        If none are found it will return an empty list.
        
        Returns:
            A list of event handling modules (which will have a function called handle that accepts the
            payload of the event) or an empty list if there are no handlers registered.
    '''
    
    handlers = []
    
    for event in settings.EVENTS:
        #each event will be a tuple, the first element is the event type, the second element is the path to the handler module
        if event[0] == event_type:
            #attempt to import the handler module
            handlers.append(importlib.import_module(event[1]))
    
    return handlers

def poll_for_events():
    logging.debug('Polling ESB')
    
    global last_poll
    events = bus.get_events(last_poll.isoformat())
    last_poll = datetime.datetime.now()
    
    if hasattr(events, 'string'):
        for event in events.string:
   
            #handle the events as described in the settings.EVENTS list
            event_type, payload = parse_event(event)
            logging.debug ('Got an event of type: %s' % event_type)
            
            for handler in _get_handlers(event_type):
                handler.handle_event(payload=payload)
            
    #update the last_poll time - we only want new events after this time.

    Timer(settings.POLL_INTERVAL/1000, poll_for_events).start()#poll again in 2 seconds time!

