import urlparse
import urllib2
import re
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, URL_VALIDATOR_USER_AGENT
from django.utils.encoding import smart_unicode
from django.core.urlresolvers import reverse


class ViewPathValidator(RegexValidator):
    regex = re.compile(
        r'^(((?!/)\S)+)$' , re.IGNORECASE) # option : accept everything except '/' and spaces

    def __call__(self, value):
        try:
            super(ViewPathValidator, self).__call__(value)
        except ValidationError, e:
            raise
        else:
            value = value
        try:
            url = reverse(value)
        except: # view does not exist
            raise ValidationError(_(u'This View does not exist.'), code='invalid_view')


class URLValidator(RegexValidator):
    regex = re.compile(
        r'(?!^//)'                                      # dont accept start with '//'
        r'^('                                           # block start with
          r'('                                          # optional adress block
            r'(https?://|ftp://)'                       # block protocol
            r'('                                        # block server name
              r'(([A-Z0-9]\.?)+)|'                      # a domain or just a server name
              r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'   # or an ip number
            r')'                                        # end server name
            r'(?::\d+)?'                                # with optional port
          r')|'                                         # end optional adress block
          r'(\.\.?)|'                                   # or start with '.(.)'
          r'(/{1})|'                                    # or start with unik '/'
          r'((?![/|\s]))'                               # or start at least by one non space char except '/'
        r')'                                            # end startwith
        r'((?!//)\S)*$' , re.IGNORECASE)                # optional end with : accept everything except '//' and spaces

    def __init__(self, verify_exists=False, validator_user_agent=URL_VALIDATOR_USER_AGENT):
        super(URLValidator, self).__init__()
        self.verify_exists = verify_exists
        self.user_agent = validator_user_agent

    def __call__(self, value):
        try:
            super(URLValidator, self).__call__(value)
        except ValidationError, e:
            if value:
                value = smart_unicode(value)
                scheme, netloc, path, query, fragment = urlparse.urlsplit(value)
                url = urlparse.urlunsplit((scheme, netloc, path, query, fragment))
                super(URLValidator, self).__call__(url)
            else:
                raise
        else:
            url = value

        if self.verify_exists:
            headers = {
                "Accept": "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
                "Accept-Language": "en-us,en;q=0.5",
                "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
                "Connection": "close",
                "User-Agent": self.user_agent,
            }
            try:
                req = urllib2.Request(url, None, headers)
                u = urllib2.urlopen(req)
            except ValueError:
                raise ValidationError(_(u'Enter a valid URL.'), code='invalid')
            except: # urllib2.URLError, httplib.InvalidURL, etc.
                raise ValidationError(_(u'This URL appears to be a broken link.'), code='invalid_link')