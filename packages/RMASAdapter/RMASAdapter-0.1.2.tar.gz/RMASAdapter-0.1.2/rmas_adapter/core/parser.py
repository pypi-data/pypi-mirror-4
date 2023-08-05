'''
This module handles the parsing of RMAS messages. 
'''

from lxml import etree

def _process_single_element_xpath(root, xpath_expression, namespaces={'p':'urn:xmlns:org:eurocris:cerif-1.4-0'}):
    '''
        This function should be used to process an xpath that you believe will only
        return one element (or you only want the first element of those returned)
    '''
    
    expression_result = root.xpath(xpath_expression, namespaces=namespaces)
    
    result = None
    if len(expression_result) > 0:
        result = expression_result.pop() 
    
    return result
    
def parse_event(event):
    '''
        Parses the event and returns a tuple, the first element being the
        event type, and the second element being the cerif payload of the message
    '''
    
    parser = etree.XMLParser(remove_comments=True)
    event_root = etree.fromstring(str(event), parser=parser)
    
    event_type = event_root.xpath('/rmas/message-type').pop().text
    payload = _process_single_element_xpath(event_root, '/rmas/p:CERIF')
    
    return (event_type, payload)

