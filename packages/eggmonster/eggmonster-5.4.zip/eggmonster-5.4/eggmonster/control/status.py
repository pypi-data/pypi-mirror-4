"""Output eggmonster status."""

import signal
from collections import defaultdict

from eggmonster.control._common import getjson, timestr, reset_sigpipe

def _statline_to_dict(sl):
	if isinstance(sl, dict): return sl
	host_info, launch_info = sl
	host, app_name, num = host_info
	launch_time, conf_sync = launch_info
	return dict(
		host = host, app_name = app_name, num = num,
		launchtime = launch_time, conf_sync = conf_sync,
		)

def getstatus():
    status = getjson('status')
    servertime, statlines = status
    statlines = map(_statline_to_dict, statlines)
    return servertime, statlines

def main():
    reset_sigpipe()

    servertime, statlines = getstatus()

    packages = defaultdict(lambda: defaultdict(list))

    for statline in statlines:
        host = statline['host']
        app_id = statline['app_name']
        num = statline['num']
        ts = statline.get('launchtime', 0)
        conf_sync = statline.get('conf_sync', True)
        pkg_ver = statline['pkg_ver'] if statline.get('pkg_ver_diff') else ''

        package, app = app_id.split('.', 1)
        packages[package][app].append((host, num, ts, conf_sync, pkg_ver))

    for pname, apps in sorted(packages.items()):
        for a, nodes in sorted(apps.items()):
            for host, num, ts, conf_sync, pkg_ver in sorted(nodes):
                if ts:
                    uptime = timestr(servertime - ts, 2).strip()
                else:
                    uptime = 'DOWN'
                extra = ''
                if (not conf_sync) or pkg_ver:
                    extra = '[%s%s]' % (pkg_ver, ('*' if not conf_sync else ''))
                print '%s.%s (%s:%s) %s %s' % (
                pname, a, host, num, uptime, extra)
