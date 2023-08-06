import datetime, time

def gettimestamp(dt=None):
    """
    Gives you a timestamp for any given datetime 
    object. If called without a datetime argument
    it'll give you the timestamp of now.
    """
    if not dt:
        dt = datetime.datetime.now()
    return time.mktime(dt.timetuple())
