from basky.forms import BasketForm

def register(cls, config=None):
    # create a blank configuration
    if config is None:
        config = BasketConfig()
        for k,v in kwargs.items():
            setattr(config, k, v)
    # generate a key for the class
    key = '%s_%s' % (cls._meta.app_label, cls._meta.module_name)
    # update the config with any kwargs
    # now add it to the registry
    BasketRegistry._registry[key] = config




class BasketRegistry(object):
    _registry = {}
    
    @staticmethod
    def key(model):
        """returns a key for an instance or model class to query registry"""
        return '%s_%s' % (model._meta.app_label, model._meta.module_name)
    
    @staticmethod
    def get(instance):
        """returns the config"""
        key = BasketRegistry.key(instance)
        try:
            config = BasketRegistry._registry[key]
        except KeyError:
                config = BasketConfig
        return config
        

class BasketConfig(object):
    """Basic configuration"""
    name = 'name'
    total = 'total'
    form = BasketForm
