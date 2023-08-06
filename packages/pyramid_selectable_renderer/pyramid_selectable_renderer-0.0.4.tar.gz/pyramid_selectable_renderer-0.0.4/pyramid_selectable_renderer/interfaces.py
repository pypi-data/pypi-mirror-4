from zope.interface import Interface

class IReceiveArguments(Interface):
    def __init__(*args, **kwargs):
        pass

    def __call__(*args, **kwargs):
        pass

class ISelectRenderer(Interface):
    def __init__(setup):
        pass

    def __call__(env, value, system_values, request=None):
        pass

