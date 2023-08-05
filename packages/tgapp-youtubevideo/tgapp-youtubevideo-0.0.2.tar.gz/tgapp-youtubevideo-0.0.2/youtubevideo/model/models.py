import tg
import json, urllib2, contextlib

from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime, LargeBinary
from sqlalchemy.orm import backref, relation

from datetime import datetime, timedelta
from youtubevideo.model import DeclarativeBase
from tgext.pluggable import app_model, primary_key

class YouTubeCollection(DeclarativeBase):
    __tablename__ = 'youtubevideo_collection'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    user_name = Column(Unicode(128), index=True)
    category = Column(Unicode(128), index=True, nullable=True)
    last_update = Column(DateTime, nullable=True)

    json = Column(LargeBinary, nullable=False, default='')

    @classmethod
    def fetch_collection(cls, user_name=None, category=None):
        if not user_name:
            ytvideo_config = tg.config.get('_pluggable_youtubevideo_config')
            user_name = ytvideo_config['user']

        collection = app_model.DBSession.query(cls).filter_by(user_name=user_name)\
                                                   .filter_by(category=category).first()

        if not collection:
            collection = cls(user_name=user_name, category=category)
            app_model.DBSession.add(collection)
            app_model.DBSession.flush()

        return collection

    @property
    def feed_url(self):
        url = 'http://gdata.youtube.com/feeds/api/users/'
        if self.category:
            url += '%s/uploads/?category=%s&alt=json&v=2' % (self.user_name, self.category)
        else:
            url += '%s/uploads/?alt=json&v=2' % (self.user_name,)
        return url

    @property
    def entries(self):
        if not self.json:
            return []

        json_data = json.loads(self.json)
        entries = json_data['feed'].get('entry', [])
        return [{'id':entry['media$group']['yt$videoid']['$t'],
                 'title':entry['title']['$t'],
                 'player':entry['content']['src'],
                 'description':entry['media$group']['media$description']['$t'],
                 'thumbnail':entry['media$group']['media$thumbnail'][0]['url']} for entry in entries]

    @property
    def expire(self):
        ytvideo_config = tg.config.get('_pluggable_youtubevideo_config')
        if not self.last_update:
            return None
        return self.last_update+timedelta(seconds=ytvideo_config['refresh'])

    def update(self):
        now = datetime.now()
        if not self.last_update or self.expire < now:
            try:
                with contextlib.closing(urllib2.urlopen(self.feed_url)) as req:
                    answer = req.read()
                    json.loads(answer) #check json is well formed
                    self.json = answer
                self.last_update = datetime.now()
            except:
                pass