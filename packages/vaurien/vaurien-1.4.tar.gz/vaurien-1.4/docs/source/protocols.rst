
.. _protocols:

Protocols
=========

Vaurien provides a collections of protocols.

http
----

HTTP protocol.


Options:

- **buffer**: Buffer size (int, default: 2048)
- **keep_alive**: Keep the connection alive (bool, default: False)
- **reuse_socket**: If True, the socket is reused. (bool, default: False)


memcache
--------

Memcache protocol.


Options:

- **buffer**: Buffer size (int, default: 2048)
- **keep_alive**: Keep the connection alive (bool, default: False)
- **reuse_socket**: If True, the socket is reused. (bool, default: False)


redis
-----

Redis protocol.


Options:

- **buffer**: Buffer size (int, default: 2048)
- **keep_alive**: Keep the connection alive (bool, default: False)
- **reuse_socket**: If True, the socket is reused. (bool, default: False)


tcp
---

TCP handler.


Options:

- **buffer**: Buffer size (int, default: 2048)
- **keep_alive**: Keep the connection alive (bool, default: False)
- **reuse_socket**: If True, the socket is reused. (bool, default: False)



