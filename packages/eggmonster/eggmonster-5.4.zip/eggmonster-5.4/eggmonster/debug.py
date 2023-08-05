#!/usr/bin/python

def enable_rpdb2_support():
    '''This is a method to basically setup CherryPy with rpdb2 to allow easier debugging.'''
    try:
        install_cherrypy_hooks()
    except ImportError:
        pass

    try:
        install_rpdb2_hooks()
    except ImportError:
        raise RuntimeError, 'rpdb2 support not available!'

def install_cherrypy_hooks():
    '''We need to replace the way CherryPy respawns itself - we want rpdb2
       to be monitoring the respawned process.'''
    import cherrypy

    # You can add as many versions as you want here - all that I would suggest
    # you check that the below code hasn't changed so much that the hack is no
    # longer applicable - we're just limiting the number of supported versions
    # to safeguard against silent failures.
    if cherrypy.__version__ not in ('3.0.1', '3.0.3'):
        raise RuntimeError, 'support not enabled for CherryPy %s' % cherrypy.__version__

    # Required imports for modified reexec.
    import os
    import time

    # New reexec method (from _cpengine.py).
    def reexec():
        """Re-execute the current process."""
        cherrypy.server.stop()
        self.stop()

        # XXX: This line has been changed - we want to keep the original
        # rpdb2 arguments.
        args = original_argv[:]
        cherrypy.log("Re-spawning %s" % " ".join(args), "ENGINE")
        args.insert(0, sys.executable)

        if sys.platform == "win32":
            args = ['"%s"' % arg for arg in args]

        # Some platforms (OS X) will error if all threads are not
        # ABSOLUTELY terminated. See http://www.cherrypy.org/ticket/581.
        for trial in xrange(self.reexec_retry * 10):
            try:
                os.execv(sys.executable, args)
                return
            except OSError, x:
                if x.errno != 45:
                    raise
                time.sleep(0.1)
        else:
            raise

    # Bind new method.
    self = cherrypy.engine
    self.reexec = reexec

    # Store sys.argv here - we keep the unmodified version here (safely)
    # so that it can be used when respawning.
    import sys
    original_argv = sys.argv[:]
    return

def install_rpdb2_hooks():

    # If this isn't going to work, then make it fail early.
    import rpdb2

    #
    #
    # os.execv hacking - we override this to try and cleanly terminate the
    # remote debugger. Calling os.execv normally while the debugger is still
    # connected will prevent the current process from terminating normally.
    #
    #

    # This CherryPyDebug helper script will terminate any listening debuggers,
    # allowing termination to correctly.
    def execv_modified(*args):

        # The code in here is based on rpdb2._atexit.
        from rpdb2 import g_debugger, g_server
        g_debugger.stoptrace()
        g_debugger.send_event_exit()

        import time
        time.sleep(1.0)

        g_server.shutdown()
        g_debugger.shutdown()

        return old_execv(*args)

    import os
    old_execv = os.execv
    os.execv = execv_modified

    #
    #
    # rpdb2 server hacking - rpdb2 doesn't permit us to pass in a password at
    # the command line, so we have to make use of a "secret" file. However,
    # use of this then seems to actually prevent us from viewing the source
    # (it certainly seems to be the case where I am trying to debug a server
    # from one machine on another).
    #
    # Because this secret file gets used for more than just the password, we
    # have to basically emulate giving the password at the command line (we
    # don't really want to be forced to give the password through stdin).
    #
    # To do this, what we do is override the one place which uses the secret
    # file path - we mangle the incoming arguments to omit it altogether.
    #

    # Strip off the last argument.
    original_startserver = rpdb2.StartServer
    rpdb2.StartServer = lambda *args: original_startserver(*args[:-1] + (None,))

    #
    #
    # For some reason, between the modified os.execv call from rpdb2 and our
    # modified call, we get some other threads reporting socket errors. I'll
    # just swallow those up.
    #
    #
    orig_handle_error = rpdb2.CXMLRPCServer.handle_error
    def our_handle_error(self, request, client_address):
        import socket
        import sys
        the_error = sys.exc_info()[1]
        if isinstance(the_error, socket.error) and the_error.args[0] == 32:
            return # 'Broken pipe'
        return orig_handle_error(self, request, client_address)
    rpdb2.CXMLRPCServer.handle_error = our_handle_error

    #
    #
    # Determining why our password is sometimes invalid is awkward - so we
    # replace the function to give some pointers.
    #
    #
    orig_is_valid_pwd = rpdb2.is_valid_pwd
    def our_is_valid_pwd(pwd):
        if orig_is_valid_pwd(pwd):
            return True
        print '****************************************'
        print 'Invalid password given: %r' % pwd
        print 'Allowed characters are [A-Za-z0-9_]'
        print 'Bracket characters aren\'t allowed - whitespace is definitely forbidden.'
        print '****************************************'
        return False
    rpdb2.is_valid_pwd = our_is_valid_pwd

def monster_run():

    # We'll insert the starting filename into sys.argv - so rpdb2 will just
    # begin execution of that (rpdb2 likes to think that it is the one who was
    # invoked, and it will begin execution of the application that needs
    # debugging).
    #
    # We don't support a mixture of option flags for rpdb2 and monster_run - so
    # figuring out where rpdb2 options end and monster_run arguments begin is
    # really awkward. So we take advantage of the fact that we know monster_run
    # requires two arguments and go with that.
    #
    # It's precisely this reason why I'm hardcoding this function to invoke
    # monster_run, rather than any arbitary script.

    import sys
    if len(sys.argv) == 2 and sys.argv[1] == '--help':
        print 'Suggested way of running monster_run in debug mode is:'
        print '  monster_debug --remote --debuggee --rid=FILEPATH cfgfile.yaml app.name'
        print
        print 'This will run the application and have rpdb2 set up to allow remote connections'
        print 'and to take the session password from the contents of FILEPATH.'
        print
        print '*** Below is the help documentation for rpdb2 module. ***'
        print
    elif len(sys.argv) < 3:
        sys.exit('Error: config file and application name required.')
    else:
        for monster_arg in sys.argv[-2:]:
            if monster_arg[:1] == '-':
                sys.exit('Error: last two arguments cannot be options.')

        # How much argument mangling can you do before your head hurts?
        import os.path
        sys.argv.insert(-2, os.path.join(os.path.dirname(sys.argv[0]), 'monster_run'))

        print '*** About to startup application with rpdb2. ***'
        print '*** You may need to connect with winpdb / rpdb2 to allow execution to start. ***'
        print

    import rpdb2
    sys.exit(rpdb2.main())
