"""
lxc containers
==============
"""
from fabric.api import *


def create(name, template, config=None):
    """
    Create lxc container
    """
    if config:
        sudo('lxc-create --name %(name)s --template %(template)s --config %(config)s' % locals())
    else:
        sudo('lxc-create --name %(name)s --template %(template)s' % locals())


def destroy(name):
    """
    Destroy lxc container
    """
    sudo('lxc-destroy --name %(name)s' % locals())


def start(name):
    """
    Start lxc container
    """
    sudo('lxc-start --name %(name)s' % locals())


def stop(name):
    """
    Stop lxc container
    """
    sudo('lxc-stop --name %(name)s' % locals())
