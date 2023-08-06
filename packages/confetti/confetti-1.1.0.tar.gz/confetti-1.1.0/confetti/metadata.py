from .config import Config

class Metadata(object):
    def __init__(self, **kwargs):
        super(Metadata, self).__init__()
        self.metadata = kwargs
    def __rfloordiv__(self, value):
        return Config(value, metadata=self.metadata)
