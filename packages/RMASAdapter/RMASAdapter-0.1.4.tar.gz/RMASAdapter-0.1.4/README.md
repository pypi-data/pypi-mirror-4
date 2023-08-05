rmas_adapter
============

A basic framework for building RMAS adapters

This package will create for you a skeleton rmas adapter, it will know how to connect to
and poll an rmas bus for events, and when an event is detected, it can be configured to
send the payload of those events to the event handlers that you specify.

Installation
============

Either clone from github: [git://github.com/UoK-Psychology/rmas_adapter.git](git://github.com/UoK-Psychology/rmas_adapter.git) then do 

`python setup.py install`

or:

`pip install RMASAdapter`

Configuring
===========

To create your adapter skeleton, you will need to run the `rmas_adapter_admin.py` script
as follows:

```
python rmas_adapter_admin.py create --name <adapter name> 
									--target <directory to generate code into>(optional)
```


When this command has run, it will have created the adapter skeleton in a directory with the
same name as the `--name` argument. This adapter skeleton contains:

* runner.py - Use this to start your adapter running
* settings.py - Basic settings for the adapter, and configuration point for adding your functionality

The settings file must contain valid settings for:

RMAS\_BUS\_WSDL : the url to the RMAS ESB  
POLL\_INTERVAL : the number of milliseconds to wait between polling

If you want your adapter to do anything then you will need to also specify:

EVENTS: this configures the events that you want your adapter to respond to and  looks like:
`[('<RMAS_EVENT_NAME>,'path.to.handler.module'),]`

Your handler module must specify a function that has the following signature, when the configured event is received the poller will send the payload to this function for you to handle as you wish:

```
def handle_event(payload):
	'''
		Do something cool!
	'''
```