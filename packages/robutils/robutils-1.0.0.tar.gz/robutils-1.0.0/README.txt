========
robutils
========

robutils is a module providing a handful of convenient classes designed for use in command line python applications.
It is designed for **Python 2.7.3+** on **Linux**. Included are the following features:

* Wrapper for executing external commands over SSH (paramiko) or locally (subprocess) with timeouts.
* Enforce single instances using locking PID files.
* Color text on Bash terminals, demonizing the main process, console redirects (for Altiris), logging, and email.
* Centralizing exit messages for different exit codes. Also useful for Altiris.
* Progress bar with ETA.

The following Python packages are required:

* `psutil <http://code.google.com/p/psutil>`_ >= 0.6.1
* `paramiko <http://pypi.python.org/pypi/paramiko>`_ >= 1.9.0
* `pandas <http://pypi.python.org/pypi/pandas>`_ >= 0.9.1

Installing robutils (one of the following)::

    pip install robutils
    easy_install robutils

Once installed, additional documentation is available within docstrings::

    >>> import robutils; help(robutils)

Quick links
===========

* `Home page <http://code.google.com/p/robutils>`_
* `Download <http://code.google.com/p/robutils/downloads/list>`_

Examples
========

Message
-------

1. Easy to use color syntax for Linux Bash terminals (.term() hides the class instance from the interactive console)::

    >>> from robutils.Message import Message
    >>> message = Message()
    >>> message('Sample text.')
    Sample text.
    <robutils.Message.Message instance at 0x107e4d0>
    >>> message('Colors: [red]red[/red] and [hiblue]multi[hired]colored[bgyellow]text[/all].').term()
    Colors: red and multicoloredtext.
    >>>

2. Print messages to stdout, stderr, and/or log to file (with colors)::

    >>> from robutils.Message import Message
    >>> message = Message(log_file='/tmp/test.log', log_level='error')
    >>> message('Regular stdout non-logged text.').term()
    Regular stdout non-logged text.
    >>> message('stderr non-logged text.', stderr=True).term()
    stderr non-logged text.
    >>> message('stdout and logged as info.').log().term()
    stdout and logged as info.
    >>> message('[red]only logged as error[/all].', quiet=True).log('error').term()
    >>> message('stdout, but not logged since debug < error').log('debug').term()
    stdout, but not logged since debug < error
    >>>

3. Centralize messages for different exit codes. Also supports terminating the script with different exit codes::

    [testuser@localhost ~]$ ~/python27/bin/python
    Python 2.7.3 (default, Nov 24 2012, 23:17:40)
    [GCC 4.4.6 20120305 (Red Hat 4.4.6-4)] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from robutils.Message import Message
    >>> message = Message()
    >>> message.retcodes[1] = 'An error occurred.'
    >>> message.retcodes[5] = 'Error doing x, check file y.'
    >>> message.retcodes[6] = 'Error doing a, check file b.'
    >>> message.quit(5)
    
    
    QUITTING: Error doing x, check file y.
    [testuser@localhost ~]$

4. Send email via SMTP or local sendmail. Supports a tail of the log and/or file attachments::

    >>> from robutils.Message import Message
    >>> message = Message(mail_smtp='smtp-server.austin.rr.com',
    ...     mail_from='test@gmail.com',
    ...     mail_to='robpol86@robpol86.com')
    >>> message.mail('Test Email', body='This is a test email.').term()
    >>>

5. Demonize scripts and/or redirect stdout/stderr to a file (useful for Altiris scripts)::

    #!/home/testuser/python27/bin/python -u
    from robutils.Message import Message
    message = Message(daemon=True, redirect='/tmp/redir.txt')
    message("[hiblue]This is a test[/all]")
    message.retcodes[1] = 'Exiting sample script.'
    message.quit(1)

ExternalCmd
-----------

1. Run external commands on the local machine::

    >>> from robutils.ExternalCmd import ExternalCmd
    >>> cmd = ExternalCmd('echo "test1\ntest2\ntest3\n" | grep test2')
    >>> cmd.run_local()
    >>> cmd.stdout
    'test2\n'
    >>> cmd.code
    0
    >>> cmd = ExternalCmd('echo test1 && echo test2')
    >>> cmd.run_local()
    >>> cmd.stdout
    'test1\ntest2\n'
    >>> cmd = ExternalCmd(['ls', '-lahd', '/tmp'])
    >>> cmd.run_local()
    >>> cmd.stdout
    'drwxrwxrwt 4 root root 32K Nov 20 04:02 /tmp\n'
    >>> 

2. Run external commands on a remote host using SSH::

    >>> from robutils.ExternalCmd import ExternalCmd
    >>> cmd = ExternalCmd('echo first && sleep 10 && echo done')
    >>> cmd.run_remote('localhost')
    >>> (cmd.code, cmd.stdout)
    (None, '')
    >>> time.sleep(10)
    >>> (cmd.code, cmd.stdout)
    (0, 'first\ndone\n')
    >>> 

Progress
--------

1. Create a progress bar and manually display the summary periodically::

    >>> from robutils.Progress import Progress
    >>> from robutils.Message import Message
    >>> message = Message()
    >>> progress = Progress(43)
    >>> while progress.total_percent < 80:
    ...     time.sleep(1)
    ...     progress.inc_pass() if random.randint(1, 5) < 5 else progress.inc_fail()
    >>> message(progress.summary())
      81% (35/43) [########################      ] eta 0:00:06 - 14% ( 5/35) failed
    >>> message(progress.summary(hide_failed=True))
      81% (35/43) [#######################################          ] eta 0:00:03 \
    >>> message(progress.summary(max_width=70))
      81% (35/43) [################    ] eta 0:00:01 | 14% ( 5/35) failed
    >>> message(progress.summary(hide_failed=True, eta_countdown=False))
      81% (35/43) [#################################        ] eta 11:45:30 PM CST /
    >>> while progress.total_percent < 100: progress.inc_pass()
    >>> message(progress.summary())
     100% (43/43) [##############################] eta 0:00:00 - 11% ( 5/43) failed
    >>> 

2. Have the progress bar print periodically in the provided threaded method::

    >>> from robutils.Progress import Progress
    >>> from robutils.Message import Message
    >>> message = Message()
    >>> progress = Progress(43)
    >>> progress.threaded_summary(message, hide_failed=True)
    >>> while progress.total_percent < 100:
    ...     time.sleep(1)
    ...     progress.inc_pass() if random.randint(1, 5) < 5 else progress.inc_fail()
    >>> print
     100% (43/43) [#################################################] eta 0:00:00 /

Instance
--------
::

    >>> from robutils import Instance
    >>> instance = Instance('/var/tmp/example_script.pid')
    >>> if not instance.single_instance_success:
    ...     if instance.old_pid_exists: print 'Another instance is running.'
    ...     if not instance.pdir_exists: print "PID file parent dir doesn't exist."
    ...     if not instance.can_write: print 'No write permissions.'

