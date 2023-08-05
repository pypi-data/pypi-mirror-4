import requests
import time
import hashlib

from urllib import urlencode


class AstridAPI(object):
    '''Connect to the Astrid Tasks API and issue requests to a specific
    user's account.

    Python Astrid API lives at https://bitbucket.org/dusty/python-astrid/
    and documentation is available at https://python-astrid.readthedocs.org/
    '''

    def __init__(self, conf):
        '''
        :param conf: a dictionary of configuration values
            for connecting to the API.

        The conf dictionary must contain::

            {
                "apikey": "<astrid api key>",
                "apisecret": "<astrid api secret>",
                "email": "you@example.com", # your astrid e-mail
                "password": "<astrid password>"
            }

        The apikey and secret can come from http://astrid.com/api_keys

        The user associated with the email and
        password provided in the configuration dictionary
        will be automatically signed in.
        The token received from signin
        is stored on the class and automatically sent
        with future requests.
        '''
        self.server = 'https://astrid.com'
        self.astrid_api_version = 7
        self.apikey = conf['apikey']
        self.apisecret = conf['apisecret']
        try:
            self.token = self.request("user_signin",
                email=conf['email'],
                provider="password",
                secret=conf['password'])['token']
        except KeyError:
            raise AttributeError("Unable to sign into astrid. Ensure your "
                "api key, api secret, email, and password are correct.")

    def request(self, method, **params):
        '''Send a request to the astrid API.
        The available methods and their parameters are described in
        http://astrid.com/apidoc/ApiController.html

        This method does the necessary work
        to create an astrid signature line as required by the API.
        It then issues the request in the format Astrid expects.

        :param method: the method name to call in the Astrid API
        :param params: keyword arguments mapping parameters to values as
            required by the *method*
        :return: json decoded response of your Astrid API request
        :rtype: dict
        '''
        signature = []
        params['app_id'] = self.apikey
        params['time'] = time.time()
        if hasattr(self, 'token'):
            params['token'] = self.token
        for param in sorted(params):
            value = params[param]
            if isinstance(value, list):
                signature.extend([("%s[]%s" % (param, v)) for v in value])
            else:
                signature.append("%s%s" % (param, value))
        sig = "%s%s%s" % (method, "".join(signature), self.apisecret)
        sig = hashlib.md5(sig).hexdigest()
        params['sig'] = sig

        url = "%s/api/%s/%s?%s" % (
            self.server,
            self.astrid_api_version,
            method,
            urlencode(params))

        return requests.post(url, data=params).json
