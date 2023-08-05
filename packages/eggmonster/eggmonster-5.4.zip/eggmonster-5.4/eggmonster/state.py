import itertools
from collections import defaultdict
import time

class RunningState(object):
    """
    Represents the current state of nodes in the system and the
    currently-configured state. The two will usually be the same except
    for the interim when changes are made but not yet synched with
    the nodes.
    """
    def __init__(self):
        # This represents the current state as Eggmonster understands
        # it - what services are currently running.
        #
        # Structure:
        #   KEY: hostname
        #   VALUE: dict
        #     KEY: key attribute of NodeInfo instance in VALUE
        #     VALUE: (config.NodeInfo instance, time-started)
        self.hosts = defaultdict(dict)

    def update_config(self, conf):
        # This represents the current configuration as described by
        # the latest configuration file.
        #
        # Structure:
        #   KEY: hostname
        #   VALUE: dict
        #     KEY: key attribute of NodeInfo instance in VALUE
        #     VALUE: config.NodeInfo instance
        self.conf = conf.host_nodes
        self.packages = conf.packages

    def launch_check(self, host):
        """
        Determine which nodes need to be launched; checks discrepancies
        between the current state and the described config.
        Return NodeInfo instances of nodes to be launched.
        """
        return (node
            for (key, node) in self.conf[host].iteritems()
            if key not in self.hosts[host]
            )

    def kill_check(self, check_conf_diff=True):
        """
        Determine which nodes need to be launched; checks discrepancies
        between the current state and the described config.
        Return (host, NodeInfo) tuples describing the process to
        terminate (and presumably restart) or start.
        """
        for host, nodes in self.hosts.iteritems():
            for key, (node, tm) in nodes.iteritems():
                existing_config = self.conf[host].get(key)
                if not existing_config:
                    # this is a new node - it needs to be started
                    yield host, node
                elif check_conf_diff and (existing_config != node):
                    # the config has changed and we care
                    yield host, node

    def node_started(self, host, node):
        "Update the state for a node (usually when started)"
        self.hosts[host][node.key] = (node, time.time())

    def node_stopped(self, host, node):
        "Remove the state for a node (usually when stopped)"
        if node.key in self.hosts[host]:
            del self.hosts[host][node.key]

    @property
    def status(self):
        """
        Return the status for each node as a dictionary to include the
        following:
          - hostname (str)
          - appname (str)
          - num (int)
          - pkg_ver (str)
          - pkg_ver_diff (bool)
        For nodes that are running, the following additional indicators
        are provided:
          - conf_sync (bool)
          - launchtime (int)

        For conf_sync, it returns a flag indicating whether the
        configuration used by the node matches the server configuration.

        For version, we only put the package version for an application
        if it differs from the main package version.
        """
        seen = set()
        for host in self.hosts:
            for key, (node, tm) in self.hosts[host].iteritems():
                node_info = (host, node.app_name, node.n)
                seen.add(node_info)
                try:
                    conf_node = self.conf[host][key]
                except KeyError:
                    # This means that the configuration no longer references
                    # a node that is being monitored by EM.
                    #
                    # We have no idea what the intended configuration was, so
                    # don't flag it as being inconsistent.
                    conf_sync = True
                else:
                    conf_sync = conf_node == node

                pkg_ver, pkg_info = self._pkg_info(node)

                yield dict(
                    host = host,
                    app_name = node.app_name,
                    num = node.n,
                    pkg_ver = pkg_ver,
                    pkg_ver_diff = node.pkginfo != pkg_info,
                    launchtime = tm,
                    conf_sync = conf_sync,
                )

        for host in self.conf:
            for node in self.conf[host].itervalues():
                node_info = (host, node.app_name, node.n)
                if node_info in seen:
                    continue
                pkg_ver, pkg_info = self._pkg_info(node)
                yield dict(
                    host=host,
                    app_name=node.app_name,
                    num=node.n,
                    pkg_ver=pkg_ver,
                    pkg_ver_diff=node.pkginfo!=pkg_info
                )

    def _pkg_info(self, node):
        # we can't deterministically grab the package name from the node.app_name
        #  because we've appended '.appname' and possibly '.instancename' to
        #  the package name, which itself could have a dot in it, so search
        #  through the list of packages until we find a match.
        pkg_name = one(
            pkg_name for pkg_name in self.packages
            if node.app_name.startswith(pkg_name)
        )
        pkg_info = self.packages[pkg_name][1] # 'packagename == 0.1.1.4'
        pkg_ver = ''.join(node.pkginfo.split(' ')[1:]) # '==0.1.1.4'
        return pkg_ver, pkg_info

# from jaraco.util.iter_
def one(item):
    """
    Return the first element from the iterable, but raise an exception
    if elements remain in the iterable after the first.

    >>> one(['val'])
    'val'
    >>> one(['val', 'other'])
    Traceback (most recent call last):
    ...
    ValueError: item contained more than one value
    >>> one([])
    Traceback (most recent call last):
    ...
    StopIteration
    """
    iterable = iter(item)
    result = next(iterable)
    if tuple(itertools.islice(iterable, 1)):
        raise ValueError("item contained more than one value")
    return result
