# Names: Sai Jyothi Attuluri, Sai Nikhil Gummadavelli

# util

# constants
SELECT_TIMEOUT = 1
BUFFER_LEN = 1024
BRIDGE_SL_TIMEOUT = 30 # in seconds
BRIDGE_SL_REFRESH_PERIOD = 10 # in seconds
STATION_PQ_REFRESH_PERIOD = 10 # in seconds
CLIENT_CONNECT_RETRIES = 5

def isIp(s: str):
    """
    check if given string is ip address or not
    """
    if s.__contains__('.'):
        if s.count('.') == 3:
            return True
    return False

def unpack(obj, d=None):
    """
    upack - deserialize object
    """
    if d is not None:
        for key, value in d.items():
            setattr(obj, key, value)
    return obj
