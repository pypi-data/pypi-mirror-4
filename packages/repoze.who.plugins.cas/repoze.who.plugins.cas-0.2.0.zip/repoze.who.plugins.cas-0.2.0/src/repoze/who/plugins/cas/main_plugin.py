
import logging
import urllib
import re
from xml.etree import ElementTree

from repoze.who.interfaces import (IChallenger,
                                   IIdentifier,
                                   IAuthenticator)
from webob.exc import HTTPFound
from zope.interface import implements

from paste.request import parse_dict_querystring
from paste.request import construct_url


CAS_NAMESPACE = 'http://www.yale.edu/tp/cas'
CAS_NAMESPACE_PREFIX = '{{{}}}'.format(CAS_NAMESPACE)
XML_NAMESPACES = {'cas': CAS_NAMESPACE}

log = logging.getLogger(__name__)


class FormPluginBase(object):
    def _get_rememberer(self, environ):
        rememberer = environ['repoze.who.plugins'][self.rememberer_name]
        return rememberer

    # IIdentifier
    def remember(self, environ, identity):
        rememberer = self._get_rememberer(environ)
        return rememberer.remember(environ, identity)

    #IIdentifier
    def forget(self, environ, identity):
        rememberer = self._get_rememberer(environ)
        return rememberer.forget(environ, identity)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, id(self))


# Former redirectingFormPlugin
class CASChallengePlugin(FormPluginBase):

    implements(IChallenger,
               IIdentifier,
               IAuthenticator)

    def __init__(self,
                 cas_url,
                 path_logout,
                 path_toskip,
                 rememberer_name,
                 cas_version=1.0,
                 attributes_name='attributes'):
        self.cas_url = cas_url
        self.cas_version = cas_version
        self.path_logout = path_logout
        self.path_toskip = path_toskip
        self.attributes_name = attributes_name
        # rememberer_name is the name of another configured plugin which
        # implements IIdentifier, to handle remember and forget duties
        # (ala a cookie plugin or a session plugin)
        self.rememberer_name = rememberer_name


    # IChallenger
    def challenge(self, environ, status, app_headers, forget_headers):

        # This challenge consists of logging out
        if environ.has_key('rwpc.logout'):
            log.debug("Headers before logout: " + str(app_headers))
            app_headers = [(a, b) for a, b in app_headers \
                           if a.lower() != 'location' ]
            log.debug("Headers after logout: " + str(app_headers))

            logout_url = '{cas_url}logout?service={service_url}'.format(
                cas_url=self.cas_url,
                service_url=urllib.quote(environ['rwpc.logout']))

            # FIXME: should Location replace the key rwpc.logout?
            headers = [('Location', logout_url)]
            headers = headers + app_headers + forget_headers

            log.debug("Logout headers: " + str(headers))

            return HTTPFound(headers=headers)

        # Perform a real challenge by redirecting the user to CAS
        else:
            login_url = '{cas_url}login?service={service_url}'.format(
                cas_url=self.cas_url,
                service_url=urllib.quote(self._serviceURL(environ)))

            log.debug('Login URL: ' + login_url)

            headers = [('Location', login_url)]
            cookies = [(h,v) for (h,v) in app_headers \
                       if h.lower() == 'set-cookie']
            headers = headers + forget_headers + cookies

            return HTTPFound(headers=headers)

    # IIdentifier
    def identify(self, environ):
        """ Identify the user according to the current environment.

        An incoming request will be processed as follows, from top to
        bottom:

        #. If a logout is in progress, return immediately.
        #. If the URI matches a *logout* regex path, then log the user out.

           #. The user will be forgotten via the ``rememberer`` specified
              by ``rememberer_name``, and
           #. A redirection will log the user out from CAS.

        #. If the URI matches a *skip* regex path, then skip identification
        #. If the query string contains a CAS ticket, then validate it
           against the server and return the result.
        """
        #If logout is in process, abort identification
        if environ.has_key('rwpc.logout'):
            return

        uri = environ.get('REQUEST_URI', construct_url(environ))
        query = parse_dict_querystring(environ)

        #Logout for a path that matches the configuration
        for path in self.path_logout:
            if path.match(uri):
                # Trigger a challenge and tell challenge this is a
                # logout, passing the service URL to CAS
                log.debug('Logout called')
                environ['rwpc.logout'] = \
                        self._serviceURL(environ, urllib.urlencode(query))
                return

        #Skip any path that matches the configuration
        for path in self.path_toskip:
            if path.match(uri):
                log.debug('Skipping path: {}'.format(uri))
                return

        #Check the CAS validation ticket
        ticket = query.pop('ticket', None)
        if ticket:
            log.debug("Retrieving credentials: validating against CAS")
            credentials = self._validate(ticket, environ, query)
            return credentials

    def _validate(self, ticket, environ, query):
        """ Validate the given ticket against CAS.
        """
        #Construct the validation URL based on CAS version
        if self.cas_version >= 2.0:
            base_url = '{cas_url}serviceValidate?service={service_url}&ticket={ticket}'
        else:
            base_url = '{cas_url}validate?service={service_url}&ticket={ticket}'

        service_url = urllib.quote(self._serviceURL(environ, urllib.urlencode(query)))
        validate_url = base_url.format(cas_url=self.cas_url,
                                       service_url=service_url,
                                       ticket=urllib.quote(ticket))

        response = urllib.urlopen(validate_url).read()
        log.debug('Validation response: ' + response)

        if self.cas_version >= 2.0:
            #CAS 2.0 validates with an XML-fragment response. See
            #section 2.5 of the CAS protocol.
            parsed = ElementTree.fromstring(response)
            success = parsed.find('cas:authenticationSuccess',
                                  namespaces=XML_NAMESPACES)
            if success != None:
                login = success.find('cas:user',
                                     namespaces=XML_NAMESPACES).text
                result = {'login': login, 'password': ''}

                if self.attributes_name:
                    attributes = success.find('cas:attributes',
                                              namespaces=XML_NAMESPACES)
                    if attributes != None:
                        processed_attributes = {}
                        for attribute in attributes.getchildren():
                            name = attribute.tag.replace(
                                CAS_NAMESPACE_PREFIX, '')
                            processed_attributes[name] = attribute.text
                        result[self.attributes_name] = processed_attributes

                return result

        else:
            #CAS 1.0 returns 2 lines - see section 2.4.2 of CAS protocol
            validation = response.splitlines()
            if len(validation) == 2 and re.match("yes", validation[0]):
                return {'login': validation[1].strip(),
                        'password': ''}

        return None

    def _serviceURL(self, environ, qs=None):
        """ Return a URL representing the current application (service).

        Used 2 times : one to get the ticket, the other to validate it.
        """
        if qs:
            url = construct_url(environ, querystring=qs)
        else:
            url = construct_url(environ)
        return url

    # IAuthenticatorPlugin
    def authenticate(self, environ, identity):
        """ Return the user's login ID.

        In actuality, this method does nothing as CAS has already
        checked the user's credentials for us.
        """
        return identity.get('login')


def compile_paths_regex(paths):
    """ Pre-compile path regex for speed in processing requests.
    """
    return [re.compile(path) for path in paths.lstrip().splitlines()]


def make_plugin(cas_url=None,
                cas_version=1.0,
                rememberer_name=None,
                attributes_name=None,
                path_logout='',
                path_toskip='',
                debug=False):
    """ Return a fully configured repoze.who CAS plugin.

    Arguments/Keywords

    cas_url
        Base URL for the CAS server. Validation, logout and other URLs
        will be built using this URL as a base.

        For example: ``http://example.com/cas/``

    cas_version
        Numerical identifier representing the version of the CAS protocol
        to follow.
        
        At present, this changes the validation behaviour
        only.  For example, CAS 1.0 specifies calling ``/validate``
        to validate an authentication ticket and CAS 2.0 specifies
        calling ``/serviceValidate``. Eventually, other CAS 2.0 and
        above methods will be supported

        Default: ``1.0``

    rememberer_name
        Name of a configured ``identifiers`` plugin (implementing the
        ``IIdentifier`` interface) that will be used to remember and
        forget the user's identity after authentication to CAS.

        For example, a typical use case is to remember the user using a
        client-side cookie or a session.  This can be
        achieved through using a plugin like
        ``repoze.who.plugins.auth_tkt``.

    attributes_name
        Identifier to use to place retrieved CAS attributes (user
        metadata) into within the ``repoze.who`` identity. By setting this
        value, attributes will be processed if they exist
        and were released on CAS ticket validation.

        This process requires CAS 2.0 service validation (so
        ``cas_version`` must be set to ``2.0`` or above) and your
        CAS server must support attribute release.

        All attributes released at time of ticket validation will be
        placed into the identity using the key specified by
        ``attributes_name``.  Note that as attributes are obtained
        **only** during validation, meaning they will only persist
        inside the identity during the validation request **only**.

        You must configure another ``repoze.who`` plugin to store this
        part of the ``identity`` after the initial ticket validation
        request or else this information will not be available.
        This may either be in a cookie, session, or cache.

        Default: ``None`` (do not process attributes).

    path_logout
        One or more paths that will cause the logout process to be
        carried out. Separate multiple paths with a newline character.

        Default: ``''`` (empty string)

    path_toskip
        One or more paths to skip authentication for. Separate multiple
        paths with a newline character.

        Default: ``''`` (empty string)
    """
    #Check presence of required options
    required_keywords = ('cas_url', 'rememberer_name')
    for kw in required_keywords:
        if not eval(kw):
            raise ValueError(
                'CAS plugin configuration must include {}.'.format(kw))

    plugin = CASChallengePlugin(
        cas_url=cas_url,
        cas_version=float(cas_version),
        rememberer_name=rememberer_name,
        attributes_name=attributes_name,
        path_logout=compile_paths_regex(path_logout),
        path_toskip=compile_paths_regex(path_toskip))

    return plugin


