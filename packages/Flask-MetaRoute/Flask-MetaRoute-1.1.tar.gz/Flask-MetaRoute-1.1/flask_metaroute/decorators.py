import inspect

def enhance_ctrl_class(cls, path, args, kwargs):
    cls.METAROUTE_CONTROLLER_PATH   = path
    cls.METAROUTE_CONTROLLER_ARGS   = args
    cls.METAROUTE_CONTROLLER_KWARGS = kwargs
    return cls

def Controller(*args, **kwargs):
    if not inspect.isclass(args[0]):
        def d(cls):
            return enhance_ctrl_class(cls, args[0], args[1:], kwargs)
        return d
    else:
        return enhance_ctrl_class(args[0], "", [], {})

def Route(path = "", *args, **kwargs):
    def d(f):
        f.METAROUTE_ACTION_PATHS = getattr(f, "METAROUTE_ACTION_PATHS", []) + [(path, args, kwargs)]
        return f
    return d

def Error(ex = ""):
    def d(f):
        f.METAROUTE_ERROR_EXCEPTIONS = getattr(f, "METAROUTE_ERROR_EXCEPTIONS", []) + [ex]
        return f
    return d
