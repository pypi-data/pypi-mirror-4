from sce.utils import getcallargs
from starcluster.logger import log
from decorator import decorator
import os
from datetime import datetime

def add2file(file,line,sudo=False,node=None,del_if_exists=True):
    """
    Adds line to file if it does not exist
    if node is none, just return the command

    :param del_if_exists: if False, skip check for existing line and append no matter what.
    """
    if del_if_exists:
        sed_delete(file,regex=line,node=node,sudo=sudo)

    sudo = 'sudo ' if sudo else ''
    cmd = "{sudo}bash -c \"echo '{1}' >> {0}\"".format(file,line,sudo=sudo)
    log.info('exec({0}): {1}'.format(node if node else '<local>',cmd))
    if node:
        return node.ssh.execute(cmd)
    else:
        os.system(cmd)

def sed_delete(file,regex,node=None,sudo=False):
    sudo = 'sudo ' if sudo else ''
    cmd = "{sudo}sed '/{0}/d' {1}".format(regex,file,sudo=sudo)
    log.info('exec({0}): {1}'.format(node if node else '<local>',cmd))
    if node:
        return node.ssh.execute(cmd)
    else:
        os.system(cmd)


def apt_update(node):
    """
    apt-update if it hasn't been done in the past few days
    """
    s = node.ssh.execute('stat -c %y /var/lib/apt/periodic/update-success-stamp')[0]
    dt = datetime.now() - datetime.strptime(s[:10],"%Y-%m-%d")
    if dt.days > 2:
        log.info("Running apt-get update -y on {0}".format(node))
        node.ssh.execute('apt-get update -y')

def cluster_name(node):
    return node.parent_cluster.name.replace('@sc-','')


def catchall(f,*args,**kwargs):
    """Catch all exceptions and return"""
    try:
        return f(*args,**kwargs)
    except Exception as e:
        log.error('Plugin unsuccessful!')
        log.exception(e)
        if hasattr(e,'exceptions'):
            for e2 in e.exceptions:
                if type(e2) == list:
                    for e3 in e2:
                        log.error(e3)
                else:
                    log.error(e2)

def _trace(f, *args, **kwargs):
    callargs = getcallargs.getcallargs(f,*args,**kwargs)
    del callargs['self']
    log.info(
        '{0}({1})'.format(
            f.__name__,
            ', '.join(
                map(lambda i: '{0[0]}={0[1]}'.format(i),callargs.items())
            )
        )
    )
    return f(*args, **kwargs)

def trace(f):
    """
    Automatically logs the decorated method and its parameters each time it is called.
    :param f: the method
    """
    return decorator(_trace, f)

