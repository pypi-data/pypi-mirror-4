.. _add:


Add a watcher
=============

This command add a watcher dynamically to a arbiter.

ZMQ Message
-----------

::

    {
        "command": "add",
        "properties": {
            "cmd": "/path/to/commandline --option"
            "name": "nameofwatcher"
            "args": [],
            "options": {},
            "start": false
        }
    }

A message contains 2 properties:

- cmd: Full command line to execute in a process
- args: array, arguments passed to the command (optional)
- name: name of watcher
- options: options of a watcher
- start: start the watcher after the creation

The response return a status "ok".

Command line
------------

::

    $ circusctl add [--start] <name> <cmd>

Options
+++++++

- <name>: name of the watcher to create
- <cmd>: full command line to execute in a process
- --start: start the watcher immediately
