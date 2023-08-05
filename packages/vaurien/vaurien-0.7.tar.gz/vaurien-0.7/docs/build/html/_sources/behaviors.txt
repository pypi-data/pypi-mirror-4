
.. _behaviors:

Behaviors
=========

Vaurien provides a collections of behaviors.

blackout
--------

Reads the packets that have been sent then hangs.

Acts like a *pdb.set_trace()* you'd forgot in your code ;)

delay
-----

Adds a delay before or after the backend is called.

The delay can happen *after* or *before* the backend is called.


Options:

- **before**: If True adds before the backend is called. Otherwise after (bool, default: True)
- **sleep**: Delay in seconds (int, default: 1)


dummy
-----

Transparent behavior. Nothing's done.

error
-----

Reads the packets that have been sent then send random data in
the socket.

The *inject* option can be used to inject data within valid data received
from the backend. The Warmup option can be used to deactivate the random
data injection for a number of calls. This is useful if you need the
communication to settle in some speficic protocols before the ramdom
data is injected.

The *inject* option is deactivated when the *http* option is used.


Options:

- **inject**: Inject errors inside valid data (bool, default: False)
- **warmup**: Number of calls before erroring out (int, default: 0)


hang
----

Reads the packets that have been sent then hangs.

Acts like a *pdb.set_trace()* you'd forgot in your code ;)


