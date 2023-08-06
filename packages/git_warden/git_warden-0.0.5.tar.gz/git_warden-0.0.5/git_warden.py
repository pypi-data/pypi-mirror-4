"""
Git repository manager.

Installs, updates, and uninstalls large number of Git repositories
"""
import os

from fabric.api import local, lcd as cd


def install(repo_dir, remote):
    """Install a git repo in a directory."""
    with cd(repo_dir):
        local('git clone %s' % remote)


def install_remotes(repo_dir, remotesfilename):
    """Install git repo from a config file in a directory."""
    with open(remotesfilename) as f:
        for remote in f:
            install(remote, repo_dir)


def update(repo_dir, repo=None):
    """Update a git repo in a directory."""
    if repo:
        with cd(repo_dir):
            with cd(repo):
                local('git pull')
    else:
        for repo in os.listdir(repo_dir):
            update(repo, repo_dir)


def uninstall(repo_dir, repo=None):
    """Uninstall a git repo in a directory."""
    if repo:
        with cd(repo_dir):
            local('rm -fr %s' % repo)
    else:
        for repo in os.listdir(repo_dir):
            uninstall(repo_dir, repo)
