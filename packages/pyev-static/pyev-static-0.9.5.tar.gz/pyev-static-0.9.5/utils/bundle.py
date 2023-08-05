import os
import tarfile
import shutil
from os.path import join as pjoin, exists as pexists
from urllib2 import urlopen
from subprocess import Popen, PIPE

from .msg import info, fatal

bundled_version = (4, 4)
libev = "libev-{0}.{1:02d}.tar.gz".format(*bundled_version)
libev_url = "http://dist.schmorp.de/libev/Attic/" + libev


def fetch_archive(savedir, url, fname, force=False):
    """Download an archive to a specific location."""
    dest = pjoin(savedir, fname)
    if pexists(dest) and not force:
        info("Already have %s" % fname)
        return dest
    info("fetching %s into %s" % (url, savedir))
    if not pexists(savedir):
        os.makedirs(savedir)
    req = urlopen(url)
    with open(dest, 'wb') as f:
        f.write(req.read())
    return dest


def fetch_libev(savedir):
    """Download and extract libev."""
    dest = pjoin(savedir, 'libev')
    if os.path.exists(dest):
        info("already have %s" % dest)
        return
    fname = fetch_archive(savedir, libev_url, libev)
    tf = tarfile.open(fname)
    with_version = pjoin(savedir, tf.firstmember.path)
    tf.extractall(savedir)
    tf.close()
    # remove version suffix:
    shutil.move(with_version, dest)


def configure(root):
    """Tries to run ./configure."""
    if os.path.exists(pjoin(root, 'config.h')):
        info("libev already configured")
        return
    configure = pjoin(root, 'configure')
    if not os.access(configure, os.X_OK):
        os.chmod(configure, 0755)
    info("Attempting to execute ./configure")
    p = Popen('./configure', cwd=root, shell=True,
            stdout=PIPE, stderr=PIPE,
        )
    output, error = p.communicate()
    if p.returncode:
        fatal("failed to configure libev:\n%s" % error)
