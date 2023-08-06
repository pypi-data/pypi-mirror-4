Introduction
============

.. contents::

``repoze.who.plugins.cas`` is a plugin for the `repoze.who framework
<http://docs.repoze.org/who/>`_ that enables Single Sign-On (SSO)
for applications via a Central Authentication Service (CAS) server.

.. image:: https://secure.travis-ci.org/kiorky/repoze.who.plugins.cas.png
    :target: http://travis-ci.org/kiorky/repoze.who.plugins.cas


The plugin follows the protocols described
in the `official documentation <http://www.jasig.org/cas/protocol>`_ for
login, ticket validation, and logout. The plugin has been tested against
instances of CAS 3.0+ servers.

Compatibility Note
------------------

Whilst the plugin supports both CAS 1.0- and CAS 2.0-style service ticket
validation, the plugin has currently only been tested against instances of
CAS 3.0+ servers.  Backwards compatibility is unknown at the point and
assistance testing this plugin is welcomed.

Potential Applications
----------------------

Applications which can be used :

- Apps complying with the `simple_authentication WSGI specification
  <http://wsgi.org/wsgi/Specifications/simple_authentication>`_, which take
  advantage of the REMOTE_USER key in the WSGI environment.
- Custom applications that utilise the ``repoze.who`` environment
  variables present within a WSGI request.
- Apps which can handle themselves the CAS mechanism (for example: phpBB
  with the CAS patch, using ``wphp`` as a Paste filter for integration of
  PHP with Python),

Links
----+

- `Official link for CAS <http://www.jasig.org/cas>`_

Development
-----------

To run the test suite, clone this project from source code hosting and
run the following::

    cd repoze.who.plugins.cas
    python bootstrap.py
    ./bin/buildout
    ./bin/test

Credits
-------

|makinacom|_

* `Planet Makina Corpus <http://www.makina-corpus.org>`_
* `Contact us <mailto:python@makina-corpus.org>`_

.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com


Documentation
=============



