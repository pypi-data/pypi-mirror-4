
try:
    import simplejson as json
except:
    import json

from githubcollective.team import Team
from githubcollective.repo import REPO_OPTIONS


class Sync(object):

    def __init__(self, github, verbose=False, pretend=False):
        self.github = github
        self.verbose = verbose
        self.pretend = pretend

    def run(self, new, old):

        # CREATE (OR FORK) REPOS
        if self.verbose:
            print 'CREATED REPOS:'
        to_add = new.repos - old.repos
        for repo in to_add:
            fork_url = new.get_fork_url(repo)
            new_repo = new.get_repo(repo)
            if fork_url is None:
                self.add_repo(old, new_repo)
                if self.verbose:
                    print '    - %s' % repo
            else:
                self.fork_repo(old, fork_url, new_repo)
                if self.verbose:
                    print '    - %s - FORK OF %s' % (repo, fork_url)

            for hook in new_repo.hooks:
                self.add_repo_hook(old, new_repo, hook)
                if self.verbose:
                    print '    - %s - ADDED HOOK: %s (%r)' % (repo,
                                                              hook.name,
                                                              hook.config)

        # REMOVE REPOS
        if self.verbose:
            print 'REPOS TO BE REMOVED:'
        to_remove = old.repos - new.repos
        for repo in to_remove:
            result = self.remove_repo(old, old.get_repo(repo))
            if self.verbose:
                print '    - %s' % repo

        # UPDATE REPOS
        if self.verbose:
            print 'UPDATING REPOS:'
        for repo in new.repos - to_remove:
            old_repo = old.get_repo(repo)
            new_repo = new.get_repo(repo)
            changes = {}
            #Go through differences and create dict of changes
            #Settings removed from config are not modified
            for setting in set(vars(new_repo).keys()).intersection(REPO_OPTIONS):
                if not hasattr(old_repo, setting) or \
                   getattr(old_repo, setting) != getattr(new_repo, setting):
                    changes[setting] = getattr(new_repo, setting)
            if changes:
                self.edit_repo(old, old_repo, changes)
                if self.verbose:
                    print '    - %s' % repo
                    for change, changed_value in changes.items():
                        old_value = getattr(old_repo, change, None)
                        print '      - %s was %r, now %r' % (change,
                                                             old_value,
                                                             changed_value)

            #Go through hooks for changes
            #Hooks removed from configuration are left alone as
            #they may have been manually added upstream.
            if new_repo.hooks:
                old_hooks = old_repo.getGroupedHooks()
                new_hooks = new_repo.getGroupedHooks()
                if old_hooks != new_hooks:
                    #Conditional updating if change has happened in cfg
                    for hook_type, hooks in new_hooks.items():
                        for position_id, hook in enumerate(hooks):
                            if hook_type in old_hooks and \
                               position_id < len(old_hooks[hook_type]):
                                #If attempting to update existing hook
                                old_hook = old_hooks[hook_type][position_id]
                                old_hook_config = vars(old_hook)
                                new_hook_config = old_hook_config.copy()
                                new_hook_config.update(vars(hook))
                                if old_hook_config != new_hook_config:
                                    #If any difference at all, update server
                                    self.edit_repo_hook(old,
                                                        old_repo,
                                                        old_hook.id,
                                                        hook)
                                    if self.verbose:
                                        print '  - %s - EDITED HOOK: %s (%r)' \
                                            % (repo, hook.name, hook.config)

                            else:
                                #Adding a new hook
                                self.add_repo_hook(old, old_repo, hook)
                                if self.verbose:
                                    print '  - %s - ADDED HOOK: %s (%r)' \
                                            % (repo, hook.name, hook.config)

        # CREATE TEAMS
        if self.verbose:
            print 'CREATED TEAMS:'
        to_add = new.teams - old.teams
        for team in to_add:
            self.add_team(old, new.get_team(team))
            if self.verbose:
                print '    - %s' % team

        # REMOVE TEAMS
        if self.verbose:
            print 'REMOVED TEAMS:'
        to_remove = old.teams - new.teams
        for team in to_remove:
            self.remove_team(old, old.get_team(team))
            if self.verbose:
                print '    - %s' % team

        if self.verbose:
            print 'UPDATING TEAMS:'
        for team_name in new.teams - to_remove:

            old_team = old.get_team(team_name)
            if old_team is None:
                continue
            new_team = new.get_team(team_name)
            new_team.id = old_team.id

            # UPDATE TEAM PERMISSION
            if new_team.permission != old_team.permission:
                self.edit_team(old, new_team)
                if self.verbose:
                    print '    - %s - UPDATE PERMISSION: %s -> %s' % (
                            old_team.name, old_team.permission, new_team.permission)


            # ADD MEMBERS
            to_add = new_team.members - old_team.members
            if to_add:
                if self.verbose:
                    print '    - %s - ADDED MEMBERS:' % team_name
                for member in to_add:
                    self.add_team_member(old, old_team, member)
                    print '        - %s' % member


            # REMOVE MEMBERS
            to_remove = old_team.members - new_team.members
            if to_remove:
                if self.verbose:
                    print '    - %s - REMOVED MEMBERS:' % team_name
                for member in to_remove:
                    self.remove_team_member(old, old_team, member)
                    print '        - %s' % member

            # ADD REPOS
            to_add = new_team.repos - old_team.repos
            if to_add:
                if self.verbose:
                    print '    - %s - ADDED REPOS:' % team_name
                for repo in to_add:
                    self.add_team_repo(old, old_team, repo)
                    print '        - %s' % repo

            # REMOVE REPOS
            to_remove = old_team.repos - new_team.repos
            if to_remove:
                if self.verbose:
                    print '    - %s - REMOVED REPOS:' % team_name
                for repo in to_remove:
                    self.remove_team_repo(old, old_team, repo)
                    print '        - %s' % repo

        if self.verbose:
            print 'REQUEST STATS:'
            print '    - request_count: %s' % self.github._request_count
            print '    - request_limit: %s' % self.github._request_limit
            print '    - request_remaining: %s' % self.github._request_remaining

        return True

    #
    # github actions

    def add_repo(self, config, repo):
        config._repos[repo.name] = repo
        return self.github._gh_org_create_repo(repo)

    def add_repo_hook(self, config, repo, hook):
        config._repos[repo.name].hooks.append(hook)
        return self.github._gh_org_create_repo_hook(repo, hook)

    def remove_repo(self, config, repo):
        del config._repos[repo.name]
        return self.github._gh_org_remove_repo(repo)

    def edit_repo(self, config, repo, changes):
        config._repos[repo.name].__dict__.update(changes)
        return self.github._gh_org_edit_repo(repo, changes)

    def edit_repo_hook(self, config, repo, hook_id, hook):
        hook_ids = [getattr(h, 'id', None) \
                    for h in config._repos[repo.name].hooks]
        hook_index = hook_ids.index(hook_id)
        config._repos[repo.name].hooks[hook_index] = hook
        return self.github._gh_org_edit_repo_hook(repo, hook_id, hook)

    def rename_repo(self, config, repo, new_name):
        changes = {'name': new_name}
        config._repos[new_name] = config._repos[repo.name]
        del config._repos[repo.name]
        response = self.github._gh_org_edit_repo(repo, changes)
        config._repos[new_name].__dict__.update(changes)
        return response

    def fork_repo(self, config, fork_url, repo):
        response = self.github._gh_org_fork_repo(fork_url)
        result = json.loads(response.text)
        config._repos[repo.name] = repo

        # Check if we need to rename the fork - forks get the same
        # name by default.
        fork_name = result['name']
        if repo.name != fork_name:
            # Record the name the repo should be
            target_name = repo.name

            # Make our repo and config correctly represent the fork
            config._repos[fork_name] = config._repos[repo.name]
            del config._repos[repo.name]
            repo.name = fork_name

            response = self.rename_repo(config, repo, target_name)

        return response

    def add_team(self, config, team):
        config._teams[team.name] = Team(
                name=team.name,
                permission=team.permission,
                )
        response = self.github._gh_org_create_team(
                name=team.name,
                permission=team.permission,
                )
        if response:
            team_dict = json.loads(response.content)
            config._teams[team.name].id = team_dict['id']
        return response

    def edit_team(self, config, team):
        config._teams[team.name].name = team.name
        config._teams[team.name].permission = team.permission
        return self.github._gh_org_edit_team(
                id=team.id,
                name=team.name,
                permission=team.permission,
                )

    def remove_team(self, config, team):
        del config._teams[team.name]
        return self.github._gh_org_delete_team(team.id)

    def add_team_member(self, config, team, member):
        team = config.get_team(team.name)
        team.members.add(member)
        return self.github._gh_org_add_team_member(team.id, member)

    def remove_team_member(self, config, team, member):
        team = config.get_team(team.name)
        team.members.remove(member)
        return self.github._gh_org_remove_team_member(team.id, member)

    def add_team_repo(self, config, team, repo):
        team = config.get_team(team.name)
        team.repos.add(repo)
        return self.github._gh_org_add_team_repo(team.id, repo)

    def remove_team_repo(self, config, team, repo):
        team = config.get_team(team.name)
        team.repos.remove(repo)
        return self.github._gh_org_remove_team_repo(team.id, repo)
