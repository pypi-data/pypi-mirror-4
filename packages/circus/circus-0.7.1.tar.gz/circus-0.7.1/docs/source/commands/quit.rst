.. _quit:


Quit the arbiter immediately
============================

When the arbiter receive this command, the arbiter exit.

ZMQ Message
-----------

::

    {
        "command": "quit"
    }

The response return the status "ok".


Command line
------------

::

    $ circusctl quit
