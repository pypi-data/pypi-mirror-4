import os
import warnings
import collections

import yaml

class EggmonsterConfigError(Exception): pass

def get_nodes(name, app, options):
    nodes_s = set()
    if not options.get('Enabled', True):
        return nodes_s

    nodes = app.get('Nodes', {})

    for host, count in nodes.iteritems():
        if not type(count) is int:
            raise EggmonsterConfigError("Non-integer value given for node count for app %r" % name)
        for x in xrange(count):
            nodes_s.add((host, x + 1))

    return nodes_s

def get_pkginfo(pkg, pkgmeta):
    pkginfo = pkgmeta.get('Package', '')
    if not pkginfo:
        return ''
    pkginfo = '%s %s' % (pkg, pkginfo)
    return pkginfo

def get_appgroup(pkg, pkgmeta):
    appgroups = pkgmeta.get('Applications')
    if not appgroups:
        raise EggmonsterConfigError("No 'Applications' given for package %r" % pkg)
    return appgroups

def get_options(cfg):
    return cfg.get('Options', {})

def get_instgroup(app, appmeta):
    return appmeta.get('Instances', [])

def get_env(pkgmeta):
    opts = pkgmeta.get('Environment', {})
    return opts

def app_nameinfo(pkg, app):
    name = app.get('Name')
    if not name:
        raise EggmonsterConfigError("No 'Name' given for app in package %r" % pkg)
    entry_point = name
    return entry_point, '%s.%s' % (pkg, name)

def inst_nameinfo(app, inst):
    name = inst.get('Name')
    if not name:
        raise EggmonsterConfigError(
            "No 'Name' given for app in instance %r" % inst)

    # Returns entry point without package name, and full application name.
    return '%s.%s' % (app, name)

class NodeInfo(object):
    def __init__(self, app_name, n, entry_point, env, options, pkginfo):
        # full qualified name ("pkg.appname[.instname]")
        self.app_name = app_name
        # instance number of app_name that is running on the host
        self.n = n
        # application to execute ("appname").
        self.entry_point = entry_point
        # dictionary containing environment
        self.env = env
        # dictionary containing eggmonster running configuration
        self.options = options
        # string containing which package to use
        self.pkginfo = pkginfo

    @property
    def key(self):
        return self.app_name, self.n

    @property
    def cmp_attributes(self):
        return self.app_name, self.n, self.entry_point, self.env, self.options, self.pkginfo

    def __cmp__(self, other):
        if not isinstance(other, NodeInfo):
            return False
        return cmp(self.cmp_attributes, other.cmp_attributes)

    def __str__(self):
        return '<NodeInfo %r>' % (self.cmp_attributes,)

    def __repr__(self):
        return '<NodeInfo %r>' % (self.cmp_attributes,)

class ClusterConfig(object):
    def __init__(self, cobject):
        self.load(cobject)

    def load(self, cobject):
        self.host_nodes = collections.defaultdict(dict)

        # Keys - application name with package.
        # Values: tuple of
        #   - application name without package.
        #   - environment for application.
        #   - package version information.
        #   - options for application. (eggmonster internal)
        self.apps = {}

        # Keys - name of package.
        # Values: tuple of:
        #   - environment for package.
        #   - package version information.
        self.packages = {}

        if not cobject:
            return

        for pkg, pkgmeta in cobject.iteritems():
            pkginfo = get_pkginfo(pkg, pkgmeta)
            pkgconf = get_env(pkgmeta)
            pkgoptions = get_options(pkgmeta)
            self.packages[pkg] = (pkgconf, pkginfo)

            appgroup = get_appgroup(pkg, pkgmeta)
            for app in appgroup:
                app_entry_point, app_name = app_nameinfo(pkg, app)

                app_env = pkgconf.copy()
                app_env.update(get_env(app))

                app_pkginfo = get_pkginfo(pkg, app) or pkginfo

                app_options = pkgoptions.copy()
                app_options.update(get_options(app))

                # Process application nodes.
                nodes = get_nodes(app_name, app, app_options)
                for host, n in nodes:
                    ni = NodeInfo(app_name, n, app_entry_point, app_env, app_options, app_pkginfo)
                    self.host_nodes[host][ni.key] = ni
                self.apps[app_name] = (app_entry_point, app_env, app_pkginfo, app_options)

                # Process instance nodes.
                for inst in get_instgroup(app_name, app):
                    inst_pkginfo = get_pkginfo(pkg, inst) or app_pkginfo

                    inst_env = app_env.copy()
                    inst_env.update(get_env(inst))

                    inst_options = app_options.copy()
                    inst_options.update(get_options(inst))

                    inst_name = inst_nameinfo(app_name, inst)
                    for host, n in get_nodes(inst_name, inst, inst_env):
                        ni = NodeInfo(inst_name, n, app_entry_point, inst_env, inst_options, inst_pkginfo)
                        self.host_nodes[host][ni.key] = ni

                    self.apps[inst_name] = (app_entry_point, inst_env, inst_pkginfo, inst_options)

        return

    def __eq__(self, other):
        return (
            isinstance(other, ClusterConfig)
            and self.apps == other.apps
            and self.packages == other.packages
        )

    @classmethod
    def from_yaml(cls, stream):
        """
        Load config from a stream (or string)
        """
        return cls(yaml.load(stream))

    @classmethod
    def from_file(cls, filename):
        """
        Load config from a pathname
        """
        return cls.from_yaml(open(filename))

#############################
# for backward compatibility
def load_config(*args, **kwargs):
    warnings.warn("load_config is deprecated. Use ClusterConfig.from_file",
        DeprecationWarning,)
    return ClusterConfig.from_file(*args, **kwargs)

def load_config_from_yaml(*args, **kwargs):
    warnings.warn("load_config_from_yaml is deprecated. Use "
        "ClusterConfig.from_yaml",
        DeprecationWarning,)
    return ClusterConfig.from_yaml(*args, **kwargs)
#############################

if __name__ == '__main__':
    filename = os.path.join(os.path.dirname(__file__),
        'test', 'test1.yaml')
    conf = ClusterConfig.from_file(filename)
    host_nodes = {}
    for host, host_dict in conf.host_nodes.items():
        host_nodes[host] = {}
        for ni_key, ni in host_dict.items():
            host_nodes[host][ni_key] = ni.__dict__

    print 'HOST NODES:'
    import pprint
    pprint.pprint(host_nodes)

    print 'APPS:'
    pprint.pprint(conf.apps)
