
from urlparse import urlparse
import publicsuffix


_psl = None


class Page(object):
    title = None
    description = None
    canon_url = None
    image_url = None
    ogp_type = None
    fetch_url = None
    site_name = None

    @property
    def url(self):
        if self.canon_url is not None:
            return self.canon_url
        else:
            return self.fetch_url

    @property
    def url_domain(self):
        parts = urlparse(self.url)
        return parts.hostname

    @property
    def url_public_suffix(self):
        global _psl
        if _psl is None:
            _psl = publicsuffix.PublicSuffixList()
        return _psl.get_public_suffix(self.url_domain)
