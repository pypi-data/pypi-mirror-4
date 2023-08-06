# -*- coding: utf-8 -*-
"""
    rest

    The rest API for magento

    :copyright: (c) 2012 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import sys
from urlparse import parse_qs

import requests
from oauth_hook import OAuthHook


class MagentoOauthClient(object):
    """
    An OAuth client capable of talking to magento
    """


    def __init__(self, host, key, secret,
            request_token_url = '/oauth/initiate',
            access_token_url = '/oauth/token',
            authorization_url = '/oauth/authorize',
            admin_authorization_url = '/admin/oauth_authorize',
            ):
        self.host = host
        self.key = key
        self.secret = secret

        self.oauth_token = None
        self.oauth_token_secret = None
        self.auth_verifier = None
        self.access_token = None
        self.access_token_secret = None

        self.request_token_url= request_token_url
        self.access_token_url= access_token_url
        self.authorization_url= authorization_url
        self.admin_authorization_url= admin_authorization_url

    def fetch_request_token(self, oauth_callback):
        """
        The first step to authenticate the user is to retrieve a Request Token
        from Magento. This is a temporary token that will be exchanged for the
        Access Token.

        :param oauth_callback: URL to callback. Magento checks if this is a 
                               valid URL.
        :return: Returns oauth_token and oauth_token_secret tuple
        """
        hook = self.get_hook()
        response = requests.post(
            '%s%s' % (self.host, self.request_token_url),
            {'oauth_callback': oauth_callback},
            hooks={'pre_request': hook}
        )
        qs = parse_qs(response.text)
        try:
            self.oauth_token = qs['oauth_token'][0]
            self.oauth_token_secret = qs['oauth_token_secret'][0]
            return self.oauth_token, self.oauth_token_secret
        except KeyError, kerr:
            if 'oauth_problem' in qs:
                raise Exception(qs['oauth_problem'][0], qs['message'][0])
            raise

    def get_authorization_url(self, admin=True):
        """
        Returns a URL from which the user can authorize Magento to give info
        to the application

        :param admin: If the authorization is for the admin interface or
                      customer
        """
        return '%s%s?oauth_token=%s' % (
            self.host, 
            admin and self.admin_authorization_url or self.authorization_url,
            self.oauth_token
        )

    def fetch_access_token(self, oauth_verifier):
        """
        The final third authentication step. After the application access is
        authorized, the application needs to exchange the Request Token for an
        Access Token.

        :param oauth_verifier: Fetched from the callback made by magento on
                               user authorization by following URL generated
                               by get_authorization_url
        """
        hook = self.get_hook()
        response = requests.post(
            '%s%s' % (self.host, self.access_token_url),
            {'oauth_verifier': oauth_verifier},
            hooks={'pre_request': hook}
        )
        response = parse_qs(response.content)
        try:
            self.access_token = response['oauth_token'][0]
            self.access_token_secret = response['oauth_token_secret'][0]
            return self.access_token, self.access_token_secret
        except KeyError:
            if 'oauth_problem' in response:
                raise Exception(
                    response['oauth_problem'][0], response['message'][0]
                )
            raise

    def get_hook(self):
        "Returns hook which can be used with requests"
        return OAuthHook(
            self.access_token or self.oauth_token,
            self.access_token_secret or self.oauth_token_secret,
            self.key, self.secret
        )

    def get_session(self):
        oauth_hook = OAuthHook(
            self.access_token, self.access_token_secret,
            self.key, self.secret, header_auth=True
        )
        return requests.session(hooks={'pre_request': oauth_hook})


if __name__ == '__main__':
    client = MagentoOauthClient(*sys.argv[1:])
    oauth_token, oauth_token_secret = client.fetch_request_token(
        'http://localhost'
    )
    print "Go to:", client.get_authorization_url(oauth_token)
    print "Magento API does not support pins."
    print "So wait for the redirect and get the oauth_verifier from the URL"
    oauth_verifier = raw_input('Enter Verifier: ')

    print client.fetch_access_token(oauth_verifier)

    print "fetching products"
    session = client.get_session()
    print session.get('%s/api/rest/products' % client.host).content

