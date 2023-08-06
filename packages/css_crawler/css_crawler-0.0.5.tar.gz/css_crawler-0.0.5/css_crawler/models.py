import datetime
import simplejson

from sqlalchemy import MetaData
from elixir import Entity, Field, Unicode, String, Text, DateTime, Integer
from elixir.events import before_update

import nagare.database

from css_crawler.lib import short_url

__metadata__ = MetaData()


class URLData(Entity):

    url = Field(Unicode(255), default=u'', unique=True, index=True,
                nullable=False)
    short_url = Field(String(255), default='', unique=True, index=True,
                      nullable=False)
    color_map = Field(Text)
    submission_date = Field(DateTime, default=datetime.datetime.now,
                            onupdate=datetime.datetime.now, nullable=False)
    viewed = Field(Integer, default=0, nullable=False)

    @before_update
    def update_short_url(self):
        self.short_url = short_url.encode_url(self.id)

    def is_cached(self, delay=60):
        return ((datetime.datetime.now() - self.submission_date) <=
                datetime.timedelta(0, delay))

    @classmethod
    def get_by_or_init(cls, **keywords):
        """
        Call get_by; if no object is returned, initialize an
        object with the same parameters.  If a new object was
        created, set any initial values.
        """

        result = cls.get_by(**keywords)
        if not result:
            result = cls(**keywords)
            nagare.database.session.add(result)
            nagare.database.session.flush()

            # Is this second session.add needed ?
            nagare.database.session.add(result)
        return result

    @property
    def palette(self):
        return simplejson.loads(self.color_map)

    @palette.setter
    def palette(self, value):
        self.color_map = simplejson.dumps(value)
