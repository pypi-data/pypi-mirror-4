import functools

from setuptools.command import easy_install
import pkg_resources
from yg.lockfile import FileLock

from . import emenv

InstallLock = functools.partial(FileLock,
    lockfile = '/tmp/eggmonster-install-lock',
    timeout = 300, # seconds
)

def install(distribution, multi=True):
    return install_many([distribution], multi=multi)

def install_many(distributions, multi=True):
    """
    Install the specified distribution spec from the eggmonster eggserver
    """
    extra_params = emenv.get_easy_install_params()
    with InstallLock():
        easy_install.main([
            '--always-unzip',
            '--multi-version' if multi else '--upgrade',
        ] + extra_params + distributions)

def load_dependencies(req, installer=None):
    """
    Ensure that all dependencies for `req` are loaded.

    `installer`, if supplied, must be a callable that takes a distribution
    and performs the install. If not supplied, no installation will be attempted
    and the first exception will be raised.

    Return the resolved dependency if successful.
    """
    try:
        return pkg_resources.require(req)[0]
    except pkg_resources.VersionConflict, conflict:
        if not installer:
            raise
        found_dist, requirement = conflict.args
        missing_distribution = str(requirement)
    except pkg_resources.DistributionNotFound, dist_not_found:
        if not installer:
            raise
        missing_distribution = str(dist_not_found)

    installer(missing_distribution)

    # take a recursion approach to avoid infinite loops
    return load_dependencies(req, installer)
