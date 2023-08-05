loading = False


class Settings(dict):
    """
    Lazyly loaded settings.
    """
    def __init__(self, module):
        self.module = module
        self._mod = None

    def load(self):
        if self._mod is None:
            self._mod = __import__(self.module, globals(), locals(), [], -1)
            for attr in dir(self._mod):
                if not attr.startswith('__'):
                    self[attr] = getattr(self._mod, attr)

    def __getattr__(self, attr):
        global loading
        if not loading:
            loading = True
            self.load()
            loading = False
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value
