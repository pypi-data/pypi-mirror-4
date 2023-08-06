.. _protocol:

*****************
Mushroom protocol
*****************

General
=======

The mushroom protocol is based on JSON and negotiates the best
possible transport with the client. Once the transport negotiation is
complete, the protocol becomes transport specific.

Message format
==============

Mushroom uses RPC style messages. All messages are encoded as list
with the message type as the first argument. This message format is
used for both directions. Thus Mushroom RPC also allows to call
methods on the client.

Heartbeat
---------

The heartbeat is used by the client and server to acknowledge messages
and keep the connection alive if there has been no traffic for a given
amount of time. For transports that do not keep the connection open for
an unlimited amount of time this is used for polling.

::

    [0, last_message_id]

Notification
------------

::

    [1, message_id, method_name, data]

The method name is required to be a string and SHOULD be namespaced with
dots as separator.

Request
-------

This message works uses the same message format as the notification but
expects a response.

::

    [2, message_id, method_name, data]

Response
--------

::

    [3, message_id, request_message_id, data]



Error response
--------------

::

    [4, message_id, request_message_id, data]

Disconnect
----------

::

    [-1]


Message id
==========

The message id MUST be implemented as a counter without gaps. It is
used to match request and response messages together and provide
robust messaging even in case of a unexpected connection timeout.


Transport negotiation
=====================

Next generation web applications are probably going to use WebSocket
exclusively for transferring realtime data. Until WebSockets are part
of all browsers in use, a fallback solution is required to reach a
large audience.

Mushroom therefore supports two transports which supports most browsers
in use today, while providing the best possible performance for those
users living at the bleeding edge.

Currently the following two protocols are supported:

    - poll
    - websocket

Other transports like JSONP polling, multipart requests and flash
sockets are not supported by mushroom as they provide little to no
performance benefit over the two supported transports or require a
propietary plugin.

Client request
--------------

The client sends a POST request to BASE_URL with POST data of the
following form::

    {
        "transports": ["poll", "websocket"]
    }

Depending on the needs extra fields can be transferred to perform
authentication. For example a simple request with an user name and
password which only supports long polling as transport could look
like::

    {
        "transports": ["poll"],
        "username": "mobydick",
        "password": "lochness"
    }

For more sophisticated applications it probably makes sense to
handover authentication using some signed credentials::

    {
        "transports": ["poll", "websocket"],
        "username": "bikeshedder",
        "timestamp": 1341852462,
        "digest": "3369bf6cd89ae1387d2a6b7b0063f7b2f76fb65901dc7bdeea4ac9859e68ed82"
    }

.. note::
    Those ways of authenticating users is by no means ment to be a
    defenitive list for authenticating clients. Use whatever authentication
    method fits your application best. If you are working in a trusted
    environment or do not need authentication at all feel free to skip it
    entirely.

.. warning::
    Even though it is possible to use cookies for authentication it is
    highly discouraged. If a browser falls back to long polling, it will
    need to transmit the cookies for every single request. This might be
    fine for very small cookies but still then add bloat that is not
    required at all as mushroom encodes its own session id into the URL.

Server response
---------------

The response from the server will be a JSON of the following format::

    {
        "transport": "poll",
        "url": "https://example.com/poll/c1108b722b2447f3b603b8ff783233ef/"
    }

The response for the websocket transport looks simmilar but contains a
URL with ws or wss protocol::

    {
        "transport": "websocket",
        "url": "wss://example.com/websocket/c1108b722b2447f3b603b8ff783233ef/"
    }

Long polling
============

All requests to the server must contain a JSON array of messages.

Receiving messages (polling)
----------------------------

Once long polling is decided as transport, the browser is expected to
connect to the given URL as soon as possible. If the message array
contains a heartbeat, the connection is detected as polling and will
not return until there are messages available or the timeout is
reached::

    [
        [0, last_message_id]
    ]

.. note::
    You can also send other messages along with the heartbeat message.

The response is of the following format::

    [
        message+
    ]

The last message index is a integer and must be given at the next poll
request to confirm the receipt of the messages received during the last
poll request. This index is used to recover from a timed out poll
request without losing messages.

.. note::
    Please note that this requires a disconnecting client to perform
    one last extra poll request to the server to acknowledge the last
    received messages before stopping to poll.

Sending messages
----------------

The format for sending messages is simple and straightforward::

    [
        message+
    ]

The message id is a simple counter implemented by the client which is
used by the server to filter out duplicate messages. This can be used
to filter out already received messages which were retransmitted due
to a timeout.

The server response is a simple 200 OK without any data.

Long polling example
--------------------

Assuming the connection has been up for a while and the server has now
reached message id 117. The client has sent 5 messages so far and th
next message id is 5 (counting from zero).

    1. Poll request (client to server)::

        [
            [0, 117]
        ]

    2. Send request (client to server)::

        [
            [1, 5, "player.ready", true],
            [2, 6, "get_time"]
        ]

    3. Send response (server to client)::

        (No data, simply a 200 OK)

    4. Poll response (server to client)::

        [
            [3, 118, 6, 1342106240]
        ]

    5. Acknowledge message and continue polling::

        [
            [1, 118]
        ]

    6. ...


WebSocket
=========

WebSockets are bidirectional and have builtin framing. Every message
is transferred as a separate frame.

WebSocket example
-----------------

As in the long polling example the server has reached message
id 117 and the last message sent by the client had id 4.

    1. Heartbeat (client to server)::

        [0, 117]

    2. Heartbeat (server to client)::

        [0, 4]

    3. Notification (client to server)::

        [1, 5, "player.ready", true]

    4. Request (client to server)::

        [2, 6, "get_time"]

    5. Response (server to client)::

        [3, 118, 6, 1342106240]
