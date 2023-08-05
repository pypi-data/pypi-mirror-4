import os
import importlib

ENVIRONMENT_VARIABLE = 'RMAS_ADAPTER_SETTINGS'


class SettingsLoader(object):
    '''
        This class is used to import user settings into a standard loaction where
        all packages and modules know how to find them based on the setting module
        location being stored in an environment variable.
    '''
    
    def __init__(self, settings_module):
        '''
        Args:
            settings_module: A string representing the settings module location
            
        Thorws:
            ImportError: If it can't import the setting module.
        '''
        module = importlib.import_module(settings_module)
        
        for setting in dir(module):
            setattr(self, setting, getattr(module, setting))
        
        
#convenience attribute that knows how to initiate the settings class.
settings = SettingsLoader(os.environ[ENVIRONMENT_VARIABLE])