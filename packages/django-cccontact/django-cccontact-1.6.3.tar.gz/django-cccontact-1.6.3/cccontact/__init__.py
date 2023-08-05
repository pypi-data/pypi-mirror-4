from django.utils.importlib import import_module

version = (1, '6', '3')

def get_version():
    """returns a pep complient version number"""
    return '.'.join(str(i) for i in version)

def import_thing(thing):
    """Attempts to import a thing (function, model, form etc)from django's
    import_module doesn't catch any exceptions"""
    # split the path
    parts = thing.split('.')
    # septerate the thing from the path
    thing_cls_name = parts.pop()
    # rebuild the module path
    module = import_module('.'.join(parts))
    # import the thing
    thing = getattr(module, thing_cls_name)
    # return the module and the thing
    return module, thing
