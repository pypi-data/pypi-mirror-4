from requests_oauth2 import OAuth2


class Auth(object):

    AUTH_URL_BASE = 'https://launchpad.37signals.com/authorization/'
    AUTH_URL_NEW = 'new'
    AUTH_URL_TOKEN = 'token'

    def __init__(self, client_id, client_secret, redirect_url):
        self.oauth2 = OAuth2(client_id,
                client_secret,
                self.AUTH_URL_BASE,
                redirect_url,
                self.AUTH_URL_NEW,
                self.AUTH_URL_TOKEN)

    def authorize_url(self, state=None):
        """Return an authorization url that opens a dialog for a user.
        """
        return self.oauth2.authorize_url(type='web_server', state=state)

    def access_token(self, code='', client_type='web_server', **kwargs):
        """Get or renew an access token. Return a dictionary with
        access token, expiration time, and refresh token (only for
        new tokens).
        """
        response = self.oauth2.get_token(code, type=client_type, **kwargs)
        return response
