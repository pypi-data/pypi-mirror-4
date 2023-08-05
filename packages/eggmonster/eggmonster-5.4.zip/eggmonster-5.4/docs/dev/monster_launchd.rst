^^^^^^^^^^^^^^^
monster_launchd
^^^^^^^^^^^^^^^

Usage: ``monster_launchd [options]``

Arguments
~~~~~~~~~

None.

Options
~~~~~~~

-u/--user:
	The user under which managed processes will be run. By default, processes
	will run under the current user.

-i/--host-id:
	The host id to use when communicating with the eggmonster server. By
	default, uses `platform.node()`.

--debug:
	Output debugging information about managed processes.

Discussion
~~~~~~~~~~

The ``monster_launchd`` daemon sends its host id to the "launchd" service of a
``monster_server`` daemon. The ``monster_server`` replies with instructions on
what application to run based on configuration owned by ``monster_server``. The
``monster_launchd`` process then launches an ``emi`` process, which makes a
connection directly to the "emi" service of the ``monster_server`` daemon. In
this way the ``monster_server`` is able to report to users of the ``em`` tool
on the status of processes within the cluster.

The ``emi`` process when starting up an application uses ``setuptools`` to find
the entry point and handle dependencies. It will attempt to load the dependencies
from the monster_eggserver (or any other URL with a directory listing) as
referenced by the environment variable ``EGGMONSTER_CHEESESHOP``. When it
installs the dependencies, it installs them as "multiversion" in order to
allow multiple versions of the library to be installed (and used by different
applications in the same environment).

After loading dependencies, and if the ``--user`` parameter was specified, the
``emi`` process will attempt to switch to that user context.

The entry point defines the function to call that will run the server and the
configuration section from the eggmonster config to use.


