To Do
=====

* *More tests*: Add additional deployment scenarios for applications
* *Handle Single Sign-Out*: 

  At this point, this plugin does not handle Single Sign Out.
  There may be several ways to achieve this:

  - A simple solution may be found by enabling the plugin to execute each
    callable delivered by webapp whose purpose would be to logout the 
    user from it (e.g: by redirecting the browser on the logout url, 
    or deleting some cookies etc.).

  - Currently, CAS 3 and higher handle SSOut by triggering a POST 
    request to all the web application registered. 

* *Genericising the code*:  At the moment, the plugin relies on a CAS 
  server.  However, CAS is simply a specific trusted third party (like
  Kerberos etc.).  So, to avoid redundancy between plugins, abstract away
  "trusted third party" authentication code and refactory.

