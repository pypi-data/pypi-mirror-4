import os
import logging

if __name__ == '__main__':

    #this has to come first before you import any other modules otherwsise the settings won't be intitialized
    os.environ.setdefault("RMAS_ADAPTER_SETTINGS", "dev.settings")
    
    logging.basicConfig(level=logging.INFO)
    
    from core.poller import start_polling
    start_polling()
