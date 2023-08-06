Getting Started
===============

All you really need to do is inherit from PistonAPI and define the methods
your api provides.  Each method can specify what arguments it takes, what
authentication method should be used, and how to process the response.

=================
One simple method
=================

Say your server's urls.py defines a single pattern for the web API like::

    urlpatterns = patterns('',
        url(r'^myapicall$', myapicall_resource),
    )


Then all you'll need to define your client code is something like::

    from piston_mini_client import PistonAPI, returns_json

    class MyAPI(PistonAPI):
        default_service_root = 'http://myhostname.com/api/1.0'

        @returns_json
        def myapicall(self):
            return self._get('myapicall')

And that's it.  Some things worth noticing here:
 * Your api client class should provide a default service root, that will be
   used if instantiated with no service root.  When instantiating ``MyAPI``
   your users will be able to override this.
 * The default service root should usually include any path needed to reach
   your API urls.py.  For example, in this case you can imagine the project's
   ``urls.py`` has a line like::

    urlpatterns = patterns('',
        (r'^api/1.0/', include('myproject.api.urls')),
    )

 * ``@returns_json`` tells ``piston_mini_client`` that the data returned by
   the server will be encoded with json, and so it will be decoded accordingly
   into Python data structures.

 * PistonAPI provides ``_get``, ``_post``, ``_put`` and ``_delete`` methods to
   take care of making the lower level http calls via ``httplib2``.


======================================
Validating arguments to your API calls
======================================

If your server's ``urls.py`` specifies placeholders for resource arguments, as
in::

    urlpatterns = patterns('',
        url(r'^foo/(?P<language>[^/]+)/(?P<foobar_id>\d+)/frobble$',
            myapicall_resource),
    )

You can validate arguments on the client side to avoid unnecessary server
roundtrips with::

    from piston_mini_client import PistonAPI
    from piston_mini_client.validators import validate_pattern

    class MyAPI(PistonAPI):
        default_service_root = 'http://myhostname.com/api/1.0'

        @validate_pattern('foobar_id', r'\d+')
        @validate_pattern('language', r'[^/]+', required=False)
        def myapicall(self, foobar_id, language=None):
            if language is None:
                language = 'en'
            return self._get('foo/%s/%s/frobble' % (language, foobar_id))

The ``validate_pattern`` decorator checks that the necessary keyword argument
is provided and that it matches the pattern that the server is then going to
match against.

If you specify ``required=False`` the argument can be omitted, in which case
the client code should take care of providing a sane default value.

You could also have used the ``validate`` validator in this case that just
checks that a keyword argument is of a certain type::

    from piston_mini_client import PistonAPI
    from piston_mini_client.validators import validate, validate_pattern

    class MyAPI(PistonAPI):
        default_service_root = 'http://myhostname.com/api/1.0'

        @validate('foobar_id', int)
        @validate_pattern('language', r'[^/]+', required=False)
        def myapicall(self, foobar_id, language=None):
            if language is None:
                language = 'en'
            return self._get('foo/%s/%s/frobble' % (language, foobar_id))

Then again, if we use this we'd need to then ensure that ``foobar_id >= 0``.

==============================================
Getting back light-weight objects from the API
==============================================

If your api handlers return JSON, your api handlers can easily specify that
the response should be parsed into small objects that resemble your
server-side models.

For example if your ``handlers.py`` on the server contains::

    class FooBarHandler(BaseHandler):
        model = FooBar
        fields = (
            'name',
            'length',
        )
        allowed_methods = ('GET',)

        def read(self, request, foobar_id):
            try:
                return FooBar.objects.get(pk=foobar_id)
            except FooBar.DoesNotExist:
                return rc.NOT_FOUND

Then, assuming the right url matches this handler in your ``urls.py``, your
Piston client code could use something like::

    from piston_mini_client import PistonResponse, returns

    class FooBarResponse(PistonResponse):
        def __str__(self):
            return '<FooBar: %s>' % self.name

    
    class MyAPI(PistonAPI):
        default_service_root = 'http://myhostname.com/api/1.0'

        @validate('foobar_id', int)
        @returns(FooBarResponse)
        def get_foobar(self, foobar_id):
            return self._get('foobar/%s/' % foobar_id)

...and calls to ``api.get_foobar()`` will return a ``FooBarResponse``, that
will have the right ``name`` and ``length`` attributes.

Note that we could have just skipped the definition of ``FooBarResponse``
and specified ``@returns(PistonResponse)`` but it might be nice to be able to
print one of these responses and get a meaningful output, or we might want
to attach some other method to ``FooBarResponse``.

===========================================
Passing light-weight objects into API calls
===========================================
Same as receiving light-weight objects as responses, ``piston_mini_client``
defines a way to pass in light-weight objects to your API calls, and
have them serialized accordingly.

When calling ``_post`` or ``_put`` you need to pass in a ``data`` argument,
that will be serialized into the body of the request.  This can tipically be
a string (in which case no serialization is performed) or a simple Python data
structure (list, dict, tuple, etc...), but
you can also pass in any object with a ``as_serializable`` method.

``PistonSerializable`` is one such class, that allows you to easily define
a set of attributes that will be serialized into a request's body::

    class AccountRequest(PistonSerializable):
        _atts = ('username', 'password', 'fullname')

    class RegistrationAPI(PistonAPI):
        @validate('account', AccountRequest)
        def register(self, account):
            self._post('register', data=account)

After defining this light-weight ``AccountRequest`` class you can set it up
when you instantiate it or by assigning attributes::

    account = AccountRequest(username='joeb', password='easy123')
    account.fullname = 'Joe Blogs'

    api.register(account)

``PistonSerializable`` will take care of checking that all the needed
attributes have been set when it's serialized, and complain otherwise.  All
attributes will be packed into a dictionary for serializing.  If you have
special serialization needs you can redefine the ``as_serializable`` method,
or use your own light-weight object entirely.  All you need to provide is an
``as_serializable`` method to ensure it works with ``piston_mini_client``'s
serialization mechanism.

