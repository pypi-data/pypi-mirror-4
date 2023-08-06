from params import Param, QueryParam, PathParam
from request import Request
from utils import ClientRestException, iteritems
from urlparse import urljoin

__all__ = ('Route')

PARAM_GROUPS = (
    ('query', QueryParam),
    ('path', PathParam),
)

class BaseRoute(object):
    service = None
    params = []

    def _validate_param(self, param):
        if not self.params.has_key(param[0]):
            raise ClientRestException("Unknow param: %s, choose are: %s"%(
                        param[0], ", ".join([p for p in self.params])))
        return True
        
    def _is_all_required(self, params):
        for name, param in self.params.iteritems():
            if not params.has_key(name) and param.required:
                raise ClientRestException("%s param is required."%param[0])
        return True
    
    def _add_default_params(self, params):
        for name, param in [(name, param) for name, param in self.params.iteritems() if param.default]:
            if not params.has_key(name) and param.required:
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
        param_group = {}
        for group_name, group in PARAM_GROUPS:
            param_group[group_name] = {}
        for param in params.items():
            for group_name, group in PARAM_GROUPS:
                if isinstance(self.params[param[0]], group):
                    param_group[group_name].update(dict([param]))
        return param_group
    
    def _prepare_and_regroup(self, kwargs):
        return self._regroup_params(self._prepare_params(kwargs))

class Route(BaseRoute):    
    def __init__(self, method, url, *args, **kwargs):
        self.method = method
        self.url = url
        self.params = dict([(param.value, param) for param in args if isinstance(param, Param)])
            
    def __call__(self, *args, **kwargs):
        groups = self._prepare_and_regroup(kwargs)
        
        request = Request(urljoin(self.service.end_point, self.url % groups['path']), groups['query'])
        response = request.__getattribute__(self.method.lower())()
        
        if self.service.serializator:
            return self.service.serializator.serialize(response)
        return response