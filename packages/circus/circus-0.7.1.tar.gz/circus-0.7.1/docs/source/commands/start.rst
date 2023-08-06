.. _start:


Start the arbiter or a watcher
==============================

This command starts all the processes in a watcher or all watchers.


ZMQ Message
-----------

::

    {
        "command": "start",
        "properties": {
            "name": '<name>",
        }
    }

The response return the status "ok".

If the property name is present, the watcher will be started.

Command line
------------

::

    $ circusctl start [<name>]

Options
+++++++

- <name>: name of the watcher
