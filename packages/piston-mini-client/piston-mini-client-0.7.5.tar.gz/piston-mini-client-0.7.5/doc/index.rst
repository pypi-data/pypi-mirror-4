.. piston_mini_client documentation master file, created by
   sphinx-quickstart on Mon Nov 15 01:44:53 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to piston_mini_client's documentation!
==============================================

Contents:

.. toctree::
   :maxdepth: 2

   quickstart
   tuning
   reference
   envvars

Overview
========

Piston_mini_client is a package that allows you to easily describe an
API provided by a Django server using django-piston that takes care of:

* Serializing call arguments and deserializing responses from the api.  It
  will deserialize json provided by Piston into light-weight objects.
* Making the http calls for you.  You should be able to call a method on an
  api object instead of having to fetch a particular URL.
* Provide a in-code description of your API.  Developers should be able to
  know your API by looking at the client code you provide.

Piston_mini_client is written with the following principles in mind:

* It should have a small set of dependencies.  We depend on httplib2 mainly
  because it provides caching, but you should not need to install a pile of
  packages just to use a rest client.  Other dependencies like ``oauthlib``
  and ``socks`` are only imported if you need to use oauth authentication or
  support proxies, respectively.

* Errors should be informative.  Backtraces should point you in the right
  direction to solve your problem.

* The client library shouldn't restrict the way you layout your API.
  Piston_mini_client should be able to work with just about any rest api your
  server implements.

* There should be good documentation available.  Clear code is great, and it
  should be really easy to get started with a couple of simple examples, but
  there should be documentation available explaining, amongst other things,
  these principles. :)

