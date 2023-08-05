from photos.model import DBSession, Gallery
from tg import expose

@expose('genshi:photos.templates.gallery_partial')
def gallery(gallery=None, inline=True):
    if gallery is None:
        gallery = DBSession.query(Gallery).first()
    return dict(gallery=gallery, inline=inline)

@expose('genshi:photos.templates.albums_partial')
def albums(galleries=None):
    if galleries is None:
        galleries = DBSession.query(Gallery).order_by(Gallery.uid.desc()).all()
    return dict(galleries=galleries)
