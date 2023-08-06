Environment variables
=====================

These environment variables affect the behaviour of ``piston_mini_client``:
 * ``PISTON_MINI_CLIENT_DEBUG``: If set, all ``APIError`` exceptions will
   report the full request and response when printed, not only the headers.

 * ``PISTON_MINI_CLIENT_DISABLE_SSL_VALIDATION``: If set,
   ``piston_mini_client`` will ask ``httplib2`` to skip server SSL certificate
   validation.

 * ``PISTON_MINI_CLIENT_LOG_FILENAME``: If set,
   ``piston_mini_client`` will log all requests and responses, including
   headers, to this location.

 * ``PISTON_MINI_CLIENT_DEFAULT_TIMEOUT``: Is used as a socket timeout for
   instances that don't explicitly set a timeout.  Should be in seconds.

 * ``http_proxy`` / ``https_proxy``: ``piston_mini_client`` will check these
   variables to determine if a proxy should be used for each scheme.
   The `SocksiPy <http://socksipy.sourceforge.net/>`_ module is needed for
   proxy support.  A copy is included with ``piston_mini_client``'s code.

.. note::
   Versions of ``httplib2`` before 0.7.0 don't support SSL certificate
   validation.  If you're using an older version of ``httplib2`` setting
   ``PISTON_MINI_CLIENT_DISABLE_SSL_VALIDATION`` will have no effect.

