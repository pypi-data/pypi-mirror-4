^^^^^^^^^^^
monster_run
^^^^^^^^^^^

Usage: ``monster_run [options] <config_path> <entry_point>``

Arguments
~~~~~~~~~

config_path:
	the path to the configuration file.

	In addition to a file-system path, `config_path` may also take two special
	forms::

	 - "REMOTE" means load the configuration from the eggmonster master
	   (as defined in environment variables).
	 - "ENVIRONMENT" means get the configuration path from the environment
	   variable "EGGMONSTER_CONFIG_PATH". One may override the environment var
	   name with "ENVIRONMENT:<var name>".


entry_point:
	the function to run


Options
~~~~~~~

-u/--update:
	Update dependencies and other egg info using `sudo python setup.py develop`
	before running (setup.py must be in cwd, user must have sudo permission)

-i/--interact:
	action="store_true", dest="interact", default=False,
	help="Open up an interactive prompt with the correct environment.")

-n/--num:
	Use config substitution, swapping $num for given value.

--spawn:
	Used internally when spawning processes.
