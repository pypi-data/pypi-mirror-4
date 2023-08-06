import threading


__version__ = "0.0.2"


local = threading.local()


REQUEST_ID_HEADER_SETTING = 'LOG_REQUEST_ID_HEADER'
NO_REQUEST_ID = "none"  # Used if no request ID is available
NO_USER_ID = "none"  # User if no user ID is available
