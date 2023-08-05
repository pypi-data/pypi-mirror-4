from tg import expose

@expose('genshi:youtubevideo.templates.videogallery_partial')
def videogallery(collection):
        return dict(collection=collection, videos=collection.entries)
