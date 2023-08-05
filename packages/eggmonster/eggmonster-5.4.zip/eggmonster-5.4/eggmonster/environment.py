from . import dictlib

class Environment(dict, dictlib.ItemsAsAttributes):
    """A namespace with a set of defaults.

    Eggmonster applications may use an instance of this class as a
    global configuration namespace.
    """

    def __init__(self, *args, **kwargs):
        super(Environment, self).__init__(*args, **kwargs)
        self._defaults = dict()

    def __missing__(self, k):
        return self._defaults[k]

    def as_obscured_dict(self, keys=['password']):
        """Return ourself as a dict, suitable for public viewing.
        Named items have their value obscured to thwart data leakage.
        """
        def _hide_obscured_names(items, keys):
            """Recursively copy items into a dict, obscuring the named items.
            """
            result = {}
            for key, value in items:
                if isinstance(value, dict):
                    result[key] = _hide_obscured_names(value.items(), keys)
                elif key in keys:
                    result[key] = '********'
                else:
                    result[key] = value
            return result

        return _hide_obscured_names(self._defaults.items() + self.items(), keys)
