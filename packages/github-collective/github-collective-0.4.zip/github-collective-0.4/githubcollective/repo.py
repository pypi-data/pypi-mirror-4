REPO_RESERVED_OPTIONS = ('fork', 'owners', 'teams', 'hooks')
REPO_BOOL_OPTIONS = ('private', 'has_issues', 'has_wiki', 'has_downloads')
REPO_OPTIONS = REPO_BOOL_OPTIONS + ('name', 'description', 'homepage', 'team_id')

class Repo(object):

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __repr__(self):
        return '<Repo "%s">' % self.name

    def __str__(self):
        return self.__repr__()

    def dumps(self):
        dump = dict((k, v) for k, v in self.__dict__.iteritems()
                    if k in REPO_OPTIONS)
        dump['hooks'] = [hook.dumps() for hook in self.hooks]
        return dump

    def getGroupedHooks(self):
        """GitHub repos can only have 1 of each hook, except `web`."""
        hooks = {}
        for hook in self.hooks:
            if hook.name != 'web':
                hooks[hook.name] = [hook]
            else:
                if 'web' not in hooks:
                    hooks['web'] = []
                hooks['web'].append(hook)
        return hooks
