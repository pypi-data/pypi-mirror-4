"""
EGGMonster clients/servers may define environment variables pointing
at the essential hosts needed by the eggmonster services. If not set, these
variables will default to reasonable values which must resolve in the local
domain.

- EGGMONSTER_CHEESESHOP refers to the PyPI (package index) or cheese shop.
  It should be an HTTP endpoint suitable for retrieving the packages
  required by eggmonster. Defaults to http://cheeseshop.
- EGGMONSTER_MASTER refers to the eggmonster master server, where the
  master configuration is stored. Defaults to http://eggmaster.
- EGGMONSTER_EASY_INSTALL_PARAMS supplies explicit parameters to be passed
  to the easy_install command. If not supplied, eggmonster will supply -f
  (find-links) and -H (allow-hosts) referring to the EGGMONSTER_CHEESESHOP.
  If supplied, EGGMONSTER_CHEESESHOP will be ignored and these parameters will
  be passed directly to the easy_install command. The parameters will be
  parsed with shlex. The value may also be set to the special value "Suppress",
  in which case no parameters will be passed to easy_install (and it will
  use the default settings, such as those found in distutils.cfg).
"""

import os
import urlparse
import shlex

#primary
cheeseshop = os.environ.get('EGGMONSTER_CHEESESHOP', 'http://cheeseshop')
master = os.environ.get('EGGMONSTER_MASTER', 'http://eggmaster')
easy_install_params = os.environ.get('EGGMONSTER_EASY_INSTALL_PARAMS')

def http_url_to_host_port(url):
    parsed = urlparse.urlparse(url)
    host, sep, port = parsed.netloc.partition(':')
    port = int(port) if port else dict(http=80, https=443)[parsed.scheme.lower()]
    return host, port

def get_easy_install_params():
    """
    Construct the parameters to be passed to easy_install when eggmonster
    installs applications. See the module:emenv docs for details.
    """
    if easy_install_params is None:
        # Traditional behavior - use eggmonster cheeseshop using find_links
        server = cheeseshop
        hostname = urlparse.urlparse(server).netloc
        return [
            "-H", hostname,
            "-f", server,
        ]

    if easy_install_params.lower() == "suppress":
        # Use system default behavior
        return []

    # use the parameters from the environment
    return shlex.split(easy_install_params)

# derived
cheeseshop_host, cheeseshop_port = http_url_to_host_port(cheeseshop)


master_host, master_control_port = http_url_to_host_port(master)
master_launch_port = master_control_port + 1
master_emi_port = master_control_port + 2
