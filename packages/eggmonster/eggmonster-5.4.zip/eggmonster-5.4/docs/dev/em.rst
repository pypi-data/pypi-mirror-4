^^
em
^^

Arguments
~~~~~~~~~


Options
~~~~~~~


Discussion
~~~~~~~~~~

Eggmonster provides a command line tool called ``em`` that communicates with
the "control" service of a ``monster_server``. It allows updating the config
and sending signals (TERM, KILL) to the specific processes. The command
utilizes a grep friendly syntax.  For example: ::

  em status | grep foo.service | em term

This would send a TERM signal to any service running with "foo.service" in the
status. For example here are the steps to update the config and push out a new
release. ::

	em edit -n
	# This opens up $EDITOR with the configuration.
	# Make changes, save and close.

	em status
	# This prints the list of services running with their uptime. Services
	# marked with a [*] mean the config changed and the changes have not been
	# applied

	em status | grep foo | grep [*] | em restart --delay=20 --killafter=30

This last command searches for "foo" which is most likely the application name
and then greps for "[*]" which indicates the current config hasn't been
applied. The em restart command is then called signifying that the selected
processes be restarted one after another, sending a kill signal 30 seconds
after term signal was sent if the process was still up. The "--delay" flag says
to make sure the process is up for 20 seconds before moving on to the next one. 



