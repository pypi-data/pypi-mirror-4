
import opengraph
from jungleweb.page import Page


def fetch_and_extract(url):
    data = opengraph.OpenGraph(url=url)
    p = Page()
    p.title = data.get("title", None)
    p.description = data.get("description", None)
    p.canon_url = data.get("url", None)
    p.image_url = data.get("image", None)
    p.ogp_type = data.get("type", None)
    p.fetch_url = data.get("_url", None)
    p.site_name = data.get("site_name", None)
    return p
