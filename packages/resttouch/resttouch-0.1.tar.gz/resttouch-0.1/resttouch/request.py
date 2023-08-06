import urllib2
import urllib

__all__ = ()

class Request(object):
    def __init__(self, url, data):
        self.url = url
        self.data = data
        
    def get(self):
        request = urllib2.Request(
                url=self.url + '?' + urllib.urlencode(self.data)
        )
        response = urllib2.urlopen(request)
        return response.read()
    
    def post(self):
        request = urllib2.Request(
                url=self.url, data=self.data
        )
        response = urllib2.urlopen(request)
        return response.read()
    
    def put(self):
        pass
    
    def delete(self):
        pass