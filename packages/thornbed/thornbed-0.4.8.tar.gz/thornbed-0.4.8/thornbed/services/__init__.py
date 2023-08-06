from importlib import import_module
import os
import glob, imp


def _load(path):
    name, ext = os.path.splitext(os.path.basename(path))
    return name, imp.load_source(name, path)

def get_providers():
    path = os.path.relpath(os.path.dirname(__file__))

    files = glob.glob(os.path.join(path,'[!_]*.py'))
    modules = dict(_load(path) for path in files)
    providers = []
    for name, module in modules.items():
        func = None
        try:
            func = getattr(module, 'lookup')
        except AttributeError:
            continue
        providers.append((name, func))

    return providers