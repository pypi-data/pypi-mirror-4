from __future__ import unicode_literals

from urllib2 import Request, urlopen, URLError
from urllib import urlencode
from datetime import datetime, timedelta
import json

from utils import Constant

from endpoints import *

AUDIO = Constant(
    MAX='MaxQuality',
    MIN='MinSize',
)

CONTENT = Constant(
    HTML='text/html',
    TXT='text/plain',
)

class MSTranslatorAccessKey(object):
    """Initializes a new access key.

    This object should only be initialized once per session. After that,
    calling the ``get_key()`` method will fetch the new key as needed.

    """

    oauth_url = 'https://datamarket.accesscontrol.windows.net/v2/OAuth2-13'
    scope_url = 'http://api.microsofttranslator.com'
    grant_type = 'client_credentials'

    created = None
    access_key = None
    expiry = 10*60

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def expired(self):
        if not self.created:
            return True

        return datetime.now() - self.created > timedelta(0, self.expiry)

    def create_key(self):
        self.created = datetime.now()

        data = urlencode(dict(
            client_id = self.client_id,
            client_secret = self.client_secret,
            grant_type = self.grant_type,
            scope = self.scope_url
        ))

        request = Request(url=self.oauth_url, data=data)
        response = urlopen(request)
        response = json.loads(response.read())

        self.access_key = response['access_token']
        self.expiry = int(response['expires_in'])

        return self.access_key

    def get_key(self):
        if self.access_key and not self.expired():
            return self.access_key

        return self.create_key()


class MSTranslator(object):
    auth_header_name = 'Authorization'

    def __init__(self, api_key):
        if not isinstance(api_key, MSTranslatorAccessKey):
            raise ValueError('API key must be a MSTranslatorAccessKey instance')

        self.api_key = api_key

    # core methods

    def get_authorization_string(self):
        if not self.api_key:
            raise RuntimeError('Cannot use Translator API without API key.')

        return "Bearer %s" % self.api_key.get_key()

    def get_authorization_header(self):
        return {self.auth_header_name: self.get_authorization_string()}

    def process_endpoint(self, endpoint):
        request = Request(
            url=endpoint.get_request_url(),
            headers=self.get_authorization_header(),
        )

        data=endpoint.get_data()

        if data:
            request.add_data(data)

        return endpoint.process_response(urlopen(request))

    # api calls

    def detect(self, text):
        """Detect language used in the text and return the language code.

        """

        raise NotImplementedError('detect is not implemented yet')

    def detect_array(self, texts):
        """Detect langauges used in texts, and return a list of codes.

        """

        raise NotImplementedError('detect_array is not implemented yet')

    def get_languages_for_translation(self):
        """Get a list of language codes supported by translate feature.

        """

        raise NotImplementedError('get_languages_for_translate is not '
                                  'implemented yet')

    def translate(self, *args, **kwargs):
        """Translate text from one language to another.

        """
        endpoint = TranslateEndpoint(*args, **kwargs)
        return self.process_endpoint(endpoint)

