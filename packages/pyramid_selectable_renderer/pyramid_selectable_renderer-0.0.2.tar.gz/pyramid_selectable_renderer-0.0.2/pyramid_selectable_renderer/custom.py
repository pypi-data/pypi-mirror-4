from pyramid.renderers import RendererHelper
from functools import wraps
from zope.interface import implementer
from zope.interface import provider
from .interfaces import IReceiveArguments
from .interfaces import ISelectRenderer

## util
class SkinnyRendererHelper(RendererHelper):
    #@override
    def render(self, value, system_values, request=None):
        renderer = self.renderer
        return renderer(value, system_values)

class RendererCache(object):
    def __init__(self, info):
        self.info = info
        self.renderers = {}

    def __call__(self, path):
        renderer = self.renderers.get(path)
        if renderer:
            return renderer
        renderer = SkinnyRendererHelper(name=path,
                                        package=self.info.package,
                                        registry=self.info.registry)
        self.renderers[path] = renderer
        return renderer


@implementer(IReceiveArguments)
class RecieveTemplatePathFormat(object):
    def __init__(self, fmt):
        self.fmt = fmt

    def __call__(self, fmt_args):
        return self.fmt % fmt_args

@implementer(IReceiveArguments)
class RecieveTemplatePathCandidatesDict(object):
    def __init__(self, candidates):
        self.candidates = candidates

    def __call__(self, lookupkey):
        return self.candidates[lookupkey]

class SelectByRetvalLeftGen(object):
    def __init__(self, convert, info):
        self.convert = convert
        self.cache = RendererCache(info)

    def __call__(self, create_template_path, 
                       value,system_values,request=None):
        fmt_arg, value = value
        template_path = create_template_path(self.convert(fmt_arg))
        renderer = self.cache(template_path)
        return renderer.render(value, system_values, request=request)

    @classmethod
    def generate(cls, convert):
        @provider(ISelectRenderer)
        @wraps(convert)
        def with_info(info):
            return cls(convert, info)
        return with_info

class SelectByRequestGen(object):
    def __init__(self, convert, info):
        self.convert = convert
        self.cache = RendererCache(info)

    def __call__(self, create_template_path, 
                       value,system_values,request=None):
        template_path = create_template_path(self.convert(request))
        renderer = self.cache(template_path)
        return renderer.render(value, system_values, request=request)

    @classmethod
    def generate(cls, convert):
        @provider(ISelectRenderer)
        @wraps(convert)
        def with_info(info):
            return cls(convert, info)
        return with_info
