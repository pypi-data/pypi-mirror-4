.. _signal:


Send a signal
=============

This command allows you to send a signal to all processes in a watcher,
a specific process in a watcher or its children.

ZMQ Message
-----------

To send a signal to all the processes for a watcher::

    {
        "command": "signal",
        "property": {
            "name": <name>,
            "signum": <signum>
    }

To send a signal to a process::

    {
        "command": "signal",
        "property": {
            "name": <name>,
            "pid": <processid>,
            "signum": <signum>
    }

An optional property "children" can be used to send the signal
to all the children rather than the process itself::

    {
        "command": "signal",
        "property": {
            "name": <name>,
            "pid": <processid>,
            "signum": <signum>,
            "children": True
    }

To send a signal to a process child::

    {
        "command": "signal",
        "property": {
            "name": <name>,
            "pid": <processid>,
            "signum": <signum>,
            "child_pid": <childpid>,
    }

It is also possible to send a signal to all the processes of the
watcher and its childs::

    {
        "command": "signal",
        "property": {
            "name": <name>,
            "signum": <signum>,
            "children": True
    }

Last, you can send a signal to the process *and* its children, with
the *recursive* option::

    {
        "command": "signal",
        "property": {
            "name": <name>,
            "signum": <signum>,
            "recursive": True
    }



Command line
------------

::

    $ circusctl signal <name> [<process>] [<pid>] [--children]
            [recursive] <signum>

Options:
++++++++

- <name>: the name of the watcher
- <pid>: integer, the process id.
- <signum>: the signal number to send.
- <childpid>: the pid of a child, if any
- <children>: boolean, send the signal to all the children
- <recursive>: boolean, send the signal to the process and its children

Allowed signals are:

    - 3:    QUIT
    - 15:   TERM
    - 9:    KILL
    - 1:    HUP
    - 21:   TTIN
    - 22:   TTOU
    - 30:   USR1
    - 31:   USR2
