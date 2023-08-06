.. _stop:


Stop the arbiter or a watcher
=============================

This command stop all the process in a watcher or all watchers.

ZMQ Message
-----------

::

    {
        "command": "stop",
        "propeties": {
            "name": '<name>",
        }
    }

The response return the status "ok".

If the property name is present, then the reload will be applied
to the watcher.


Command line
------------

::

    $ circusctl stop [<name>]

Options
+++++++

- <name>: name of the watcher
