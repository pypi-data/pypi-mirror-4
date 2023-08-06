.. _rm:


Remove a watcher
================

This command remove a watcher dynamically from the arbiter. The
watchers are gracefully stopped.

ZMQ Message
-----------

::

    {
        "command": "rm",
        "properties": {
            "name": "nameofwatcher",
        }
    }

A message contains 1 property:

- name: name of watcher

The response return a status "ok".

Command line
------------

::

    $ circusctl rm <name>

Options
+++++++

- <name>: name of the watcher to create
