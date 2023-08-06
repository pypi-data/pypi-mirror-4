
.. _handlers:

Handlers
========

Vaurien provides a collections of handlers.

blackout
--------

Just closes the client socket on every call.

delay
-----

Adds a delay before the backend is called.

The delay can happen *after* or *before* the backend is called.


Options:

- **before**: If True adds before the backend is called. Otherwise after (bool, default: True)
- **buffer**: Buffer size (int, default: 2048)
- **keep_alive**: Keep-alive protocol (auto-detected with http) (bool, default: False)
- **protocol**: Protocol used (str, default: 'tcp', possible values: 'tcp', 'redis', 'memache', 'http')
- **reuse_socket**: If True, the socket is reused. (bool, default: False)
- **sleep**: Delay in seconds (int, default: 1)


dummy
-----

Dummy handler.

Every incoming data is passed to the backend with no alteration,
and vice-versa.


Options:

- **buffer**: Buffer size (int, default: 2048)
- **keep_alive**: Keep-alive protocol (auto-detected with http) (bool, default: False)
- **protocol**: Protocol used (str, default: 'tcp', possible values: 'tcp', 'redis', 'memache', 'http')
- **reuse_socket**: If True, the socket is reused. (bool, default: False)


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

- **buffer**: Buffer size (int, default: 2048)
- **inject**: Inject errors inside valid data (bool, default: False)
- **keep_alive**: Keep-alive protocol (auto-detected with http) (bool, default: False)
- **protocol**: Protocol used (str, default: 'tcp', possible values: 'tcp', 'redis', 'memache', 'http')
- **reuse_socket**: If True, the socket is reused. (bool, default: False)
- **warmup**: Number of calls before erroring out (int, default: 0)


hang
----

Reads the packets that have been sent then hangs.

Acts like a *pdb.set_trace()* you'd forgot in your code ;)


