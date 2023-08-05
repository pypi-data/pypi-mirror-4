import functools

class LookUpKey(str):
    def register_env(self,env):
        self.env = env

class SelectableRendererSetup(object):
    def __init__(self, for_arguments_fn, select_fn, renderer_name=None):
        self.for_arguments_fn = for_arguments_fn
        self.select_fn = select_fn
        self.renderer_name = renderer_name or self.__class__.__name__

    def register_to(self, config):
        factory = functools.partial(SelectableRendererFactory, self.select_fn)
        config.add_renderer(self.renderer_name, factory)

    def __call__(self, *args, **kwargs): #view_config
        env = self.for_arguments_fn(*args,**kwargs)
        lookup_key = LookUpKey(self.renderer_name)
        lookup_key.register_env(env)
        return lookup_key

class SelectableRendererFactory(object):
    def __init__(self, select_fn, info):
        self.select_fn = select_fn(info)
        ## xxx: this is hack.
        self.env = info.name.env

    def __call__(self, value, system_values, request=None):
        request = request or system_values["request"]
        return self.select_fn(self.env, value, system_values, request=request)
    
