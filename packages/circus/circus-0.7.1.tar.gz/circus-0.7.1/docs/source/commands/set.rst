.. _set:


Set a watcher option
====================

ZMQ Message
-----------

::

    {
        "command": "set",
        "properties": {
            "name": "nameofwatcher",
            "options": {
                "key1": "val1",
            }
            ..
        }
    }


The response return the status "ok". See the command Options for
a list of key to set.

Command line
------------

::

    $ circusctl set <name> <key1> <value1> <key2> <value2>
