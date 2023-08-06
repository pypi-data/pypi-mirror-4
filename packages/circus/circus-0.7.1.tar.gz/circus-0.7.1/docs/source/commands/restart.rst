.. _restart:


Restart the arbiter or a watcher
================================

This command restart all the process in a watcher or all watchers. This
funtion simply stop a watcher then restart it.

ZMQ Message
-----------

::

    {
        "command": "restart",
        "propeties": {
            "name": '<name>"
        }
    }

The response return the status "ok".

If the property name is present, then the reload will be applied
to the watcher.


Command line
------------

::

    $ circusctl restart [<name>] [--terminate]

Options
+++++++

- <name>: name of the watcher
- --terminate; quit the node immediately
