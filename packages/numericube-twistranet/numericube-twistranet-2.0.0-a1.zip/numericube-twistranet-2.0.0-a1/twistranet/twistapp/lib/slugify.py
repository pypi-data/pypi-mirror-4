import re
import unicodedata
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist

# List of words you're not allowed to use as a slug
RESERVED_KEYWORDS = [
    "account",
    "add_to_network",
    "cache",
    "configuration",
    "content",
    "comment",
    "create",
    "delete",
    "download",
    "id",
    "invitations",
    "join",
    "media",
    "media_resource",
    "menu_builder",
    "new",
    "resource",
    "remove_from_network",
    "search",
    "static",
    "twistranet",
    "twistable",
]

rsvd_kw = "$|".join(RESERVED_KEYWORDS)
SLUG_REGEX = r"(?!%s$)[a-zA-Z_][a-zA-Z0-9_\-\.]*" % rsvd_kw         # XXX TODO: The . must not be last character in the slug
FULL_SLUG_REGEX = "^%s$" % SLUG_REGEX

def slugify(value):
    """
    Transform a string value into a 50 characters slug
    """
    if not isinstance(value, unicode):
        # Double-check against invalid encodings
        value = unicode(value, errors = 'ignore')
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('\s+', '_', value))
    value = unicode(re.sub('[.@]', '_', value))
    value = unicode(re.sub('[^\w\s_-]', '', value).strip().lower())
    
    # If value starts with numbers, prefix it
    if re.match(r"[0-9]", value):
        value = u"_%s" % value
    
    # Double-check if we've slugified this correctly
    if not re.search(FULL_SLUG_REGEX, value):
        return slugify(u"%s0" % value)
    return value[:50]
    
