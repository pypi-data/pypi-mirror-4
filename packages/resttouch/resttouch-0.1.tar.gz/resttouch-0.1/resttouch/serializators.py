import json

__all__ = ('SimpleJSON')

class Serializator(object):
    pass

class PlainText(Serializator):
    def serialize(self, string):
        return string
        
class SimpleJSON(Serializator):
    def serialize(self, string):
        return json.loads(string)