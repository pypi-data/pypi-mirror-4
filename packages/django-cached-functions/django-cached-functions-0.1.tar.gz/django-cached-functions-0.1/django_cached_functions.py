import hashlib
from functools import wraps

try:
    import json
except ImportError:
    import simplejson as json

from django.core.cache import cache
from django.db.models import Model

def key_for_model(model):
    key = "{module}.{klass}/{id}".format(module=model.__module__, klass=model.__class__.__name__, id=model.id)
    if hasattr(model, 'date_modified'):
        key += "/" + model.date_modified.replace(microsecond=0).isoformat()
    else:
        key += "/nodate"
    return key

def key_for_kwargs(kwargs):
    new_dict = []
    for key in sorted(kwargs.keys()):
        value = kwargs[key]
        if isinstance(value, Model):
            new_dict.append((key, key_for_model(value)))
        elif any(isinstance(value, safetype) for safetype in [str, unicode, bool, int]):
            new_dict.append((key, repr(value)))
        else:
            raise TypeError("Unsupported type")

    return json.dumps(new_dict)

def cached_function(func):
    @wraps(func)
    def new_func(self, *args, **kwargs):
        dont_cache = kwargs.pop("dont_cache", False)

        if dont_cache:
            # short circuit, return direct function
            return func(self, *args, **kwargs)

        # Generate the cache key

        property_name = func.__name__
        key = key_for_model(self) + "/" + property_name
        if len(args) > 0:
            key += "/args(" + ",".join(key_for_model(a) for a in args) + ")"
        if len(kwargs) > 0:
            key += "/kwargs(" + key_for_kwargs(kwargs) + ")"
        #print "Cache key ", key

        key = hashlib.md5(key).hexdigest()

        # See if the value is in the cache

        cached_value = cache.get(key)

        if cached_value is None:
            # Not in the cache, so have to calculate and then return
            #print "  not in cache, calling function"
            returned_value = func(self, *args, **kwargs)
            cache.set(key, returned_value)
            return returned_value
        else:
            #print "  in cache, returning cached value"
            # return cached value
            return cached_value

    return new_func
