=====================================
Remote procedure calls - mushroom.rpc
=====================================

.. contents::
    :local:

.. currentmodule:: mushroom.rpc

Engine
------

.. autoclass:: Engine
    :members:
    :undoc-members:

RPC handlers
------------

.. autoclass:: MethodDispatcher
    :members:
    :undoc-members:

    .. automethod:: __call__

.. autofunction:: dummy_rpc_handler

Exceptions
----------

.. autoexception:: RpcError
    :members:
    :undoc-members:

.. autoexception:: MethodNotFound
    :members:
    :undoc-members:

.. autoexception:: RequestException
    :members:
    :undoc-members:

.. autoexception:: RequestTimeout
    :members:
    :undoc-members:


Message classes
---------------

.. autoclass:: Message
    :members:
    :undoc-members:

.. autoclass:: Heartbeat
    :members:
    :undoc-members:

.. autoclass:: Notification
    :members:
    :undoc-members:

.. autoclass:: Request
    :members:
    :undoc-members:

.. autoclass:: Response
    :members:
    :undoc-members:

.. autoclass:: Error
    :members:
    :undoc-members:

.. autoclass:: Disconnect
    :members:
    :undoc-members:
