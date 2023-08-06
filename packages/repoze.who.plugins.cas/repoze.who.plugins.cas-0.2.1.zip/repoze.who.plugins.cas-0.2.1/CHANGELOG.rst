Changes
=======

0.2.1 (2013-04-24)
------------------

- Nothing changed yet.


0.2.0 (2013-04-24)
------------------------------

 - Review davidjb changes, cleanify the buildout infra, travis setup [kiorky]
 - Support obtaining user attributes (metadata) via CAS 2.0 service
   validation (``/serviceValidation``) and parsing the XML response.
   User attributes will be placed into the repoze.who identity
   using the key ``attributes_name`` after the ticket validation
   process.  Due to how CAS works, the data must be either saved or cached
   by another plugin to allow persistance beyond the request
   that triggered the ticket validation.  See documentation for more info.
   [davidjb]
 - Support specifying a CAS version. This will control what version of
   the CAS protocol (http://www.jasig.org/cas/protocol) to use.
   [davidjb]
 - Precompile regex statements from configuration to avoid needing
   to recompile during every request.
   [davidjb]
 - Clean up debug process. Debugging is now possible by configuring the
   ``debug`` plugin keyword.
   [davidjb]
 - Clean up identification process to remove need for ``bhp`` in query
   string.
   [davidjb]
 - Switch use of paste HTTPFound for webob, following repoze.who.
   [davidjb]
 - Add Buildout boostrap and configuration for running tests.
   [davidjb]
 - Documentation clean up for clarity.
   [davidjb]
 - Code spring cleaning and documentation expansion. Code now requires
   Python 2.6 and works towards Python 3 compatibility (not guaranteed
   at present).
   [davidjb]

0.1.2 (2012-01-13)
------------------

 - Minor additions to example configuration about CAS URL and auth_tkt
   plugin.
   [davidjb]

0.1 (2009-07-28)
----------------
Initial release.

 - Provides repoze.who plugins (i.e.: challenge, identifier, chalenge decider and
   auth plugins) for enabling CAS
 - Provides simple unit tests


