import colander
from pyramid.i18n import TranslationStringFactory

from kotti import DBSession
from kotti.security import has_permission
from kotti.views.edit import ContentSchema
from kotti.views.edit import DocumentSchema
from kotti.views.form import AddFormView
from kotti.views.form import EditFormView
from kotti.views.util import template_api
from kotti.views.view import view_node

from kotti_site_gallery.resources import Site
from kotti_site_gallery.resources import SiteGallery

_ = TranslationStringFactory('kotti_site_gallery')


class SiteGallerySchema(ContentSchema):
    pass


class SiteGalleryAddForm(AddFormView):
    schema_factory = SiteGallerySchema
    add = SiteGallery
    item_type = _(u"Site gallery")


class SiteGalleryEditForm(EditFormView):
    schema_factory = SiteGallerySchema


class SiteSchema(DocumentSchema):

    url = colander.SchemaNode(colander.String(), title=_("URL"))


class SiteAddForm(AddFormView):
    schema_factory = SiteSchema
    add = Site

    item_type = _(u"Site")


class SiteEditForm(EditFormView):
    schema_factory = SiteSchema


def view_site_gallery(context, request):

    sites = DBSession.query(Site)\
        .filter(Site.parent_id == context.id)\
        .all()

    sites = [s for s in sites if has_permission('view', s, request)]

    return dict(
        api=template_api(context, request),
        sites=sites,
    )


def includeme_edit(config):

    config.add_view(
        SiteGalleryEditForm,
        context=SiteGallery,
        name='edit',
        permission='edit',
        renderer='kotti:templates/edit/node.pt',
    )

    config.add_view(
        SiteGalleryAddForm,
        name=SiteGallery.type_info.add_view,
        permission='add',
        renderer='kotti:templates/edit/node.pt',
    )

    config.add_view(
        SiteEditForm,
        context=Site,
        name='edit',
        permission='edit',
        renderer='kotti:templates/edit/node.pt',
    )

    config.add_view(
        SiteAddForm,
        name=Site.type_info.add_view,
        permission='add',
        renderer='kotti:templates/edit/node.pt',
    )


def includeme_view(config):

    config.add_view(
        view_site_gallery,
        context=SiteGallery,
        name='view',
        permission='view',
        renderer='templates/site-gallery-view.pt',
    )

    config.add_view(
        view_node,
        context=Site,
        name='view',
        permission='view',
        renderer='templates/site-view.pt',
    )


def includeme(config):

    config.add_translation_dirs('kotti_site_gallery:locale/')
    includeme_edit(config)
    includeme_view(config)
