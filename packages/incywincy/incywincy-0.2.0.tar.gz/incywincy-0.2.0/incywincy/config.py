class Settings(dict):
    """
    Application settings, that will typically be loaded from a module.
    """
    def __init__(self):
        self._mod = None

    def load(self, module):
        self.module = module
        if self._mod is None:
            self._mod = __import__(self.module, globals(), locals(), [], -1)
            for attr in dir(self._mod):
                if not attr.startswith('__'):
                    self[attr] = getattr(self._mod, attr)

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value


settings = Settings()
