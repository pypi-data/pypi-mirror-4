Tuning your API
===============

Sometimes the defaults ``piston_mini_client`` provides won't be what you need,
or you just need to customize the requests you send out for one part or
another of your API.  In those cases, ``piston_mini_client`` will strive to
stay out of your way.

================
Handling Failure
================

A common issue is what to do if the webservice returns an error.  One possible
solution (and the default for ``piston-mini-client``) is to raise an
exception.

This might not be the best solution for everybody, so piston-mini-client
allows you to customize the way in which such failures are handled.

You can do this by defining a ``FailHandler`` class.  This class needs to
provide a single method (``handle``), that receives the response headers and
body, and decides what to do with it all.  It can raise an exception, or
modify the body in any way.

If it returns a string this will be assumed to be the (possibly
fixed) body of the response and will be deserialized by any decorators the
method has.

To use a different fail handler in your ``PistonAPI`` set the ``fail_handler``
class attribute.  For example, to use the
``NoneFailHandler`` instead of the default ``ExceptionFailHandler``,
you can use::

    class MyAPI(PistonAPI):
        fail_handler = NoneFailHandler
        # ... rest of the client definition...

``piston-mini-client`` provides four fail handlers out of the box:

 * ``ExceptionFailHandler``: The default fail handler, raises ``APIError`` if
   anything goes wrong
 * ``NoneFailHandler``: Returns None if anything goes wrong.  This will
   provide no information about *what* went wrong, so only use it if you don't
   really care.
 * ``DictFailHandler``: If anything goes wrong it returns a dict with all the
   request and response headers and body, requested url and method, for you
   to debug.
 * ``MultiExceptionFailHandler``: Raises a different exception according to
   what went wrong.

===============================
Talking to dual http/https apis
===============================

Often your API provides a set of public calls, and some other calls that
are authenticated.

Public calls sometimes are heavily used, so we'd like to
serve them over http.  They're public anyway.

Authenticated calls involve some sensitive information passing with the user's
credentials, so we like serving those over https.

Once you've got all this set up on the server, you can ask piston_mini_client
to make each call using the appropriate scheme by using the ``scheme``
optional argument when you call ``_get``, ``_post``, ``_put`` or ``_delete``::

    class DualAPI(PistonAPI):
        default_service_root = 'http://myhostname.com/api/1.0'

        def public_method(self):
            return self._get('public_method/', scheme='http')

        def private_method(self):
            return self._post('private_method/', scheme='https')

        def either(self):
            return self._get('either/')

In this case, no matter what scheme the service root uses, calls to
``public_method()`` will result in
an http request, and calls to ``private_method()``  will result in an https
request.  Calls to ``either()`` will leave the scheme alone, so it will
follow the scheme used to instantiate the api, or fall back to
``default_service_root``'s scheme.

===========================
Customizing request headers
===========================

If you need to send custom headers to the server in your requests you can
specify these both in the ``PistonAPI`` instance as an instance or class
variable, or when you make calls to ``_get``, ``_post``, ``_put`` or
``_delete``.
Specifying headers as a class variable will add the same custom headers
to all requests made by all instances of the class::

    class MyAPI(PistonAPI):
        extra_headers = {'X-Requested-With': 'XMLHttpRequest'}
        # ... etc

Here these ``extra_headers`` will be added to any and all requests made by
``MyAPI`` instances.  You could also specify an extra header for a single
instance of ``MyAPI``::

    api = MyAPI()
    api.extra_headers = {'X-Somethingelse': 'dont forget to buy milk'}

In this case you'll get this extra header in all requests made by this
instance of ``MyAPI``.

Finally, you can also pass in an optional ``extra_headers`` argument into
each call to ``_get``, ``_post``, ``_put`` or ``_delete``, if only specific api
calls need to be provided additional headers::

    class MyAPI(PistonAPI):
        def crumble(self):
            return self._get('crumble')
        def icecream(self):
            return self._get('icecream',
                extra_headers={'X-secret-sauce': 'chocolate'})

Here calls to ``icecream`` will use the extra special header, but other calls
(like ``crumble``) won't.


================================================
Customizing the serializer for each content type
================================================

``piston_mini_client`` provides a set of default serializers, but sometimes
you have your own serialization convention, set by the server, and the client
just needs to comply.  In that case, you can implement your own serializer and
add *an instance* of it to the ``serializers`` class attribute.

To define a serializer all you need to provide is a ``serialize`` method,
that should take a single ``obj`` argument and return it serialized into
a string::

    class ReprSerializer(object):
        def serialize(self, obj):
            return repr(obj)

    class MyAPI(PistonAPI):
        serializers = {'application/json': ReprSerializer()}

In this case, any POST/PUT request that goes out with a content type of
``application/json`` will use your ``ReprSerializer`` for serializing its
data into the request body.

If you need to serialize only arguments of a certain specific API call with
this special serializer, you can serialize data before
calling ``_post``/``_put``::

    class GroceryAPI(PistonAPI):
        def order(self, shopping_list):
            serializer = ReprSerializer()
            self._post('somecall', data=serializer.serialize(shopping_list))

Passing a string into the ``data`` argument skips serialization altogether,
so you can apply whichever serialization you want before calling ``_post`` or
``_put``, and ``piston_mini_client`` will avoid double-serializing your
request body.

=================
Logging to a file
=================

If you need to debug the actual requests and responses on the wire, you can
initialize a ``PistonAPI`` passing in a ``log_filename`` argument.
``piston_mini_client`` will append all requests and responses, including
headers, status code and all, to this file.

Also, if you're debugging an application that uses ``piston_mini_client``
but don't want to (or can't) start hacking at the code, you can set
``PISTON_MINI_CLIENT_LOG_FILENAME`` in the environment to point a file,
and all ``PistonAPI`` instances will use this location by default. That is,
unless they're explicitly being instantiated to log elsewhere.

=================
Handling timeouts
=================
When you instantiate a ``PistonAPI`` you can provide an optional ``timeout``
argument that will be used as a socket timeout for the requests that instance
makes.  To explicitly set no timeout, pass in ``timeout=0``.  If you leave
the default ``timeout=None``, the instance will first check for an environment
variable ``PISTON_MINI_CLIENT_DEFAULT_TIMEOUT``, and if that is undefined or
invalid, then the class's default timeout will be used; this can be defined
by setting a ``default_timeout`` class attribute when
writing the API class.  Finally, if the class's default timeout is
also ``None``, Python's system-wide socket default timeout will be used.

You can't currently define timeouts on a per-request basis.  If you need to
change the timeout used for certain requests, you'll need to use a new
``PistonAPI`` instance.
