Installing
==========

Requirement
++++++++++++

You must have a CAS server working and you will need to know the URL to your
CAS server.  Typically, this will be the part of the URL before your
``/login`` or ``/logout`` URLs for CAS.  For example::

    https://example.edu/cas/

All URLs for CAS login, validation, and logout will be built using this
address.

CAS
+++

You must ensure that logout is enabled on your CAS server.
Typically, this involves adding::

    <property name="followServiceRedirects" value="true" />

into the ``LogoutController`` bean in your ``cas-servlet.xml`` file.
Ask your system administrator if you're unsure about the above.

Attribute release
+++++++++++++++++

If your CAS server supports it, this plugin can parse and capture 
user metadata attributes being released during the CAS ticket validation
process. By specifying an identifer for ``attributes_name`` in the plugin
configuration, attributes released from CAS will be stored into the
``repoze.who`` identity within the given environment.  Given the way
CAS works, you will need to cache or store this information within your
application (or use another ``repoze.who`` plugin to do it for you), as 
this data is only associated with a user's initial CAS request.

A suite of plugins exists for precisely this reason and can be found at
https://pypi.python.org/pypi/repoze.who.plugins.metadata_cache

You can always customise your own method of managing this metadata, too.
As mentioned, you can find the retrieved attributes within the ``repoze.who``
identity within the specific request that triggers the CAS authentication.

Your apps
+++++++++

Nothing is required within your apps, just set them up and configure 
``repoze.who`` accordingly.  You may like to follow the example 
configuration file as seen in the ``config_example/`` directory.
This is what the ``who.ini`` configuration file looks like::

    # IDENTIFIER
    # @param :
    # - cas_url : URL to your CAS server. Ensure your URL has a trailing slash.
    # - cas_version : Version of your CAS server. Affects how the CAS protocol
    #                 is followed.
    # - rememberer_name : name of the plugin for remembering (delegate)
    # - attributes_name : identifier for where to place CAS-sources metadata
    #                     inside the ``repoze.who`` identity.
    # - path_toskip : regex for URLs handling authentication to CAS separately
    # - path_logout : regex for URLS that should be trigger a logout
    #                 WARNING: you must include the path of logout even 
    #                 it is present within ``path_toskip``.
    [plugin:casauth]
    use = repoze.who.plugins.cas.main_plugin:make_plugin
    cas_url= https://servcas:8443/cas/
    cas_version = 3.0
    rememberer_name = auth_tkt
    attributes_name = attributes
    path_toskip = .*/phpbb/.*
    path_logout = .*/logout.*
                  .*mode=logout.*

    
    # CHALLENGE DECIDER
    # @param:
    # - path_login : those regexp indicate which url should be redirected for a challenge 
    #                e.g. : for CAS, will be redirected on a "/cas/login" like url
    [plugin:decider]
    use = repoze.who.plugins.cas.challenge_decider:make_plugin
    path_login = 
                .*trac/login.*
                .*/login$ 

    
    [plugin:auth_tkt]
    # identification
    use = repoze.who.plugins.auth_tkt:make_plugin
    secret = secret
    cookie_name = oatmeal
    secure = False
    include_ip = False
    
    [general]
    request_classifier = repoze.who.classifiers:default_request_classifier
    remote_user_key = REMOTE_USER
    # trick : target the plugin whose name is the same
    challenge_decider = decider
    
    
    [identifiers]
    # plugin_name;classifier_name:.. or just plugin_name (good for any)
    plugins =
          casauth
          auth_tkt
    
    [authenticators]
    # plugin_name;classifier_name.. or just plugin_name (good for any)
    plugins =
          casauth
    
    
    [challengers]
    # plugin_name;classifier_name:.. or just plugin_name (good for any)
    plugins =
          casauth
    
Using the above configuration will see the given application receive the
remote user's name as the ``REMOTE_USER`` environment variable
