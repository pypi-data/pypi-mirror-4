from django.core.cache import cache
from django.conf import settings
from django.utils.html import *


def _get_site_name_or_baseline(return_baseline = False):
    """
    Read the site name from global community.
    We use tricks to ensure we can get the glob com. even with anonymous requests.
    """
    d = cache.get_many(["twistranet_site_name", "twistranet_baseline"])
    site_name = d.get("site_name", None)
    baseline = d.get("baseline", None)
    if site_name is None or baseline is None:
        from twistranet.twistapp.models import SystemAccount, GlobalCommunity
        __account__ = SystemAccount.get()
        try:
            glob = GlobalCommunity.get()
            site_name = glob.site_name
            baseline = glob.baseline
        finally:
            del __account__
        cache.set('twistranet_site_name', site_name)
        cache.set("twistranet_baseline", baseline)
    if return_baseline:
        return baseline
    return site_name
    
def get_site_name():
    return _get_site_name_or_baseline(return_baseline = False)
def get_baseline():
    return _get_site_name_or_baseline(return_baseline = True)


def truncate(text, length, ellipsis=u'\u2026'):
    if text is None:
        text = ''
    if not isinstance(text, basestring):
        raise ValueError("%r is no instance of basestring or None" % text)

    # thread other whitespaces as word break
    content = text.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
    # make sure to have at least one space for finding spaces later on
    content += ' '

    if len(content) > length:
        # find the next space after max_len chars (do not break inside a word)
        pos = length + content[length:].find(' ')
        if pos != (len(content) - 1):
            # if the found whitespace is not the last one add an ellipsis
            text = text[:pos].strip() + ' ' + ellipsis

    return text

def formatbytes(sizeint, configdict=None, **configs):
    """
    Given a file size as an integer, return a nicely formatted string that
    represents the size. Has various options to control it's output.
    
    """
    defaultconfigs = {  'forcekb' : False,
                        'largestonly' : True,
                        'kiloname' : 'KB',
                        'meganame' : 'MB',
                        'bytename' : 'bytes',
                        'nospace' : True}
    if configdict is None:
        configdict = {}
    for entry in configs:
        # keyword parameters override the dictionary passed in
        configdict[entry] = configs[entry]
    #
    for keyword in defaultconfigs:
        if not configdict.has_key(keyword):
            configdict[keyword] = defaultconfigs[keyword]
    #
    if configdict['nospace']:
        space = ''
    else:
        space = ' '
    #
    mb, kb, rb = bytedivider(sizeint)
    if configdict['largestonly']:
        if mb and not configdict['forcekb']:
            return stringround(mb, kb)+ space + configdict['meganame']
        elif kb or configdict['forcekb']:
            if mb and configdict['forcekb']:
                kb += 1024*mb
            return stringround(kb, rb) + space+ configdict['kiloname']
        else:
            return str(rb) + space + configdict['bytename']
    else:
        outstr = ''
        if mb and not configdict['forcekb']:
            outstr = str(mb) + space + configdict['meganame'] +', '
        if kb or configdict['forcekb'] or mb:
            if configdict['forcekb']:
                kb += 1024*mb
            outstr += str(kb) + space + configdict['kiloname'] +', '
        return outstr + str(rb) + space + configdict['bytename']

def bytedivider(nbytes):
    """
    Given an integer (probably a long integer returned by os.getsize() )
    it returns a tuple of (megabytes, kilobytes, bytes).
    
    This can be more easily converted into a formatted string to display the
    size of the file.
    """
    mb, remainder = divmod(nbytes, 1048576)
    kb, rb = divmod(remainder, 1024)
    return (mb, kb, rb)

def stringround(main, rest):
    """
    Given a file size in either (mb, kb) or (kb, bytes) - round it
    appropriately.
    """
    # divide an int by a float... get a float
    value = main + rest/1024.0
    return str(round(value, 1))

def _check_file_size(data):
    """
    check file size depending on max upload in settings
    """
    max_size = int(settings.QUICKUPLOAD_SIZE_LIMIT)
    if not max_size :
        return 1
    data.seek(0, os.SEEK_END)
    file_size = data.tell() / 1024
    data.seek(0, os.SEEK_SET )
    if file_size<=max_size:
        return 1
    return 0

# XXX mut be removed when django ticket https://code.djangoproject.com/ticket/9655
# will be resolved
def twist_urlize(text, trim_url_limit=None, nofollow=False, autoescape=False):
    """
    BASED on django.utils.html urlize
    but also fix the bug  https://code.djangoproject.com/ticket/9655
    
    Original text :
    
    Converts any URLs in text into clickable links.

    Works on http://, https://, www. links and links ending in .org, .net or
    .com. Links can have trailing punctuation (periods, commas, close-parens)
    and leading punctuation (opening parens) and it'll still do the right
    thing.

    If trim_url_limit is not None, the URLs in link text longer than this limit
    will truncated to trim_url_limit-3 characters and appended with an elipsis.

    If nofollow is True, the URLs in link text will get a rel="nofollow"
    attribute.

    If autoescape is True, the link text and URLs will get autoescaped.
    """
    trim_url = lambda x, limit=trim_url_limit: limit is not None and (len(x) > limit and ('%s...' % x[:max(0, limit - 3)])) or x
    safe_input = isinstance(text, SafeData)
    words = word_split_re.split(force_unicode(text))
    nofollow_attr = nofollow and ' rel="nofollow"' or ''
    for i, word in enumerate(words):
        match = None
        if '.' in word or '@' in word or ':' in word:
            match = punctuation_re.match(word)
        if match:
            lead, middle, trail = match.groups()
            # Make URL we want to point to.
            url = None
            if middle.startswith('http://') or middle.startswith('https://'):
                # XXX : The fix is here
                url = urlquote(middle, safe='/%&=:;#?+*')
            elif middle.startswith('www.') or ('@' not in middle and \
                    middle and middle[0] in string.ascii_letters + string.digits and \
                    (middle.endswith('.org') or middle.endswith('.net') or middle.endswith('.com'))):
                url = urlquote('http://%s' % middle, safe='/&=:;#?+*')
            elif '@' in middle and not ':' in middle and simple_email_re.match(middle):
                url = 'mailto:%s' % middle
                nofollow_attr = ''
            # Make link.
            if url:
                trimmed = trim_url(middle)
                if autoescape and not safe_input:
                    lead, trail = escape(lead), escape(trail)
                    url, trimmed = escape(url), escape(trimmed)
                middle = '<a href="%s"%s>%s</a>' % (url, nofollow_attr, trimmed)
                words[i] = mark_safe('%s%s%s' % (lead, middle, trail))
            else:
                if safe_input:
                    words[i] = mark_safe(word)
                elif autoescape:
                    words[i] = escape(word)
        elif safe_input:
            words[i] = mark_safe(word)
        elif autoescape:
            words[i] = escape(word)
    return u''.join(words)
twist_urlize = allow_lazy(twist_urlize, unicode)