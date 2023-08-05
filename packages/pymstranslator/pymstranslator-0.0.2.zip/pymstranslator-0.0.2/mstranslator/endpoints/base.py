"""Base classes for endpoint processing"""

from __future__ import unicode_literals

from urllib import urlencode
from xml.etree import ElementTree
from copy import copy

from mstranslator.utils import Constant

__all__ = ['AUDIO', 'CONTENT', 'Endpoint', 'GetEndpoint']

AUDIO = Constant(
    MAX='MaxQuality',
    MIN='MinSize',
)

CONTENT = Constant(
    HTML='text/html',
    TXT='text/plain',
)

LANGUAGES = (
    ('ar' 'Arabic'),
    ('bg' 'Bulgarian'),
    ('ca', 'Catalan'),
    ('zh-CHS', 'Chinese (Simplified)'),
    ('zh-CHT', 'Chinese (Traditional)'),
    ('cs', 'Czech'),
    ('da', 'Danish'),
    ('nl', 'Dutch'),
    ('en', 'English'),
    ('et', 'Estonian'),
    ('fa', 'Persian (Farsi)'),
    ('fi', 'Finnish'),
    ('fr', 'French'),
    ('de', 'German'),
    ('el', 'Greek'),
    ('ht', 'Haitian Creole'),
    ('he', 'Hebrew'),
    ('hi', 'Hindi'),
    ('hu', 'Hungarian'),
    ('id', 'Indonesian'),
    ('it', 'Italian'),
    ('ja', 'Japanese'),
    ('ko', 'Korean'),
    ('lv', 'Latvian'),
    ('lt', 'Lithuanian'),
    ('mww', 'Hmong Daw'),
    ('no', 'Norwegian'),
    ('pl', 'Polish'),
    ('pt', 'Portuguese'),
    ('ro', 'Romanian'),
    ('ru', 'Russian'),
    ('sk', 'Slovak'),
    ('sl', 'Slovenian'),
    ('es', 'Spanish'),
    ('sv', 'Swedish'),
    ('th', 'Thai'),
    ('tr', 'Turkish'),
    ('uk', 'Ukrainian'),
    ('vi', 'Vietnamese '),
)

LANGUAGE_CODES = [l[0] for l in LANGUAGES]

class Endpoint(object):
    endpoint = None
    api_protocol = 'http'
    api_base = 'api.microsofttranslator.com'
    api_version = 'V2'
    api_type = 'HTTP.svc'
    params = {}
    data = None

    def convert_args(self, args):
        pass

    def convert_kwargs(self, kwargs):
        if 'self' in kwargs:
            del kwargs['self']
        if 'tfrom' in kwargs:
            kwargs['from'] = kwargs['tfrom']
            del kwargs['tfrom']

        if 'fmt' in kwargs:
            kwargs['format'] = kwargs['fmt']
            del kwargs['fmt']

        url_params = dict()

        for k, v in kwargs.items():
            url_params[self.camelize_param(k)] = v

        self.params = url_params

    def camelize_param(self, s):
        """Takes all_lowercase and turns it into camelCase"""

        final = ''
        parts = s.split('_')
        final += parts.pop(0)

        for p in parts:
            final += p[0].upper() + p[1:]

        return final

    def get_endpoint_url(self):
        if not self.endpoint:
            raise NotImplementedError('You must set endpoint attribute')

        return '%s://%s/%s/%s/%s' % (
            self.api_protocol,
            self.api_base,
            self.api_version,
            self.api_type,
            self.endpoint,
        )

    def get_quoted_params(self):
        # first get a copy of params and encode UTF-8
        params = copy(self.params)
        for p, v in params.items():
            if isinstance(v, unicode):
                params[p] = v.encode('UTF-8')

        # ... then encode params
        return urlencode(params)

    def get_request_url(self):
        return '%s?%s' % (self.get_endpoint_url(), self.get_quoted_params())

    def store_data(self):
        raise NotImplementedError('Please override this method in subclass')

    def get_data(self):
        return self.data

    def parse_xml(self, response):
        e = ElementTree.parse(response)
        return e.getroot()

    def process_response(self, response):
        raise NotImplementedError('Please override this method in subclass')


class GetEndpoint(Endpoint):
    def store_data(self):
        raise RuntimeError('GET endpoints have no data')

    def process_response(self, response):
        """Returns verbatim response"""
        return response



