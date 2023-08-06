Reference
=========

=========
Resources
=========
.. autoclass:: piston_mini_client.PistonAPI
  :members: __init__, _get, _post, _put, _delete

.. autoclass:: piston_mini_client.PistonResponseObject

.. autoclass:: piston_mini_client.PistonSerializable
  :members: as_serializable

===========================
Deserializing response data
===========================

These decorators can be applied to your ``PistonAPI`` methods to control how
the retrieved data is handled.

.. autofunction:: piston_mini_client.returns_json

.. autofunction:: piston_mini_client.returns

.. autofunction:: piston_mini_client.returns_list_of

==========
Validators
==========

.. automodule:: piston_mini_client.validators
  :members: validate_pattern, validate, validate_integer, oauth_protected, basic_protected

=============
Fail handlers
=============

.. automodule:: piston_mini_client.failhandlers
  :members:
    
===========
Serializers
===========

.. automodule:: piston_mini_client.serializers
   :members:

.. _authentication:

==============
Authentication
==============

.. automodule:: piston_mini_client.auth
   :members:
