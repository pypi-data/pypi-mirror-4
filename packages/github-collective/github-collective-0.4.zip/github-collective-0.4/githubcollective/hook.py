import json

HOOK_BOOL_OPTIONS = ('active',)
HOOK_OPTIONS = HOOK_BOOL_OPTIONS + ('id', 'name', 'config', 'events')

class Hook(object):

    config = ''

    def __init__(self, **kw):
        self.__dict__.update(kw)
        #Handle case of unicode coming from GitHub
        self.name = unicode(self.name)
        if isinstance(self.config, str):
            try:
                self.config = json.loads(self.config)
            except ValueError:
                raise ValueError("Error parsing JSON config for %r" % self)

    def __repr__(self):
        return '<Hook "%s">' % self.name

    def __str__(self):
        return self.__repr__()

    def dumps(self):
        return dict((k, v) for k, v in self.__dict__.iteritems()
                    if k in HOOK_OPTIONS)
