# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import TGController
from tg import expose, flash, require, url, lurl, request, redirect, validate, config, abort
from tg.i18n import ugettext as _, lazy_ugettext as l_

from youtubevideo import model
from youtubevideo.model import DBSession
from tgext.datahelpers.validators import SQLAEntityConverter

class RootController(TGController):
    @expose('youtubevideo.templates.index')
    def index(self):
        collection = model.YouTubeCollection.fetch_collection()
        collection.update()
        return dict(collection=collection)

    @expose('youtubevideo.templates.video')
    @validate({'category':SQLAEntityConverter(model.YouTubeCollection)},
              error_handler=lambda *args:abort(404))
    def video(self, category, vid):
        entries = category.entries
        entry = [e for e in entries if e.get('id') == vid]
        if not entry:
            abort(404)
        return dict(entry=entry[0])
