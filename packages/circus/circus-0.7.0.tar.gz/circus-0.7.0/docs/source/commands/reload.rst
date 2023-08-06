.. _reload:


Reload the arbiter or a watcher
===============================

This command reload all the process in a watcher or all watchers. If a
the option send_hup is set to true in a watcher then the HUP signal
will be sent to the process.A graceful reload follow the following
process:


1. Send a SIGQUIT signal to a process
2. Wait until graceful timeout
3. Send a SIGKILL signal to the process to make sure it is finally
   killed.

ZMQ Message
-----------

::

    {
        "command": "reload",
        "propeties": {
            "name": '<name>",
            "graceful": true
        }
    }

The response return the status "ok". If the property graceful is
set to true the processes will be exited gracefully.

If the property name is present, then the reload will be applied
to the watcher.


Command line
------------

::

    $ circusctl reload [<name>] [--terminate]

Options
+++++++

- <name>: name of the watcher
- --terminate; quit the node immediately
