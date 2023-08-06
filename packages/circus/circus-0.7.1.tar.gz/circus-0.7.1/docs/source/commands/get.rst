.. _get:


Get the value of a watcher option
=================================

This command return the watchers options values asked.

ZMQ Message
-----------

::

    {
        "command": "get",
        "properties": {
            "keys": ["key1, "key2"]
            "name": "nameofwatcher"
        }
    }

A response contains 2 properties:

- keys: list, The option keys for which you want to get the values
- name: name of watcher

The response return an object with a property "options"
containing the list of key/value returned by circus.

eg::

    {
        "status": "ok",
        "options": {
            "flapping_window": 1,
            "times": 2
        },
        time': 1332202594.754644
    }

See Optios for for a description of options enabled?


Command line
------------

::

    $ circusctl get <name> <key> <value> <key1> <value1>
