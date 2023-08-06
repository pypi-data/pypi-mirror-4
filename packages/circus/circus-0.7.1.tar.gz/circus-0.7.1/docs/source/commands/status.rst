.. _status:


Get the status of a watcher or all watchers
===========================================

This command start get the status of a watcher or all watchers.

ZMQ Message
-----------

::

    {
        "command": "status",
        "properties": {
            "name": '<name>",
        }
    }

The response return the status "active" or "stopped" or the
status / watchers.


Command line
------------

::

    $ circusctl status [<name>]

Options
+++++++

- <name>: name of the watcher

Example
+++++++

::

    $ circusctl status dummy
    active
    $ circusctl status
    dummy: active
    dummy2: active
    refuge: active
