import json


class BaseBackend(object):
    """
    BaseBackend must subclassed by custom backends to be used. It only
    define basic utilities to help writing backends
    """

    def __init__(self, **kwargs):
        self.template = None
        self.name = kwargs.pop('name')
        self.data = json.dumps(self.fetch(self.name, **kwargs))

    def fetch(self, method, **kwargs):
        """
        Return a set of data formated information
        """
        meth = getattr(self, method, **kwargs)
        return meth()
