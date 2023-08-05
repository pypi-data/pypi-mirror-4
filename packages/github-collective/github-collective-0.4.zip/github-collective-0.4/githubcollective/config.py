
try:
    import simplejson as json
except:
    import json

import os
import re
import requests
import ConfigParser
import StringIO
from githubcollective.team import Team
from githubcollective.repo import Repo, REPO_BOOL_OPTIONS, \
        REPO_RESERVED_OPTIONS
from githubcollective.hook import Hook, HOOK_BOOL_OPTIONS


BASE_URL = 'https://api.github.com'
TEAM_PREFIX = '--auto-'
TEAM_OWNERS_SUFFIX = '-owners'
LOCAL_SECTION_PREFIXES = ('repo',)


class Config(object):

    def __init__(self, filename, verbose, pretend):
        self._teams = {}
        self._repos = {}
        self._fork_urls = {}

        self.filename = filename
        self.verbose = verbose
        self.pretend = pretend

        if type(filename) is file:
            data = filename.read()
        elif type(filename) in [str, unicode] and \
             self.is_url(filename):
            response = requests.get(filename)
            response.raise_for_status()
            data = response.text
        elif type(filename) in [str, unicode] and \
             os.path.exists(filename):
            f = open(filename)
            data = f.read()
            f.close()
        else:
            data = filename

        if data:
            self._teams, self._repos, self._fork_urls = self.parse(data)

    def parse(self, data):
        teams, repos = {}, {}
        data = json.loads(data)

        for team in data['teams']:
            team = Team(**team)
            teams[team.name] = team

        for repo in data['repos']:
            if repo['hooks']:
                repo['hooks'] = [Hook(**hook) for hook in repo['hooks']]
            repo = Repo(**repo)
            repos[repo.name] = repo

        return teams, repos, data['fork_urls']

    def dumps(self, cache):
        if cache.mode != 'w+':
            cache = open(cache.name, 'w+')
        cache.truncate(0)
        cache.seek(0)
        json.dump({
            'teams': [self._teams[name].dumps() for name in self.teams],
            'repos': [self._repos[name].dumps() for name in self.repos],
            'fork_urls': self._fork_urls,
            }, cache, indent=4)

    def is_url(self, url):
        return url.startswith('http')

    @property
    def teams(self):
        return set(self._teams.keys())

    def get_team(self, name):
        return self._teams.get(name, None)

    def get_team_members(self, name):
        members = []
        team = self.get_team(name)
        if team:
            members = team.members
        return set(members)

    def get_team_repos(self, name):
        repos = []
        team = self.get_team(name)
        if team:
            repos = team.repos
        return set(repos)

    @property
    def repos(self):
        return set(self._repos.keys())

    def get_repo(self, name):
        return self._repos.get(name, None)

    def get_fork_url(self, repo):
        return self._fork_urls.get(repo, None)


_template_split = re.compile('([$]{[^}]*?})').split

def substitute(value, config, context=None, local=False, stack=()):
    """Carry out subsitution of values in the form ${section:option}.

    `value`: the original value to have substitution applied.
    `config`: an instance of a ConfigParser.
    `context`: the identifier of the current section context (used to
    determine empty section name lookups).
    `stack`: the current tuple of fields inspected through recursion.
    `local`: resolve local references (eg Hook references Repo) against
    the given ``context``.

    Strongly influenced by what ``zc.buildout`` does.
    """
    parts = _template_split(value)
    subs = []
    for ref in parts[1::2]:
        option_parts = tuple(ref[2:-1].rsplit(':', 1))
        if len(option_parts) < 2:
            raise ValueError("The substitution %s is missing a colon." % ref)
        section, option = option_parts

        #Support ${:option} and ${repo:option} syntaxes
        if not section or local:
            section = context

        #Only lookup now if substituting from global config
        if section not in LOCAL_SECTION_PREFIXES:
            sub = config.get(section, option)

            #Recurse accordingly to resolve nested substitution
            if '${' in sub:
                if ref in stack:
                    circle = ' --> '.join(stack + (ref,) )
                    raise ValueError(
                        "Circular reference in substitutions %s." % circle
                    )
                sub = substitute(value=sub,
                                 config=config,
                                 context=section,
                                 stack=stack + (ref,))
            subs.append(sub)
        #Leave alone until we process the context
        else:
            subs.append(ref)
    subs.append('')

    #Rejoin normal parts and resolved substititions
    substitution = ''.join([''.join(v) for v in zip(parts[::2], subs)])
    return substitution

def global_substitute(config):
    """Take care of all global configuration substitutions.

    This function will not adjust `local` substitions as these
    cannot be resolved until a relevant context is available later.
    `config` will be modified in place.
    """
    for section in config.sections():
        for option, value in config.items(section):
            if '${' in value:
                sub_value = substitute(value=value,
                                       config=config,
                                       context=section,
                                       local=False)
                config.set(section, option, sub_value)

def load_config(data):
    """Load configuration using string data."""
    config = ConfigParser.SafeConfigParser()
    config.readfp(StringIO.StringIO(data))
    return config

def output_config(config):
    """Output configuration back to string."""
    result = StringIO.StringIO()
    config.write(result)
    return result.getvalue().expandtabs(4)


class ConfigCFG(Config):

    def parse(self, data):
        teams, repos, fork_urls = {}, {}, {}
        config = load_config(data)

        # global substitutions in ${section:option} style
        global_substitute(config)
        if self.verbose:
            print 'RESOLVED CONFIGURATION:\n'
            print output_config(config)

        for section in config.sections():
            if section.startswith('repo:'):
                # add repo
                name = section[len('repo:'):]
                # load configuration for repo
                repo_config = dict(config.items(section))
                # remove reserved properties
                for option in REPO_RESERVED_OPTIONS:
                    if option in repo_config:
                        del repo_config[option]
                # coerce boolean values
                for option in REPO_BOOL_OPTIONS:
                    if option in repo_config:
                        repo_config[option] = config.getboolean(section,
                                                                option)
                # load hooks for repo
                hooks = []
                if config.has_option(section, 'hooks'):
                    for hook in config.get(section, 'hooks').split():
                        hook_section = 'hook:%s' % hook
                        hook_config = {}
                        for config_key, config_value in config.items(hook_section):
                            # local variable substitution
                            if '${' in config_value:
                                config_value = substitute(value=config_value,
                                                          config=config,
                                                          context=section,
                                                          local=True)

                            # coerce values into correct formats
                            if config_key == 'config':
                                config_value = config_value.replace('\n', '')
                            elif config_key == 'events':
                                config_value = config_value.split()

                            if config_key in HOOK_BOOL_OPTIONS:
                                config_value = config.getboolean(hook_section,
                                                                 config_key)
                            hook_config[config_key] = config_value

                        hooks.append(Hook(**hook_config))

                repos[name] = Repo(name=name, hooks=hooks, **repo_config)
                # add fork
                if config.has_option(section, 'fork'):
                    fork_urls[name] = config.get(section, 'fork')
                # add owners team
                if config.has_option(section, 'owners'):
                    team_name = TEAM_PREFIX + name + TEAM_OWNERS_SUFFIX
                    team_members = config.get(section, 'owners').split()
                    teams[team_name] = Team(team_name, 'admin',
                            members=team_members, repos=[name])
            elif section.startswith('team:'):
                # add team
                name = TEAM_PREFIX + section[len('team:'):]
                permission = 'pull'
                if config.has_option(section, 'permission'):
                    permission = config.get(section, 'permission')
                members = []
                if config.has_option(section, 'members'):
                    members = config.get(section, 'members').split()
                team_repos = []
                if config.has_option(section, 'repos'):
                    team_repos = config.get(section, 'repos').split()
                teams[name] = Team(name, permission,
                        members=members, repos=team_repos)

        # add repos to teams (defined with repo: section
        for section in config.sections():
            if section.startswith('repo:'):
                if config.has_option(section, 'teams'):
                    for team in config.get(section, 'teams').split():
                        teams[TEAM_PREFIX + team].repos.add(
                                section[len('repo:'):],
                                )

        return teams, repos, fork_urls

class ConfigGithub(Config):

    def __init__(self, github, cache, verbose=False, pretend=False):
        self.github = github
        self._github = {'teams': {}, 'repos': {}}

        data = None
        if cache:
            data = cache.read()
        super(ConfigGithub, self).__init__(data, verbose, pretend)
        if cache and not data:
            print 'CACHE DOES NOT EXISTS! CACHING...'
            self.dumps(cache)
            print 'CACHE WRITTEN TO %s!' % cache.name

    def _get_teams(self):
        if 'teams' not in self._github.keys() or \
           not self._github['teams']:
            self._github['teams'] = {}
            for item in self.github._gh_org_teams():
                if not item['name'].startswith(TEAM_PREFIX):
                    continue
                item.update(self.github._gh_team(item['id']))
                team = Team(**item)
                if team.members_count > 0:
                    team.members.update([i['login']
                            for i in self.github._gh_team_members(item['id'])])
                if team.repos_count > 0:
                    team.repos.update([i['name']
                            for i in self.github._gh_team_repos(item['id'])])
                self._github['teams'][team.name] = team
        return self._github['teams']
    def _set_teams(self, value):
        self._github['teams'] = value
    def _del_teams(self):
        del self._github['teams']
    _teams = property(_get_teams, _set_teams, _del_teams)

    def _get_repos(self):
        if 'repos' not in self._github.keys() or \
           not self._github['repos']:
            self._github['repos'] = {}
            for item in self.github._gh_org_repos():
                hooks = []
                for hook in self.github._gh_org_repo_hooks(item['name']):
                    hooks.append(Hook(**hook))
                repo = Repo(hooks=hooks, **item)
                self._github['repos'][repo.name] = repo
        return self._github['repos']
    def _set_repos(self, value):
        self._github['repos'] = value
    def _del_repos(self):
        del self._github['repos']
    _repos = property(_get_repos, _set_repos, _del_repos)

