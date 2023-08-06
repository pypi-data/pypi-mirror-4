"""
This is an OpenID challenger for TiddlyWeb that replaces the one that
was originally included in the core TiddlyWeb package. It improves on
that one by using the python-openid package, thus supporting OpenID 2
and improved discovery mechanisms.

To use, add 'tiddlywebplugins.openid2' to auth_systems via
tiddlywebconfig.py. The following example replaces all existing
auth_systems with just openid.

config = {
    'auth_systems': ['tiddlywebplugins.openid2'],
}
"""

import logging
import urlparse

from httpexceptor import HTTP302

from openid import oidutil
from openid.consumer import consumer

from tiddlyweb.web.challengers import ChallengerInterface
from tiddlyweb.web.util import server_base_url, server_host_url, make_cookie


LOGGER = logging.getLogger(__name__)


def log_message(message, level=0):
    """
    Redefine the Python OpenID log function,
    which just writes to stderr, spewing all
    over the place.
    """
    LOGGER.debug(message)

oidutil.log = log_message


class Challenger(ChallengerInterface):

    desc = "OpenID"

    def __init__(self):
        self.name = __name__

    def challenge_get(self, environ, start_response):
        openid_mode = environ['tiddlyweb.query'].get('openid.mode', [None])[0]

        if openid_mode:
            return self._handle_response(environ, start_response)
        else:
            return self._render_form(environ, start_response)

    def challenge_post(self, environ, start_response):
        openid_url = environ['tiddlyweb.query'].get('openid', [None])[0]
        redirect = environ['tiddlyweb.query'].get(
            'tiddlyweb_redirect', ['/'])[0]

        if not openid_url:
            return self._render_form(environ, start_response,
                    message='Enter an openid')
        # Make a bare bones stateless consumer
        oidconsumer = consumer.Consumer({}, None)

        try:
            request = oidconsumer.begin(openid_url)
        except consumer.DiscoveryFailure, exc:
            return self._render_form(environ, start_response,
                    openid=openid_url,
                    message='Error in discovery: %s' % exc[0])

        if request is None:
            return self._render_form(environ, start_response,
                    openid=openid_url,
                    message='No open id services for %s' % openid_url)
        else:
            trust_root = server_base_url(environ)
            return_to = urlparse.urljoin(trust_root, '%s/challenge/%s' % (
                environ['tiddlyweb.config']['server_prefix'],
                self.name))
            request.return_to_args['tiddlyweb_redirect'] = redirect

            if request.shouldSendRedirect():
                redirect_url = request.redirectURL(trust_root, return_to,
                        immediate=False)
                raise HTTP302(redirect_url)
            else:
                form_html = request.htmlMarkup(trust_root, return_to,
                        form_tag_attrs={'id': 'openid_message'},
                        immediate=False)
                start_response('200 OK', [
                    ('Content-Type', 'text/html; charset=UTF-8')])
                return [form_html]

    def _handle_response(self, environ, start_response):
        oidconsumer = consumer.Consumer({}, None)
        host = server_base_url(environ)
        url = urlparse.urljoin(host, '%s/challenge/%s' % (
                environ['tiddlyweb.config']['server_prefix'],
                self.name))
        query = {}
        for key in environ['tiddlyweb.query']:
            query[key] = environ['tiddlyweb.query'][key][0]
        info = oidconsumer.complete(query, url)

        display_identifier = info.getDisplayIdentifier()

        if info.status == consumer.FAILURE and display_identifier:
            return self._render_form(environ, start_response,
                    openid=display_identifier,
                    message='Verification of %s failed with: %s' % (
                        display_identifier, info.message))
        elif info.status == consumer.SUCCESS:
            return self._success(environ, start_response, info)
        elif info.status == consumer.CANCEL:
            return self._render_form(environ, start_response,
                    message='You cancelled, try again with something else?')
        elif info.status == consumer.SETUP_NEEDED:
            if info.setup_url:
                message = ('<a href=%s>Setup needed at openid server.</a>'
                        % info.setup_url)
            else:
                message = 'More information needed at server'
            return self._render_form(environ, start_response,
                    message=message)
        else:
            return self._render_form(environ, start_response,
                    message='Unable to process. Unknown error')

    def _success(self, environ, start_response, info):
        usersign = info.getDisplayIdentifier()
        if info.endpoint.canonicalID:
            usersign = info.endpoint.canonicalID
        # canonicolize usersign to tiddlyweb form
        if usersign.startswith('http'):
            usersign = usersign.split('://', 1)[1]
        usersign = usersign.rstrip('/')
        uri = urlparse.urljoin(server_host_url(environ),
                environ['tiddlyweb.query'].get('tiddlyweb_redirect', ['/'])[0])
        secret = environ['tiddlyweb.config']['secret']
        cookie_age = environ['tiddlyweb.config'].get('cookie_age', None)
        cookie_header_string = make_cookie('tiddlyweb_user', usersign,
                mac_key=secret, path=self._cookie_path(environ),
                expires=cookie_age)
        start_response('303 See Other',
                [('Location', uri.encode('utf-8')),
                    ('Content-Type', 'text/plain'),
                    ('Set-Cookie', cookie_header_string)])
        return [uri]

    def _render_form(self, environ, start_response, openid='',
            message='', form=''):
        redirect = environ['tiddlyweb.query'].get(
            'tiddlyweb_redirect', ['/'])[0]
        start_response('200 OK', [
            ('Content-Type', 'text/html')])
        environ['tiddlyweb.title'] = 'OpenID Login'
        return ["""
<div id='content'>
    <div class='message'>%s</div>
    <pre>
    <form action="" method="POST">
    OpenID: <input name="openid" size="60" value="%s"/>
    <input type="hidden" name="tiddlyweb_redirect" value="%s" />
    <input type="submit" value="submit" />
    </form>
    </pre>
</div>""" % (message, openid, redirect)]
