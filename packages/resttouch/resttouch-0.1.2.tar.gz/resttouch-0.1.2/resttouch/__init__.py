#coding: utf-8

__version__ = '0.1'
__author__ = 'Marek Waluś <marekwalus@gmail.com>'

from routes import Route
from utils import iteritems

__all__ = ('Service', 'serializator', 'end_point')

def serializator(serializator):
    def wrapper(klass):
        klass.serializator = serializator()
        return klass
    return wrapper

def end_point(end_point):
    def wrapper(klass):
        klass.end_point = end_point
        return klass
    return wrapper

def build_routes(bases, attrs):
    return [(route_name, obj) for route_name, obj in list(iteritems(attrs)) if isinstance(obj, Route)]

def add_service_to_routes(service):
    for r in service.routes:
        r[1].service = service
    
class DeclarativeRouteMetaclass(type):
    def __new__(cls, name, bases, attrs):
        attrs['routes'] = build_routes(bases, attrs)
        new_class = super(DeclarativeRouteMetaclass,
                     cls).__new__(cls, name, bases, attrs)
        add_service_to_routes(new_class)
        return new_class

class Service(object):
    __metaclass__ = DeclarativeRouteMetaclass
    
    endpoint = ''
    serializator = None