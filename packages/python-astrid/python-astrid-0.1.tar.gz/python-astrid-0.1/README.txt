
Welcome to Astrid Python API's documentation!
*********************************************

Contents:

class class astrid.AstridAPI(conf)

   Connect to the Astrid Tasks API and issue requests to a specific
   user's account.

   Python Astrid API lives at https://bitbucket.org/dusty/python-
   astrid/ and documentation is available at https://python-
   astrid.readthedocs.org/

   Parameters:
      **conf** -- a dictionary of configuration values for connecting
      to the API.

   The conf dictionary must contain:

      {
          "apikey": "<astrid api key>",
          "apisecret": "<astrid api secret>",
          "email": "you@example.com", # your astrid e-mail
          "password": "<astrid password>"
      }

   The apikey and secret can come from http://astrid.com/api_keys

   The user associated with the email and password provided in the
   configuration dictionary will be automatically signed in. The token
   received from signin is stored on the class and automatically sent
   with future requests.

   request(method, **params)

      Send a request to the astrid API. The available methods and
      their parameters are described in
      http://astrid.com/apidoc/ApiController.html

      This method does the necessary work to create an astrid
      signature line as required by the API. It then issues the
      request in the format Astrid expects.

      Parameters:
         * **method** -- the method name to call in the Astrid API

         * **params** -- keyword arguments mapping parameters to
           values as required by the *method*

      Returns:
         json decoded response of your Astrid API request

      Return type:
         dict
