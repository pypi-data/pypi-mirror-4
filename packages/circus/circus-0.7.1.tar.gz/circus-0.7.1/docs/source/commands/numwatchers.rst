.. _numwatchers:


Get the number of watchers
==========================

Get the number of watchers in a arbiter

ZMQ Message
-----------

::

    {
        "command": "numwatchers",
    }

The response return the number of watchers in the 'numwatchers`
property::

    { "status": "ok", "numwatchers": <n>, "time", "timestamp" }


Command line
------------

::

    $ circusctl numwatchers
