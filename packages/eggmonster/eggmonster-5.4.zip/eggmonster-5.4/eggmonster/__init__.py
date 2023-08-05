import pkg_resources
import yaml

from .environment import Environment

def load_version_info():
    "load version info and version from package resources"
    global __version_info__, __version__
    __pkg__ = pkg_resources.require('eggmonster')[0]
    __version_info__ = tuple(
        (int(x) if x.isdigit() else x)
        for x in __pkg__.parsed_version
    )
    __version__ = '.'.join(str(x) for x in __version_info__)
load_version_info()

logger_port = 13000

env = Environment()

def clear_defaults():
    env._defaults.clear()

def update_defaults(e):
    env._defaults.update(e)

def clear_locals():
    env.clear()

def update_locals(e):
    env.update(e)

def load_default_yaml(string='', file=None, sub=None):
    load_yaml(update_defaults, string=string, file=file, sub=sub)

def load_local_yaml(string='', file=None, sub=None):
    load_yaml(update_locals, string=string, file=file, sub=sub)

def load_yaml(loader, string='', file=None, sub=None):
    """Update the global env with the given YAML.

    If 'sub' is given, it should be a callable that returns
    a subkey of the loaded YAML; e.g. lambda x: x['bix']
    """
    if file:
        string = open(file).read()
    if string.strip():
        opts = yaml.load(string)
        if sub:
            opts = sub(opts)
        assert type(opts) is dict
        loader(opts)

_man_env = [False]

def managed_env():
    return _man_env[0]

def _set_managed_env():
    _man_env[0] = True
