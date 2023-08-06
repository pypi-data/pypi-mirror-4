.. _stats:


Get process infos
=================

You can get at any time some statistics about your processes
with the stat command.

ZMQ Message
-----------

To get stats for all watchers::

     {
         "command": "stats"
     }


To get stats for a watcher::

     {
         "command": "stats",
         "properties": {
             "name": <name>
         }
     }

To get stats for a process::


     {
         "command": "stats",
         "properties": {
             "name": <name>,
             "process": <processid>
         }
     }

The response retun an object per process with the property "info"
containing some process informations::

     {
       "info": {
         "children": [],
         "cmdline": "python",
         "cpu": 0.1,
         "ctime": "0:00.41",
         "mem": 0.1,
         "mem_info1": "3M",
         "mem_info2": "2G",
         "nice": 0,
         "pid": 47864,
         "username": "root"
       },
       "process": 5,
       "status": "ok",
       "time": 1332265655.897085
     }

Command Line
------------

::

     $ circusctl stats [<watchername>] [<processid>]
