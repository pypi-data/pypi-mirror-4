.. _list:


Get list of watchers or processes in a watcher
==============================================

ZMQ Message
-----------


To get the list of all the watchers::

    {
        "command": "list",
    }


To get the list of active processes in a watcher::

    {
        "command": "list",
        "properties": {
            "name": "nameofwatcher",
        }
    }


The response return the list asked. the mapping returned can either be
'watchers' or 'pids' depending the request.

Command line
------------

::

    $ circusctl list [<name>]
