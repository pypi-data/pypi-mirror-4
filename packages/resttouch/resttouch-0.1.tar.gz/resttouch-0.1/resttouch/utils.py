class ClientRestException(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return self.value
    
def iteritems(d):
    return iter(getattr(d, 'iteritems')())