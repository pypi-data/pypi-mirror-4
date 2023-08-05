from twistranet.compress.filters.jsmin.jsmin import jsmin
from twistranet.compress.filter_base import FilterBase

class JSMinFilter(FilterBase):
    def filter_js(self, js):
        return jsmin(js)