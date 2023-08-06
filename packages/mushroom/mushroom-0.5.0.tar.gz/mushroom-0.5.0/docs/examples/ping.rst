============
Ping example
============

The browser requests the `ping` method of the server every 2 seconds.
When sending the `ping` request `-> ping` is written to the browser
window and upon receiving the response a `<- pong` is added.

Server - examples/ping-server.py
--------------------------------

.. literalinclude:: ../../examples/ping-server.py


Client - examples/ping.html
---------------------------

.. literalinclude:: ../../examples/ping.html
    :language: html
