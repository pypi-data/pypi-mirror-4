
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Index,
    PrimaryKeyConstraint,
    String,
    DateTime,
    create_engine,
)
from sqlalchemy.exc import IntegrityError
from hashlib import sha1
from datetime import datetime
from jungleweb.page import Page


metadata = MetaData()


store_table = Table(
    "page",
    metadata,
    Column("id", String(40)),
    Column("public_suffix_id", String(40)),
    Column("title", String(1024)),
    Column("description", String(1024)),
    Column("url", String(1024)),
    Column("image_url", String(1024)),
    Column("ogp_type", String(25)),
    Column("site_name", String(1024)),
    Column("last_stored", DateTime),
    PrimaryKeyConstraint("id"),
    Index("public_suffix_id", "public_suffix_id"),
    Index("ogp_type", "ogp_type"),
    Index("last_stored", "last_stored"),
)


class PageStore(object):

    def __init__(self, dsn):
        self.engine = create_engine(dsn)

    def create_schema_in_db(self):
        metadata.create_all(self.engine)

    def store_page(self, page):
        page_id = sha1(page.url).hexdigest()
        public_suffix_id = sha1(page.url_public_suffix).hexdigest()
        values = {
            "id": page_id,
            "public_suffix_id": public_suffix_id,
            "title": page.title,
            "description": page.description,
            "url": page.url,
            "image_url": page.image_url,
            "ogp_type": page.ogp_type,
            "site_name": page.site_name,
            "last_stored": datetime.utcnow(),
        }
        try:
            stmt = store_table.insert().values(**values)
            self.engine.execute(stmt)
        except IntegrityError, ex:
            stmt = store_table.update().values(**values).where(
                store_table.c.id == page_id,
            )
            self.engine.execute(stmt)

    def _pages_from_db_result(self, result):
        for row in result:
            p = Page()
            p.canon_url = row["url"]
            p.title = row["title"]
            p.description = row["description"]
            p.image_url = row["image_url"]
            p.ogp_type = row["ogp_type"]
            p.site_name = row["site_name"]
            yield p

    def get_page_by_url(self, url):
        page_id = sha1(url).hexdigest()
        stmt = store_table.select().where(
            store_table.c.id == page_id,
        )
        result = self.engine.execute(stmt)
        return self._pages_from_db_result(result).next()


