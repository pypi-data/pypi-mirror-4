"""
Users
=====
"""
from __future__ import with_statement

from fabric.api import *


def exists(name):
    """
    Check if a user exists.
    """
    with settings(hide('running', 'stdout', 'warnings'), warn_only=True):
        return sudo('getent passwd %(name)s' % locals()).succeeded


def create(name, home=None, shell=None, uid=None, gid=None, groups=None):
    """
    Create a new user.

    Example::

        import fabtools

        if not fabtools.user.exists('alice'):
            fabtools.user.create('alice', home='/home/alice')

    """
    options = []
    if gid:
        options.append('--gid "%s"' % gid)
    if groups:
        if not isinstance(groups, basestring):
            groups = ','.join('"%s"' % group for group in groups)
        options.append('--groups %s' % groups)
    if home:
        options.append('--home-dir "%s"' % home)
    if shell:
        options.append('--shell "%s"' % (shell))
    if uid:
        options.append('--uid %s' % uid)
    options = " ".join(options)
    sudo('useradd %(options)s %(name)s' % locals())
