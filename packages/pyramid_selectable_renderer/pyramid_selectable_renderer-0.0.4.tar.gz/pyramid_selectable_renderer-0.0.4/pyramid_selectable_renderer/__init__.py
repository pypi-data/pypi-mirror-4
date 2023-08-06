from zope.interface import Interface, Attribute, implementer
from pyramid.interfaces import ITemplateRenderer
import functools

__all__ = [
    'LookUpKey',
    'SelectableRendererSetup',
    'SelectableRendererFactory',
    ]


# XXX: this should have been defined in pyramid_layout!
class ILayoutTemplateRendererImpl(Interface):
    filename = Attribute('''The filename of the template''')
    uri = Attribute('''The uri of the template''')

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

@implementer(ILayoutTemplateRendererImpl)
class SelectableRendererAdapter(object):
    def __init__(self, select_fn, create_template_path, request):
        self.select_fn = select_fn
        self.create_template_path = create_template_path
        self.request = request

    @property
    def filename(self):
        return self.uri

    @property
    def uri(self):
        return self.select_fn.get_template_path(self.create_template_path, self.request)

@implementer(ITemplateRenderer)
class SelectableRendererFactory(object):
    def __init__(self, select_fn, info):
        self.select_fn = select_fn(info)
        ## xxx: this is hack.
        self.env = info.name.env

    def implementation(self):
        from pyramid.threadlocal import get_current_request
        return SelectableRendererAdapter(self.select_fn, self.env, get_current_request())

    def __call__(self, value, system_values, request=None):
        request = request or system_values["request"]
        return self.select_fn(self.env, value, system_values, request=request)
    
