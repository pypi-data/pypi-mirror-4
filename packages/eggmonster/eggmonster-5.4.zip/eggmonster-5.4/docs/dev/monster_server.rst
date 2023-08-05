^^^^^^^^^^^^^^
monster_server
^^^^^^^^^^^^^^

Usage: ``monster_server [options] <config_dir>``

Arguments
~~~~~~~~~

config_dir:
    A directory where the revisioned configuration files will live. The
    configuration is managed via the ``em edit`` command.

Options
~~~~~~~

-a PASSWD, --authdb=PASSWD:
    Path to a file with HTTP basic auth password hashes. Defaults to no
    authentication.
    
-p PORT, --port=PORT:
    The port for the control server to listen on (default 8000). Two other
    services start listening on ports PORT+1 and PORT+2 (default 8001 and 8002).
    These are the launch server and the EMI server respectively.

Discussion
~~~~~~~~~~

Eggmonster runs a server that is responsible for managing the configuration.
The server versions changes to the configuration and understand the format of
the config in order to start/stop/kill the applications defined in the config.
The config format is a YAML file.  In addtion to the control server the
``monster_server`` runs a launch server and an EMI server.

The launch server controls the launch of ``emi`` procs on remote nodes. It
communicates with the remote ``monster_launchd`` processes. If a configured
``emi`` process goes away, the launch server will instruct the remote 
``monster_launchd`` to bring it back.

The EMI server controls the individual running apps. It sends instructions
to TERM/KILL remote ``emi`` processes.

These three servers all work together to provide remote control, configuration
and monitoring of remote applications.

