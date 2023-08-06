.. _listsockets:


Get the list of sockets
=======================

ZMQ Message
-----------


To get the list of sockets::

    {
        "command": "listsockets",
    }


The response return a list of json mappings with keys for fd, name,
host and port.

Command line
------------

::

    $ circusctl listsockets
