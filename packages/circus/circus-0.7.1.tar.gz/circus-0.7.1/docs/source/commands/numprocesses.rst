.. _numprocesses:


Get the number of processes
===========================

Get the number of processes in a watcher or in a arbiter

ZMQ Message
-----------

::

    {
        "command": "numprocesses",
        "propeties": {
            "name": "<watchername>"
        }

    }

The response return the number of processes in the 'numprocesses`
property::

    { "status": "ok", "numprocesses": <n>, "time", "timestamp" }

If the property name isn't specified, the sum of all processes
managed is returned.

Command line
------------

::

    $ circusctl numprocesses [<name>]

Options
+++++++

- <name>: name of the watcher
