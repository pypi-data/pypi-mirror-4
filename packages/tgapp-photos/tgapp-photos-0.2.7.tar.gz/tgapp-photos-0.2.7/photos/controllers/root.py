# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import TGController
from tg import expose, flash, require, url, lurl, request, redirect, validate, abort, config
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.decorators import cached_property

from photos import model
from photos.model import DBSession, Gallery, Photo

from tgext.crud import EasyCrudRestController

try:
    from tg import predicates
except ImportError:
    from repoze.what import predicates

try:
    from tw2.forms import FileField
    from tw2.forms import FileValidator
    from tw2.core import Deferred
except ImportError:
    from tw.forms import FileField
    from tw.forms.validators import FieldStorageUploadConverter as FileValidator
    def Deferred(f):
        return f

from tgext.datahelpers.validators import SQLAEntityConverter
from tgext.pluggable import plug_url, primary_key, app_model
from webhelpers import html

def _get_current_user():
    return getattr(request.identity['user'], primary_key(app_model.User).key)

class PhotosController(EasyCrudRestController):
    allow_only = predicates.in_group('photos')
    title = "Manage Photos"
    model = model.Photo
    keep_params = ['gallery']
    remember_values = ['image']

    __form_options__ = {
        '__hide_fields__' : ['uid', 'author', 'gallery'],
        '__field_widget_types__' : {'image':FileField},
        '__field_validator_types__' : {'image':FileValidator},
        '__field_widget_args__' : {'author':{'default':_get_current_user,
                                             'value':Deferred(_get_current_user)}}
    }

    __table_options__ = {
        '__omit_fields__' : ['uid', 'author_id', 'gallery_id', 'gallery'],
        '__xml_fields__' : ['image'],
        'image': lambda filler,row: html.literal(row.image and '<img src="%s"/>' % row.image.thumb_url or '<span>no image</span>')
    }

    @property
    def mount_point(self):
        return plug_url('photos', '/manage/photos')

class GalleriesController(EasyCrudRestController):
    allow_only = predicates.in_group('photos')
    title = "Manage Galleries"
    model = model.Gallery

    __form_options__ = {
        '__hide_fields__' : ['uid'],
        '__omit_fields__' : ['photos']
    }

    @property
    def mount_point(self):
        return plug_url('photos', '/manage/galleries')

class ManagementController(TGController):
    @cached_property
    def galleries(self):
        return GalleriesController(DBSession.wrapped_session)

    @cached_property
    def photos(self):
        return PhotosController(DBSession.wrapped_session)

class RootController(TGController):
    manage = ManagementController()

    @expose('genshi:photos.templates.index')
    def index(self, *args, **kw):
        galleries = DBSession.query(Gallery).order_by(Gallery.uid.desc()).all()
        return dict(galleries=galleries)

    @expose('genshi:photos.templates.gallery')
    @validate(dict(gallery=SQLAEntityConverter(Gallery)), error_handler=index)
    def gallery(self, gallery):
        photos_config = config.get('_pluggable_photos_config')
        return dict(gallery=gallery, inline=photos_config.get('inline_photos', True))

    @expose('genshi:photos.templates.photo')
    @validate(dict(photo=SQLAEntityConverter(Photo)), error_handler=lambda c:abort(404))
    def photo(self, photo):
        return dict(photo=photo)
