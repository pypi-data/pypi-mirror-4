^^^^^^^^^^^^^^^^^
monster_eggserver
^^^^^^^^^^^^^^^^^

Usage: ``monster_eggserver [options] <repo_root>``

Arguments
~~~~~~~~~

repo_root:
	foo

Options
~~~~~~~

-a/--auth:
	the path to a file to use in implementing HTTP Basic Authentication. If not
	provided, no authentication is performed. If provided, it should be a
	newline-separated list of username:password combinations.

-p/--port:
	the port to listen on. The default is 8010.


Discussion
~~~~~~~~~~

This daemon implements the HTTP interface required of a package repository by
Python's package management tools, such as ``distutils``,
``setuptools``/``easy_install``, and ``pip``.  It serves a package listing at /
and individual packages at /[package_filename]. It responds to POST requests to
/[package_filename] by storing the POST body at the location specified. It
returns 500 Internal Server Error if there is already a package at that
location.




