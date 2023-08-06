from params import Param, QueryParam, PathParam
from request import Request
from utils import RestTouchException, iteritems
from urlparse import urljoin

__all__ = ('Route')

class BaseRoute(object):
    service = None
    params = []

    def _validate_param(self, param):
        if not self.params.has_key(param[0]):
            raise RestTouchException("Unknow param: %s, choose are: %s"%(
                        param[0], ", ".join([p for p in self.params])))
        return True
        
    def _is_all_required(self, params):
        for name, param in self.params.iteritems():
            if not params.has_key(name) and param.required:
                raise RestTouchException("%s param is required."%name)
        return True
    
    def _add_default_params(self, params):
        for name, param in self.params.iteritems():
            if param.default and not params.has_key(name) and param.required:
                params[name] = param.default
        return params

    def _prepare_params(self, kwargs):
        request_params = {}
        for param in list(iteritems(kwargs)):
            self._validate_param(param)
            request_params[param[0]] = param[1]
        self._add_default_params(request_params)
        self._is_all_required(request_params)
        return request_params
    
    def _regroup_params(self, params):
        param_groups = {
            'query': (QueryParam, {}),
            'path': (PathParam, {})
        }
        for name, param in params.iteritems():
            for group_name, data in param_groups.iteritems():
                if isinstance(self.params[name], data[0]):
                    data[1][name] = param
        return dict((group_name, data[1]) for group_name, data in param_groups.iteritems())

    def _prepare_and_regroup(self, kwargs):
        return self._regroup_params(self._prepare_params(kwargs))


class Route(BaseRoute):    
    def __init__(self, method, url, *args, **kwargs):
        self.method = method
        self.url = url
        self.params = dict((param.value, param) for param in args if isinstance(param, Param))
            
    def __call__(self, *args, **kwargs):
        extra_query = kwargs.pop('extra_query', {})
        groups = self._prepare_and_regroup(kwargs)
        
        groups['query'].update(extra_query)
        
        request = Request(urljoin(self.service.end_point, self.url % groups['path']), groups['query'])
        response = request.__getattribute__(self.method.lower())()
        
        if self.service.serializator:
            return self.service.serializator.serialize(response)
        return response