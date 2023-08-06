"""
Git repository manager.

Capable of installing, updating, and uninstalling large number of Git repositories
"""
import os

from fabric.api import local, lcd as cd

__version__ = '0.0.1'


class GitWarden(object):
    def __init__(self, remote_config='remotes.txt', repo_dir='repos'):
        self.remote_config = remote_config
        self.repo_dir = repo_dir

    @property
    def remotes(self):
        with open(self.remote_config) as f:
            for remote in f:
                yield remote

    @property
    def repos(self):
        for repo in os.listdir(self.repo_dir):
            yield repo

    def install(self, remote=None):
        """Install a git repo or all of them."""
        if remote:
            with cd(self.repo_dir):
                local('git clone %s' % remote)
        else:
            for remote in self.remotes:
                self.install(remote)

    def update(self, repo=None):
        """Update a git repo or all of them."""
        if repo:
            with cd(self.repo_dir):
                with cd(repo):
                    local('git pull')
        else:
            for repo in self.repos:
                self.update(repo)

    def uninstall(self, repo=None):
        """Uninstall a git repo or all of them."""
        if repo:
            with cd(self.repo_dir):
                local('rm -fr %s' % repo)
        else:
            for repo in self.repos:
                self.uninstall(repo)
