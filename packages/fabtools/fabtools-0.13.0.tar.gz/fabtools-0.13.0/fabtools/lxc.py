"""
lxc containers
==============
"""

from fabtools.utils import run_as_root


def create(name, template, config=None):
    """
    Create lxc container
    """
    if config:
        run_as_root('lxc-create --name %(name)s --template %(template)s --config %(config)s' % locals())
    else:
        run_as_root('lxc-create --name %(name)s --template %(template)s' % locals())


def destroy(name):
    """
    Destroy lxc container
    """
    run_as_root('lxc-destroy --name %(name)s' % locals())


def start(name):
    """
    Start lxc container
    """
    run_as_root('lxc-start --name %(name)s' % locals())


def stop(name):
    """
    Stop lxc container
    """
    run_as_root('lxc-stop --name %(name)s' % locals())
