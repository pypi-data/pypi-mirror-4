Introduction
============

``repoze.who.plugins.metadata_cache`` is a set of plugins for the 
`repoze.who framework
<http://docs.repoze.org/who/>`_ that enables the caching and replaying
of "one-off" user metadata, specifically targetting SSO requests.

Quick start and Example Applications
------------------------------------

Usage with CAS attribute release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use a metadata cache plugin with `repoze.who.plugins.cas
<https://pypi.python.org/pypi/repoze.who.plugins.cas>`_ to capture the metadata
returned from ticket validation.  

To do this, configure a metadata cache plugin with the
same ``name`` as the ``attributes_name`` for the CAS plugin, and ensure you're
using at least CAS version 2 (so set ``cas_version = 2.0`` or higher for the
CAS plugin).  During ticket validation for CAS, the attributes will be
retrieved and placed into the ``repoze.who`` identity for the metadata cache
plugin to pick up and hold onto.

An example configuration would look like the following.  The one main thing
to make sure of is that the configuration for the attributes for the CAS
plugin matches up with the ``name`` configured for the ``metadata_cache``
plugin.  This very basic configuration stores user attributes in memory (a
Python dictionary, specifically).

.. code:: ini

    [plugin:casauth]
    use = repoze.who.plugins.cas.main_plugin:make_plugin
    cas_url = https://cas.example.com/cas/
    cas_version = 3.0
    attributes_name = attributes
    rememberer_name = auth_tkt

    [plugin:metadata_cache]
    use = repoze.who.plugins.metadata_cache.memory:make_plugin
    name = attributes

    ...

    [identifiers]
    plugins =
        casauth
        auth_tkt
                      
    [authenticators]
    plugins =
        casauth
        auth_tkt

    [challengers]
    plugins =
        casauth

    [mdproviders]
    plugins = 
        metadata_cache


Web server authentication
~~~~~~~~~~~~~~~~~~~~~~~~~

You can use a metadata cache plugin with a front-end web server authentication
module (for example, Shibboleth) to extract user metadata out of the
environment or headers and reduce your dependency on the authentication/web
server layers above.

An implementation and example for this will be coming soon.

...and more
~~~~~~~~~~~

You can also extend the classes available here for anything else where user
details come into the application via the environment or request (headers,
cookies, etc).

If you build something you think is going to useful to the world at large,
send a pull request to see if it can be included.


Caution
-------

Be wary of anything upstream - servers, proxies, and especially the client -
being able to spoof or inject things into the request or environment that might 
inadvertently affect the given metadata being used.  A careless configuration
could compromise security.

Development
-----------

To clone this project, and run the test suite, run the following::

    git clone git://github.com/davidjb/repoze.who.plugins.metadata_cache.git
    cd repoze.who.plugins.metadata_cache
    python bootstrap.py
    ./bin/buildout
    ./bin/test

Send a pull request with things to fix, new features or whatever you think
could be useful.  Try to document what you're doing and keep the code clean.
No reasonable pull request refused™.

Credits
-------

* David Beitey (davidjb), Author


Documentation
=============

.. contents::


