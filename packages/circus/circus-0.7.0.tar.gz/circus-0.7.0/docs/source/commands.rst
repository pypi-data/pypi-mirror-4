
.. _commands:

Commands
########

At the epicenter of circus lives the command systems.  *circusctl* is just a
zeromq client, and if needed you can drive programmaticaly the Circus system by
writing your own zmq client.

All messages are Json mappings.

For each command below, we provide a usage example with circusctl but also the
input / output zmq messages.

circus-ctl commands
-------------------

- **add**: :doc:`commands/add`
- **decr**: :doc:`commands/decr`
- **dstats**: :doc:`commands/dstats`
- **get**: :doc:`commands/get`
- **globaloptions**: :doc:`commands/globaloptions`
- **incr**: :doc:`commands/incr`
- **list**: :doc:`commands/list`
- **listen**: :doc:`commands/listen`
- **listsockets**: :doc:`commands/listsockets`
- **numprocesses**: :doc:`commands/numprocesses`
- **numwatchers**: :doc:`commands/numwatchers`
- **options**: :doc:`commands/options`
- **quit**: :doc:`commands/quit`
- **reload**: :doc:`commands/reload`
- **restart**: :doc:`commands/restart`
- **rm**: :doc:`commands/rm`
- **set**: :doc:`commands/set`
- **signal**: :doc:`commands/signal`
- **start**: :doc:`commands/start`
- **stats**: :doc:`commands/stats`
- **status**: :doc:`commands/status`
- **stop**: :doc:`commands/stop`

.. toctree::
   :hidden:
   :glob:

   commands/*
