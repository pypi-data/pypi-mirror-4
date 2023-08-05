import tg
import inspect
from utils import object_primary_key

class CacheKey(object):
    """
    Cache Key object, useful to use the entitycached
    decorator when we don't have any real object to pass
    to the cached function
    """
    def __init__(self, cache_key):
        self.cache_key = cache_key

class entitycached(object):
    def __init__(self, key_argument, expire=3600*24*3, cache_type='memory', namespace=None, sqla_merge=False):
        self.cache_key_argument = key_argument
        self.cache_expire = expire
        self.cache_type = cache_type
        self.cache_namespace = namespace
        self.sqla_merge = sqla_merge

    def _get_argspec(self, func):
        try:
            im_func = func.im_func
        except AttributeError:
            im_func = func

        spec = inspect.getargspec(im_func)
        argvals = spec[3]
        if argvals is None:
            argvals = []
        return spec[0], spec[1], spec[2], argvals

    def _get_params_with_argspec(self, args, kw):
        argvars, var_args, argkws, argvals = self.argspec
        if argvars and args:
            kw = kw.copy()
            args_len = len(args)
            for i, var in enumerate(argvars):
                if i >= args_len:
                    break
                kw[var] = args[i]
        return kw

    def _object_primary_key(self, model):
        return object_primary_key(model)

    def _determine_namespace(self, func):
        if self.cache_namespace is not None:
            return self.cache_namespace

        try:
            im_func = func.im_func.__name__
            im_class = (func.im_self if func.im_class == type else func.im_class).__name__
            im_module = self.func_module
        except AttributeError:
            im_func = func.__name__
            im_class = ''
            im_module = self.func_module
        return '%s-%s-%s' % (im_module, im_class, im_func)

    def _determine_cachekey(self, args, kw):
        named_params = self._get_params_with_argspec(args, kw)
        cache_pivot = named_params.get(self.cache_key_argument)

        cache_key = getattr(cache_pivot, 'cache_key', None)
        if not cache_key:
            try:
                object_id = getattr(cache_pivot, self._object_primary_key(cache_pivot))
            except:
                raise ValueError('Unable to determine object primary key, please declare a cache_key property in the object')

            try:
                updated_at = getattr(cache_pivot, 'updated_at').strftime('%Y%m%d%H%M%S')
            except:
                raise ValueError('Object missing an updated_at field, please add one ore declare a cache_key property')

            try:
                cache_key = '%s-%s' % (object_id, updated_at)
            except:
                raise ValueError('Unable to determine object cache key')

        return cache_key

    def _merge_sqla_result(self, results):
        DBSession = tg.config['DBSession']
        return [DBSession.merge(o, load=False) for o in results]

    def __call__(self, func):
        #Precalculate argspec
        if not hasattr(func, 'func_name'):
            raise TypeError('decorated object seems not to be a function or method, \
if you are using multiple decorators check that @entitycached is the first.')

        self.argspec = self._get_argspec(func)
        self.func_module = func.__module__

        def wrapped_function(*args, **kw):
            cache_namespace = self._determine_namespace(func)
            cache_key = self._determine_cachekey(args, kw)

            def call_function():
                return func(*args, **kw)

            cache = tg.cache.get_cache(cache_namespace, type=self.cache_type)
            result = cache.get_value(cache_key, createfunc=call_function, expiretime=self.cache_expire)
            if self.sqla_merge:
                result = self._merge_sqla_result(result)
            return result

        #Look like the decorated function
        wrapped_function.__doc__ = func.__doc__
        wrapped_function.__name__ = func.__name__
        wrapped_function.__entitycached__ = self
        return wrapped_function